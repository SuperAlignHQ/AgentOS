# analyzer/analyze.py

from schema_base import FileResults
from utils.logger import setup_logger
from analyzer.llm import DocumentLLM
from documents.document_type.prompt import document_type_prompt
from documents.document_type.schema import DocumentCategoryAndType
from typing import Optional, List, Tuple
import difflib

logger = setup_logger(__name__)


def _normalize_value(s: str, allowed: Optional[List[str]] = None) -> str:
    """
    Normalize a string to lowercase with underscores and optionally fuzzy match
    against a provided allowed list.
    """
    base = str(s or "unknown").strip().lower().replace(" ", "_").replace("-", "_")
    if allowed:
        match = difflib.get_close_matches(base, allowed, n=1, cutoff=0.8)
        if match:
            return match[0]
    return base


def _normalize_pair(
    cat: str, typ: str,
    allowed_cats: Optional[List[str]] = None,
    allowed_types: Optional[List[str]] = None
) -> Tuple[str, str]:
    return (
        _normalize_value(cat, allowed_cats),
        _normalize_value(typ, allowed_types)
    )


def analyze_document(
    file_results: FileResults,
    allowed_pairs: Optional[List[dict]] = None,
    stop_on_failure: bool = False
) -> Optional[FileResults]:
    """
    Runs classification on the provided file_results (uses page images).
    Returns updated FileResults with normalized category/type and status.
    """
    if not file_results or not file_results.properties or not file_results.properties.page_paths:
        logger.debug("No file_results or no page_paths present")
        return None

    # Normalize allowed_pairs set and track normalized values for fuzzy matching
    allowed_pairs_set = set()
    allowed_cats = []
    allowed_types = []
    if allowed_pairs:
        for p in allowed_pairs:
            try:
                c = p.get("document_category")
                t = p.get("document_type")
            except Exception:
                continue
            cat_n = _normalize_value(c)
            typ_n = _normalize_value(t)
            allowed_pairs_set.add((cat_n, typ_n))
            allowed_cats.append(cat_n)
            allowed_types.append(typ_n)

    document_llm = DocumentLLM()
    logger.info("Analyzing pages: %s", file_results.properties.page_paths)

    response = document_llm.call_llm_api(
        prompt=document_type_prompt,
        image_path=file_results.properties.page_paths
    )
    parsed = response.get("parsed")
    raw = response.get("raw")
    error = response.get("error")

    # default fallback
    file_results.document_category_details.document_category = "unknown"
    file_results.document_category_details.document_type = "unknown"
    try:
        file_results.document_category_details.status = "unknown"
        file_results.document_category_details.note = None
    except Exception:
        pass

    if parsed:
        try:
            # Validate/coerce with Pydantic model
            doc_cat_type = DocumentCategoryAndType.model_validate(parsed)
            cat_raw = str(doc_cat_type.document_category)
            typ_raw = str(doc_cat_type.document_type)

            # Normalize with fuzzy matching
            cat_n, typ_n = _normalize_pair(cat_raw, typ_raw, allowed_cats, allowed_types)

            # Determine status relative to allowed_pairs
            if allowed_pairs_set and (cat_n, typ_n) not in allowed_pairs_set:
                status = "extra"
                note = "Pair not in allowed list (user-provided)"
            else:
                status = "classified"
                note = None

            # Write back
            file_results.document_category_details.document_category = cat_n
            file_results.document_category_details.document_type = typ_n
            try:
                file_results.document_category_details.status = status
                file_results.document_category_details.note = note
            except Exception:
                pass

            # Store raw LLM + parsed outputs
            file_results.ocr_results = {
                "llm_raw": raw,
                "llm_parsed": parsed,
                "status": status,
                "note": note
            }

            logger.info("Classification result: %s, %s -> %s", cat_raw, typ_raw, status)
            return file_results

        except Exception as e:
            logger.exception("Failed to validate LLM parsed output: %s", e)
            file_results.document_category_details.document_category = "unknown"
            file_results.document_category_details.document_type = "unknown"
            file_results.document_category_details.status = "unknown"
            file_results.document_category_details.note = "validation_failed"
            file_results.ocr_results = {"llm_raw": raw, "error": "validation_failed"}
            if stop_on_failure:
                return None
            return file_results

    else:
        logger.warning("LLM returned no parsed JSON (error=%s)", error)
        file_results.document_category_details.document_category = "unknown"
        file_results.document_category_details.document_type = "unknown"
        file_results.document_category_details.status = "unknown"
        file_results.document_category_details.note = error or "no_parsed_response"
        file_results.ocr_results = {"error": error}
        if stop_on_failure:
            return None
        return file_results
