from __future__ import annotations

import importlib
import os
import warnings
from typing import Any

from core.config import get_settings
from services.media import MediaError, prepare_transcription_media


DEFAULT_TRANSCRIBER_MODEL = "gemini-2.5-flash"
TRANSCRIBE_PROMPT = """
Transcribe this audio exactly.

Rules:
- Return only the transcript text.
- Preserve speaker changes when they are obvious.
- Preserve line breaks when they improve readability.
- Do not summarize or explain.
- If there is no intelligible speech, return an empty string.
""".strip()


class TranscriptionError(RuntimeError):
    """Raised when audio or video transcription fails in a user-actionable way."""


def transcribe_media(
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None,
) -> str:
    if not file_bytes:
        return ""

    api_key = get_settings().gemini_api_key.strip()
    if not api_key:
        raise TranscriptionError("GEMINI_API_KEY is not set.")

    try:
        audio_bytes, audio_filename, audio_mime_type, _source_type = prepare_transcription_media(
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type,
        )
    except MediaError as exc:
        raise TranscriptionError(str(exc)) from exc

    model_name = os.getenv("GEMINI_TRANSCRIBER_MODEL", DEFAULT_TRANSCRIBER_MODEL)

    try:
        return _transcribe_with_google_genai(
            audio_bytes=audio_bytes,
            audio_filename=audio_filename,
            audio_mime_type=audio_mime_type,
            api_key=api_key,
            model_name=model_name,
        )
    except ImportError:
        try:
            return _transcribe_with_deprecated_sdk(
                audio_bytes=audio_bytes,
                audio_mime_type=audio_mime_type,
                api_key=api_key,
                model_name=model_name,
            )
        except ImportError as exc:
            raise TranscriptionError(
                "No Gemini Python SDK is installed. Install dependencies with "
                "`python -m pip install -r requirements.txt`."
            ) from exc
        except Exception as exc:
            raise TranscriptionError(f"Gemini transcription failed: {exc}") from exc
    except Exception as exc:
        raise TranscriptionError(f"Gemini transcription failed: {exc}") from exc


def _transcribe_with_google_genai(
    *,
    audio_bytes: bytes,
    audio_filename: str,
    audio_mime_type: str,
    api_key: str,
    model_name: str,
) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=audio_mime_type)
    response = client.models.generate_content(
        model=model_name,
        contents=[
            f"{TRANSCRIBE_PROMPT}\n\nFilename: {audio_filename}",
            audio_part,
        ],
        config=types.GenerateContentConfig(temperature=0),
    )
    return _extract_response_text(response)


def _transcribe_with_deprecated_sdk(
    *,
    audio_bytes: bytes,
    audio_mime_type: str,
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
            TRANSCRIBE_PROMPT,
            {
                "mime_type": audio_mime_type,
                "data": audio_bytes,
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
