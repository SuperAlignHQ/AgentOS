import os
import json
import shutil
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from utils.process_file import save_upload_to_temp, process_file, DEFAULT_MAX_UPLOAD_BYTES, DEFAULT_MAX_PDF_PAGES
from analyzer.analyze import analyze_document
from difflib import get_close_matches
import pandas as pd
from utils.logger import setup_logger
import vertexai
from vertexai.generative_models import Part, Image, GenerativeModel


logger = setup_logger(__name__)


project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
if project and location:
    try:
        vertexai.init(project=project, location=location)
    except Exception:
        logger.exception("vertexai.init failed (maybe running locally without credentials).")

app = FastAPI()

# Configurable limits
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", DEFAULT_MAX_UPLOAD_BYTES))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", DEFAULT_MAX_PDF_PAGES))
FUZZY_MATCHING = os.getenv("FUZZY_MATCHING", "true").lower() in ("1", "true", "yes")

# Policy Excel path
POLICY_FILE_PATH = r"C:\Users\Manas Pati Tripathi\Downloads\policy_new.xlsx" 

# Vertex Gemini
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")


# --- Helper functions ---

def _norm(s: Optional[str]) -> str:
    if not s:
        return "unknown"
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")

def _matches_required(req_cat: str, req_typ: str, doc_cat: str, doc_typ: str) -> bool:
    req_c, req_t = _norm(req_cat), _norm(req_typ)
    doc_c, doc_t = _norm(doc_cat), _norm(doc_typ)

    # Category match: exact or fuzzy/substring
    category_match = (
        req_c == doc_c or
        (FUZZY_MATCHING and (req_c in doc_c or doc_c in req_c or get_close_matches(req_c, [doc_c], cutoff=0.8)))
    )

    # Type match: exact or fuzzy/substring/close match
    type_match = (
        req_t == doc_t or
        (FUZZY_MATCHING and (
            req_t in doc_t or
            doc_t in req_t or
            get_close_matches(req_t, [doc_t], cutoff=0.8)
        ))
    )

    return category_match and type_match


def coerce_category_type_pair(cat: str, typ: str) -> tuple[str, str]:
    c = _norm(cat)
    t = _norm(typ)
    
    return c, t


def fetch_policies(document_type: str, policy_df):
    print("fetching_policies")
    relevant = policy_df[policy_df.iloc[:, 0].astype(str).str.strip().str.lower().str.contains(document_type.strip().lower())]
    print(relevant)
    policies = []
    for _, row in relevant.iterrows():
        name = str(row.iloc[1]).strip()
        rule = str(row.iloc[3]).strip()
        if name and rule:
            policies.append({"name": name, "rule": rule})
    return policies

async def validate_policy_from_images(document_images: list, policy_pair: dict):
    if not document_images or not policy_pair:
        return "No"
    try:
        model = GenerativeModel(model_name=LLM_MODEL)
        response = model.generate_content(
            [
                f"Given the following document images/content, determine if the policy named "
                f"'{policy_pair['name']}' with rule '{policy_pair['rule']}' is present and adhered to. "
                f"Respond only with 'Yes' or 'No'.",
                *document_images
            ],
           
        )
        result = response.text.strip().lower()
        return "Yes" if result == "yes" else "No"
    except Exception as e:
        logger.exception(f"Policy validation error for {policy_pair['name']}: {e}")
        return "Error"

# --- FastAPI endpoint ---

