from __future__ import annotations

import importlib
import json
import os
import warnings
from typing import Any

from core.config import get_settings
from schemas.analysis import CoverageItem, FramingAnalysis, NeutralSummary, SummaryResult


DEFAULT_SUMMARY_MODEL = "gemini-2.5-flash"
SUMMARY_PROMPT_TEMPLATE = """
You are summarizing a potentially misleading social or news-style post.

Your job:
- Use only the OCR text, framing analysis, and coverage snippets provided below.
- Do not claim anything that is not supported by the supplied materials.
- If the evidence is mixed or incomplete, say so plainly.
- Keep the tone neutral and concise.
- Return valid JSON only.

Return this exact JSON shape:
{{
  "what_is_known": "...",
  "what_is_unclear": "...",
  "user_takeaway": "...",
  "verdict": "..."
}}

OCR text:
{ocr_text}

Framing analysis summary:
{framing_summary}

Framing signals:
{framing_signals}

Coverage:
{coverage_block}
""".strip()


class SummaryError(RuntimeError):
    """Raised when summary generation fails in a user-actionable way."""


def build_summary(
    extracted_text: str,
    framing: FramingAnalysis,
    coverage: list[CoverageItem],
) -> SummaryResult:
    if not extracted_text.strip():
        return SummaryResult(
            neutral_summary=NeutralSummary(
                what_is_known="No usable text was extracted from the upload.",
                what_is_unclear="Without extracted text, the claim cannot be compared against broader coverage.",
                user_takeaway="Try a clearer screenshot or image with readable text before trusting the post.",
            ),
            verdict="No usable text was extracted from the upload.",
        )

    api_key = get_settings().gemini_api_key.strip()
    if not api_key:
        raise SummaryError("GEMINI_API_KEY is not set.")

    prompt = _build_prompt(extracted_text, framing, coverage)
    model_name = os.getenv("GEMINI_SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL)

    try:
        response_text = _generate_with_google_genai(
            prompt=prompt,
            api_key=api_key,
            model_name=model_name,
        )
    except ImportError:
        try:
            response_text = _generate_with_deprecated_sdk(
                prompt=prompt,
                api_key=api_key,
                model_name=model_name,
            )
        except ImportError as exc:
            raise SummaryError(
                "No Gemini Python SDK is installed. Install dependencies with "
                "`python -m pip install -r requirements.txt`."
            ) from exc
        except Exception as exc:
            raise SummaryError(f"Gemini summary request failed: {exc}") from exc
    except Exception as exc:
        raise SummaryError(f"Gemini summary request failed: {exc}") from exc

    payload = _parse_summary_payload(response_text)

    return SummaryResult(
        neutral_summary=NeutralSummary(
            what_is_known=payload["what_is_known"],
            what_is_unclear=payload["what_is_unclear"],
            user_takeaway=payload["user_takeaway"],
        ),
        verdict=payload["verdict"],
    )


def _build_prompt(
    extracted_text: str,
    framing: FramingAnalysis,
    coverage: list[CoverageItem],
) -> str:
    signal_lines = "\n".join(
        f"- {signal.label} (score {signal.score}/5): {signal.explanation}"
        for signal in framing.signals
    )
    if not signal_lines:
        signal_lines = "- No framing signals were detected."

    coverage_lines = "\n".join(
        f"- Outlet: {item.outlet}\n  Title: {item.title}\n  Angle: {item.angle}\n  URL: {item.url or 'N/A'}"
        for item in coverage
    )
    if not coverage_lines:
        coverage_lines = "- No coverage results were found."

    return SUMMARY_PROMPT_TEMPLATE.format(
        ocr_text=extracted_text.strip(),
        framing_summary=f"{framing.summary} Overall risk: {framing.overall_risk}.",
        framing_signals=signal_lines,
        coverage_block=coverage_lines,
    )


def _generate_with_google_genai(*, prompt: str, api_key: str, model_name: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return _extract_response_text(response)


def _generate_with_deprecated_sdk(*, prompt: str, api_key: str, model_name: str) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        genai = importlib.import_module("google.generativeai")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name)
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.2},
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


def _parse_summary_payload(response_text: str) -> dict[str, str]:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise SummaryError(f"Summary model returned non-JSON output: {response_text}") from exc

    required_fields = ["what_is_known", "what_is_unclear", "user_takeaway", "verdict"]
    for field in required_fields:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise SummaryError(f"Summary model returned an invalid `{field}` field.")

    return {field: payload[field].strip() for field in required_fields}
