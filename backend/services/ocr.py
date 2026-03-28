from __future__ import annotations

import mimetypes
import importlib
import os
import warnings
from typing import Any

from core.config import get_settings


class OCRError(RuntimeError):
    """Raised when OCR extraction fails in a user-actionable way."""


DEFAULT_OCR_MODEL = "gemini-2.5-flash"
OCR_PROMPT = """
Extract all readable text from this image.

Rules:
- Return only the extracted text.
- Preserve paragraph and line breaks when they help keep the original meaning.
- Do not summarize, explain, or correct the text.
- If the image contains no readable text, return an empty string.
""".strip()


def extract_text(image_bytes: bytes, filename: str) -> str:
    if not image_bytes:
        return ""

    settings = get_settings()
    api_key = settings.gemini_api_key.strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    mime_type = _guess_mime_type(filename)
    model_name = os.getenv("GEMINI_OCR_MODEL", DEFAULT_OCR_MODEL)

    try:
        return _extract_with_google_genai(
            image_bytes=image_bytes,
            mime_type=mime_type,
            api_key=api_key,
            model_name=model_name,
        )
    except ImportError:
        try:
            return _extract_with_deprecated_sdk(
                image_bytes=image_bytes,
                mime_type=mime_type,
                api_key=api_key,
                model_name=model_name,
            )
        except ImportError as exc:
            raise OCRError(
                "No Gemini Python SDK is installed. Install dependencies with "
                "`python -m pip install -r requirements.txt`."
            ) from exc
        except Exception as exc:
            raise OCRError(f"Gemini OCR request failed: {exc}") from exc
    except Exception as exc:
        raise OCRError(f"Gemini OCR request failed: {exc}") from exc


def _guess_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "image/png"


def _extract_with_google_genai(
    *,
    image_bytes: bytes,
    mime_type: str,
    api_key: str,
    model_name: str,
) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    response = client.models.generate_content(
        model=model_name,
        contents=[OCR_PROMPT, image_part],
        config=types.GenerateContentConfig(temperature=0),
    )

    return _extract_response_text(response)


def _extract_with_deprecated_sdk(
    *,
    image_bytes: bytes,
    mime_type: str,
    api_key: str,
    model_name: str,
) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        genai = importlib.import_module("google.generativeai")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name)
    response = model.generate_content(
        [
            OCR_PROMPT,
            {
                "mime_type": mime_type,
                "data": image_bytes,
            },
        ],
        generation_config={"temperature": 0},
    )

    return _extract_response_text(response)


def _extract_response_text(response: Any) -> str:
    direct_text = getattr(response, "text", None)
    if isinstance(direct_text, str):
        return direct_text.strip()

    candidates = getattr(response, "candidates", None) or []
    text_fragments: list[str] = []

    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            text = getattr(part, "text", None)
            if text:
                text_fragments.append(text)

    return "\n".join(fragment.strip() for fragment in text_fragments if fragment.strip()).strip()