@app.post("/analyze")
async def analyze(
    payload: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        data = json.loads(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"payload must be valid JSON: {e}")

    if "Application_id" not in data or "Application_type" not in data:
        raise HTTPException(status_code=400, detail="payload must include Application_id and Application_type")

    total_list = data.get("total_list_of_documents", [])
    required_list = data.get("required_documents", [])

    # Prepare allowed_pairs and allowed_doc_types
    allowed_pairs = []
    allowed_doc_types = []
    for p in total_list:
        cat = p.get("document_category") or p.get("category")
        typ = p.get("document_type") or p.get("type")
        if cat is None or typ is None:
            continue
        c, t = coerce_category_type_pair(cat, typ)
        allowed_pairs.append({"document_category": c, "document_type": t})
        allowed_doc_types.append(t)

    classified_docs = []

    # Load policy Excel
    try:
        policy_df = pd.read_excel(POLICY_FILE_PATH)
        print(policy_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy file loading error: {e}")

    # Process each uploaded file
    for file in files:
        fname = file.filename or "uploaded_file"
        saved_path = None
        file_results_obj = None

        try:
            saved_path = await asyncio.to_thread(save_upload_to_temp, file, None, MAX_UPLOAD_BYTES)
            file_results_obj = await asyncio.to_thread(process_file, None, saved_path, MAX_PDF_PAGES)
            if not file_results_obj or not file_results_obj.properties.file_present or not file_results_obj.properties.page_paths:
                raise HTTPException(status_code=400, detail=f"File {fname} empty or contains no pages")

            analyzed = await asyncio.to_thread(analyze_document, file_results_obj, allowed_pairs)
            cat = getattr(analyzed.document_category_details, "document_category", "unknown")
            typ = getattr(analyzed.document_category_details, "document_type", "unknown")
            status = getattr(analyzed.document_category_details, "status", "classified")
            note = getattr(analyzed.document_category_details, "note", None)
            cat, typ = coerce_category_type_pair(cat, typ)

            # Identify document type via LLM
            document_images = getattr(file_results_obj.properties, "page_paths", [])
            #doc_type_llm = await identify_document_type_from_images(document_images, allowed_doc_types)
            #final_doc_type =  typ

            # Only validate policies if document type matches a required document type
            matched_required = any(
                _matches_required(r.get("document_category"), r.get("document_type"), cat, typ)
                for r in required_list
            )


            validation_results = []
            if matched_required:
                print(typ)
                policies = fetch_policies(typ, policy_df)
                for policy in policies:
                    print(policy)
                    result = await validate_policy_from_images(document_images, policy)
                    validation_results.append({
                        "doc_type": typ,
                        "policy_name": policy["name"],
                        "validation_result": result,
                        "comment": ""
                    })

            classified_docs.append({
                "filename": fname,
                "file_path": saved_path,
                "status": status,
                "document_category": cat,
                "document_type": typ,
                "note": note,
                "policy_validation_results": validation_results
            })

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error processing file {fname}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Cleanup
            try:
                if file_results_obj and file_results_obj.properties and getattr(file_results_obj.properties, "file_dir", None):
                    shutil.rmtree(file_results_obj.properties.file_dir, ignore_errors=True)
                elif saved_path:
                    parent = os.path.dirname(saved_path)
                    if parent and "tmp" in parent:
                        shutil.rmtree(parent, ignore_errors=True)
            except Exception:
                logger.exception(f"Cleanup failed for file {fname}")

    # Compute required document presence
    classification_results = []
    overall_ok = True

    def _is_present(req_cat: str, req_typ: str):
        req_c, req_t = coerce_category_type_pair(req_cat, req_typ)
        for d in classified_docs:
            if d.get("status") in (None, "classified", "classified_extra", "classified_cached"):
                doc_c = d.get("document_category")
                doc_t = d.get("document_type")

                # Strict match
                if doc_c == req_c and doc_t == req_t:
                    return True, d.get("filename")

                # Fuzzy/partial match if enabled
                if FUZZY_MATCHING:
                    
                    # 1. Substring match
                    if req_t in doc_t or doc_t in req_t:
                        return True, d.get("filename")

                    # 2. Close match
                    from difflib import get_close_matches
                    if get_close_matches(req_t, [doc_t], cutoff=0.8):
                        return True, d.get("filename")
        return False, None


    for r in required_list:
        req_cat = r.get("document_category")
        req_typ = r.get("document_type")
        is_opt = bool(r.get("is_optional", False))
        present, matched_filename = _is_present(req_cat, req_typ)
        if not present and not is_opt:
            overall_ok = False
        classification_results.append({
            "document_category": req_cat,
            "document_type": req_typ,
            "optional": is_opt,
            "result": present,
            "reason": f"{req_typ} is {'present' if present else 'missing'}",
            "matched_filename": matched_filename
        })

    return JSONResponse({
        "Application_id": data.get("Application_id"),
        "Application_type": data.get("Application_type"),
        "classification_overall_result": overall_ok,
        "classification_results": classification_results,
        "files": classified_docs
    }, status_code=200)
