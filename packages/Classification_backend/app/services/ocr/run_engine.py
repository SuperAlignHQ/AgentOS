import os
import json
import uuid
import shutil
import hashlib
import asyncio
import time
import tempfile
from typing import List, Optional
from uuid import UUID as UUIDType

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from utils.process_file import save_upload_to_temp, process_file, DEFAULT_MAX_UPLOAD_BYTES, DEFAULT_MAX_PDF_PAGES
from analyzer.analyze import analyze_document
from schema_base import FileResults
from documents.document_type.schema import DocumentCategoryAndType
from utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI()

# Configurable limits
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", DEFAULT_MAX_UPLOAD_BYTES))
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", DEFAULT_MAX_PDF_PAGES))
FUZZY_MATCHING = os.getenv("FUZZY_MATCHING", "true").lower() in ("1", "true", "yes")

# In-memory cache (sha256 -> classification dict)
_FILE_CACHE: dict[str, dict] = {}


def _sha256_of_file(path: str, chunk: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""):
            h.update(c)
    return h.hexdigest()


def _norm(s: Optional[str]) -> str:
    if not s:
        return "unknown"
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")


def coerce_category_type_pair(cat: str, typ: str) -> tuple[str, str]:
    """
    Normalize strings and coerce bank_statement -> bank_statement category if type indicates bank.
    """
    c = _norm(cat)
    t = _norm(typ)
    # some heuristics
    if "bank" in t:
        c = "bank_statement"
    if c in ("id_proof", "id", "identity"):
        c = "identity_verification_document"
    if c == "income":
        c = "income_document"
    return c, t


@app.post("/analyze")
async def analyze(
    payload: str = Form(...),            # JSON string with Application_id, Application_type, total_list_of_documents, required_documents
    file: UploadFile = File(...)        # single file per request (can be extended to List[UploadFile])
):
    """
    New /analyze endpoint:
    - payload: JSON string with keys:
        - Application_id
        - Application_type
        - total_list_of_documents: [{document_category, document_type}, ...]
        - required_documents: [{document_category, document_type, is_optional}, ...]
    - file: uploaded file (single)
    Returns:
      {
        Application_id,
        Application_type,
        classification_overall_result,
        classification_results: [ {document_category, document_type, optional, result, reason, matched_filename?}, ... ]
      }
    """
    # parse payload JSON
    try:
        data = json.loads(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"payload must be valid JSON: {e}")

    # validate minimal fields
    if "Application_id" not in data or "Application_type" not in data:
        raise HTTPException(status_code=400, detail="payload must include Application_id and Application_type")

    total_list = data.get("total_list_of_documents", [])
    required_list = data.get("required_documents", [])

    # prepare allowed_pairs for analyzer
    allowed_pairs = []
    for p in total_list:
        # tolerate various key names
        cat = p.get("document_category") or p.get("category")
        typ = p.get("document_type") or p.get("type")
        if cat is None or typ is None:
            continue
        c, t = coerce_category_type_pair(cat, typ)
        allowed_pairs.append({"document_category": c, "document_type": t})

    # process uploaded file (save and run OCR + LLM)
    fname = file.filename or "uploaded_file"
    saved_path = None
    file_results_obj = None
    sha = None

    try:
        # save upload to temp (streamed)
        saved_path = await asyncio.to_thread(save_upload_to_temp, file, None, MAX_UPLOAD_BYTES)
        sha = _sha256_of_file(saved_path)

        # try cache
        if sha in _FILE_CACHE:
            logger.info("Cache hit for file %s", fname)
            cached = _FILE_CACHE[sha]
            classified_docs = [{
                "filename": fname,
                "file_path": saved_path,
                "status": cached.get("status", "classified"),
                "document_category": cached["document_category"],
                "document_type": cached["document_type"],
                "note": cached.get("note")
            }]
        else:
            # process file -> produces FileResults with properties.page_paths etc.
            file_results_obj = await asyncio.to_thread(process_file, None, saved_path, MAX_PDF_PAGES)
            if not file_results_obj or not file_results_obj.properties.file_present or not file_results_obj.properties.page_paths:
                raise HTTPException(status_code=400, detail="file not present or contains no pages")

            # analyze_document will attach document_category/document_type and status/note inside file_results_obj
            analyzed = await asyncio.to_thread(analyze_document, file_results_obj, allowed_pairs)

            if not analyzed:
                raise HTTPException(status_code=500, detail="analysis failed")

            # read values (fall back to ocr_results if needed)
            cat = getattr(analyzed.document_category_details, "document_category", "unknown")
            typ = getattr(analyzed.document_category_details, "document_type", "unknown")
            # try to get status/note; else check ocr_results
            status = getattr(analyzed.document_category_details, "status", None)
            note = getattr(analyzed.document_category_details, "note", None)
            if not status:
                ocr = getattr(analyzed, "ocr_results", {}) or {}
                status = ocr.get("status", "classified" if cat != "unknown" else "unknown")
                note = note or ocr.get("note")

            # normalize
            cat, typ = coerce_category_type_pair(cat, typ)

            classified_docs = [{
                "filename": fname,
                "file_path": saved_path,
                "status": status if status else "classified",
                "document_category": cat,
                "document_type": typ,
                "note": note
            }]

            # cache summary
            _FILE_CACHE[sha] = {
                "document_category": cat,
                "document_type": typ,
                "status": status,
                "note": note,
                "timestamp": time.time()
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing uploaded file %s: %s", fname, e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # cleanup process_file temp directories if present
        try:
            if file_results_obj and file_results_obj.properties and getattr(file_results_obj.properties, "file_dir", None):
                shutil.rmtree(file_results_obj.properties.file_dir, ignore_errors=True)
            else:
                # if saved_path lives in a tmp dir created by save_upload_to_temp, try to remove parent
                if saved_path:
                    parent = os.path.dirname(saved_path)
                    if parent and "tmp" in parent:
                        shutil.rmtree(parent, ignore_errors=True)
        except Exception:
            logger.exception("Cleanup failed for file %s", fname)

    # Now compute results for each required document (strict both category & type)
    classification_results = []
    overall_ok = True

    # helper to check presence in classified_docs
    def _is_present(req_cat: str, req_typ: str) -> (bool, Optional[str]):
        req_c, req_t = coerce_category_type_pair(req_cat, req_typ)
        for d in classified_docs:
            # only consider classified and classified_extra and cached classified
            if d.get("status") not in (None, "classified", "classified_extra", "cache", "classified_cached"):
                # still allow matching if status unknown? we stick to classified/classified_extra/cache
                pass
            if d.get("document_category") == req_c and d.get("document_type") == req_t:
                return True, d.get("filename")
        return False, None

    for r in required_list:
        req_cat = r.get("document_category")
        req_typ = r.get("document_type")
        is_opt = bool(r.get("is_optional", False))

        present, matched_filename = _is_present(req_cat, req_typ)
        if not present and not is_opt:
            overall_ok = False

        reason = f"{req_typ} is present" if present else f"{req_typ} is missing"

        entry = {
            "document_category": req_cat,
            "document_type": req_typ,
            "optional": is_opt,
            "result": present,
            "reason": reason
        }
        if present and matched_filename:
            entry["matched_filename"] = matched_filename

        classification_results.append(entry)

    return JSONResponse({
        "Application_id": data.get("Application_id"),
        "Application_type": data.get("Application_type"),
        "classification_overall_result": overall_ok,
        "classification_results": classification_results
    }, status_code=200)
