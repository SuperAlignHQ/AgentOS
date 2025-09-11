# analyzer/llm.py
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import re
import time
from vertexai.generative_models import Part, Image, GenerativeModel
import vertexai
from utils.logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()

project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
if project and location:
    try:
        vertexai.init(project=project, location=location)
    except Exception:
        logger.exception("vertexai.init failed (maybe running locally without credentials).")

class DocumentLLM(BaseModel):
    """
    Wrapper around Vertex/Gemini model to pass images + prompt and return parsed + raw outputs.
    """

    def call_llm_api(self, prompt: str, image_path: list[str], retries: int = 2, backoff: float = 1.0) -> dict:
        """
        Calls the generative model with images + prompt.
        Returns: { "parsed":(<json|None>), "raw": <raw_text or None>, "error": <error_str|None> }
        """
        try:
            model = GenerativeModel(model_name="gemini-2.0-flash-001")
        except Exception as e:
            # if model creation fails, raise up (caller will fallback)
            logger.exception("Failed to create GenerativeModel: %s", e)
            raise

        text_part = Part.from_text(prompt)
        image_parts = []
        for p in image_path:
            try:
                image_parts.append(Part.from_image(Image.load_from_file(p)))
            except Exception:
                logger.exception("Failed loading image for LLM: %s", p)
                # still proceed (model may accept less images)
        last_exc = None
        for attempt in range(retries + 1):
            try:
                response = model.generate_content([*image_parts, text_part])
                raw_text = response.text
                # First try direct JSON parse
                try:
                    parsed = json.loads(raw_text)
                    return {"parsed": parsed, "raw": raw_text, "error": None}
                except Exception:
                    # strip fenced code blocks and try again
                    cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text, flags=re.MULTILINE)
                    parsed = json.loads(cleaned)
                    return {"parsed": parsed, "raw": raw_text, "error": None}
            except Exception as e:
                last_exc = e
                logger.warning("LLM call failed (attempt %d/%d): %s", attempt + 1, retries + 1, str(e))
                time.sleep(backoff * (2 ** attempt))
        logger.exception("LLM all retries failed: %s", last_exc)
        return {"parsed": None, "raw": None, "error": str(last_exc)}
