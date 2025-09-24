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
import re
from utils.field_prompts import get_prompt_for_type
logger = setup_logger(__name__)

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
if project and location:
    try:
        vertexai.init(project=project, location=location)
    except Exception:
        logger.exception("vertexai.init failed (maybe running locally without credentials).")

app = FastAPI()

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", DEFAULT_MAX_UPLOAD_BYTES))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", DEFAULT_MAX_PDF_PAGES))
FUZZY_MATCHING = os.getenv("FUZZY_MATCHING", "true").lower() in ("1", "true", "yes")
POLICY_FILE_PATH = r'utils/policy_new.xlsx'
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-001")


# ----------------- Helpers -----------------

def _norm(s: Optional[str]) -> str:
    if not s:
        return "unknown"
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")

def _matches_required(req_cat: str, req_typ: str, doc_cat: str, doc_typ: str) -> bool:
    req_c, req_t = _norm(req_cat), _norm(req_typ)
    doc_c, doc_t = _norm(doc_cat), _norm(doc_typ)

    category_match = (
        req_c == doc_c or
        (FUZZY_MATCHING and (req_c in doc_c or doc_c in req_c or get_close_matches(req_c, [doc_c], cutoff=0.8)))
    )
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
    return _norm(cat), _norm(typ)

def fetch_policies(document_type: str, policy_df: pd.DataFrame) -> list[dict]:
    relevant = policy_df[policy_df.iloc[:, 0]
                         .astype(str).str.strip().str.lower()
                         .str.contains(document_type.strip().lower())]
    policies = []
    for _, row in relevant.iterrows():
        name = str(row.iloc[1]).strip()
        rule = str(row.iloc[3]).strip()
        if name and rule:
            policies.append({"name": name, "rule": rule})
    return policies


async def get_evaluated_fields(document_images:list,prompt:str)->dict:
        
        model = GenerativeModel(model_name=LLM_MODEL)
        text_part = Part.from_text(prompt)
        image_parts = []
        for p in document_images:
            try:
                image_parts.append(Part.from_image(Image.load_from_file(p)))
            except Exception:
                logger.exception("Failed loading image for LLM: %s", p)
        response = model.generate_content([*image_parts, text_part],generation_config={"temperature":0.0})
        raw = response.text.strip()
        
                # --- 1️⃣  Remove markdown code fences like ```json ... ```  ---
        # Matches optional language tag after opening ```
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
        raw = re.sub(r'```$', '', raw)

        # --- 2️⃣  Collapse any *real* newlines inside quoted strings ---
        raw = re.sub(r'(".*?)(\n+)(.*?")',
                    lambda m: m.group(1) + " " + m.group(3),
                    raw,
                    flags=re.DOTALL)
        #print(raw)
        try:
            parsed = json.loads(raw)
            return parsed
        except:
             return {}
        
async def validate_policies_from_images(document_images: list, policies: list[dict],all_types:list) -> list:
    
    """
    Validate all policies together. 
    Returns dict: {policy_name: 'Yes'/'No'/'Error'}
    """
    if not document_images or not policies:
        return {}

    # Build a single instruction string with all policies
    policy_descriptions = "\n".join(
        [f"- {p['name']}: {p['rule']}" for p in policies]
    )

    prompt = (
    f"You are given document images of following documents:{all_types}, and a list of policies. Examine the content of the images carefully, understand them, do not fabricate your own details,stick to what is written in the images. then Do check across all the document images, cross checking other document images also for some policies where need be.\n"
    "For each policy, return an object with keys result (Pass or Fail) and comment (short explanation). Return only a valid JSON object mapping policy names to these objects—no markdown, no back-ticks.\n"
    "Return **only** a valid JSON object — no markdown fences, no extra text, "
    "no quotes around the word JSON. Your response must start with '{' and end with '}'.\n\n"
    f"Policies:\n{policy_descriptions}"
)

    #print(prompt)
    try:
        model = GenerativeModel(model_name=LLM_MODEL)
        text_part = Part.from_text(prompt)
        image_parts = []
        for p in document_images:
            try:
                image_parts.append(Part.from_image(Image.load_from_file(p)))
            except Exception:
                logger.exception("Failed loading image for LLM: %s", p)
        response = model.generate_content([*image_parts, text_part],generation_config={"temperature":0.0})
        raw = response.text.strip()
                # --- 1️⃣  Remove markdown code fences like ```json ... ```  ---
        # Matches optional language tag after opening ```
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
        raw = re.sub(r'```$', '', raw)

        # --- 2️⃣  Collapse any *real* newlines inside quoted strings ---
        raw = re.sub(r'(".*?)(\n+)(.*?")',
                    lambda m: m.group(1) + " " + m.group(3),
                    raw,
                    flags=re.DOTALL)
        #print(raw)
        try:
            parsed = json.loads(raw)
            # Ensure all policy names are present
            results = []

            for p in policies:
                policy_name = p["name"]
                entry = parsed.get(policy_name, {})
                results.append({
                    "policy_name": policy_name,
                    "validation_result": "Pass" if str(entry.get("result", "")).strip().lower() == "pass" else "Fail",
                    "comment": entry.get("comment", "")
                })
            return results
        except Exception:
            logger.warning("Model output not valid JSON; falling back to No for all")
            return ["Error"]
    except Exception as e:
        logger.exception(f"Policy batch validation error: {e}")
        return ["Error"]


# ----------------- FastAPI endpoint -----------------

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

    allowed_pairs, allowed_doc_types = [], []
    for p in total_list:
        cat = p.get("document_category") or p.get("category")
        typ = p.get("document_type") or p.get("type")
        if cat and typ:
            c, t = coerce_category_type_pair(cat, typ)
            allowed_pairs.append({"document_category": c, "document_type": t})
            allowed_doc_types.append(t)

    classified_docs = []

    # Load policies
    try:
        policy_df = pd.read_excel(POLICY_FILE_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy file loading error: {e}")
    all_document_images=[]
    all_types=[]
    for file in files:
        fname = file.filename or "uploaded_file"
        saved_path = None
        file_results_obj = None
        try:
            saved_path = await asyncio.to_thread(save_upload_to_temp, file, None, MAX_UPLOAD_BYTES)
            file_results_obj = await asyncio.to_thread(process_file, None, saved_path, MAX_PDF_PAGES)
            if not file_results_obj or not file_results_obj.properties.file_present or not file_results_obj.properties.page_paths:
                raise HTTPException(status_code=400, detail=f"File {fname} empty or contains no pages")

            analyzed = await asyncio.to_thread(analyze_document, file_results_obj,allowed_pairs)
            cat = getattr(analyzed.document_category_details, "document_category", "unknown")
            typ = getattr(analyzed.document_category_details, "document_type", "unknown")
            field_prompt=get_prompt_for_type(typ)
            
            all_types.append(typ)
            status = getattr(analyzed.document_category_details, "status", "classified")
            note = getattr(analyzed.document_category_details, "note", None)
            cat, typ = coerce_category_type_pair(cat, typ)
            print("category from llm after validation and coercing is",cat)
            print("type from llm after validation and coercing is",typ)
            document_images=getattr(file_results_obj.properties, "page_paths", [])
            evaluated_fields=await get_evaluated_fields(document_images,field_prompt)
            all_document_images.extend(document_images)
            #print("length of images list after new doc added is ",len(document_images))
            matched_required = any(
                _matches_required(r.get("document_category"), r.get("document_type"), cat, typ)
                for r in required_list
            )

            batch_results=[]
            overall_policy_check="Pass"
            if matched_required:
                policies = fetch_policies(typ, policy_df)
                if policies:
                    batch_results = await validate_policies_from_images(all_document_images, policies,all_types)
                    for policy_dict in batch_results:
                        if policy_dict.get("validation_result")=="Fail":
                           overall_policy_check="Fail"
                           
                    

            classified_docs.append({
                "filename": fname,
                "file_path": saved_path,
                "status": status,
                "document_category": cat,
                "document_type": typ,
                "note": note,
                "evaluations":evaluated_fields,
                "policy_validation_results": batch_results ,
                "final_policy_validation_result":overall_policy_check
            })

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error processing file {fname}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            try:
                if file_results_obj and getattr(file_results_obj.properties, "file_dir", None):
                    shutil.rmtree(file_results_obj.properties.file_dir, ignore_errors=True)
                elif saved_path:
                    parent = os.path.dirname(saved_path)
                    if parent and "tmp" in parent:
                        shutil.rmtree(parent, ignore_errors=True)
            except Exception:
                logger.exception(f"Cleanup failed for file {fname}")

    # Check required documents
    classification_results = []
    overall_ok = True

    def _is_present(req_cat: str, req_typ: str):
        req_c, req_t = coerce_category_type_pair(req_cat, req_typ)
        for d in classified_docs:
            if d.get("status") in (None, "classified", "classified_extra", "classified_cached"):
                doc_c = d.get("document_category")
                doc_t = d.get("document_type")
                if doc_c == req_c and doc_t == req_t:
                    return True, d.get("filename")
                if FUZZY_MATCHING:
                    if req_t in doc_t or doc_t in req_t:
                        return True, d.get("filename")
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
