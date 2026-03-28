from __future__ import annotations

import importlib
import json
import os
import warnings
from typing import Any

from core.config import get_settings
from schemas.analysis import FramingAnalysis, FramingSignal


DEFAULT_ANALYZER_MODEL = "gemini-2.5-flash"
ANALYZER_PROMPT_TEMPLATE = """
You are analyzing whether text uses misleading, manipulative, sensational, or bait-like framing.

Focus on framing, not factual accuracy. Look for:
- urgency cues
- sensational or exaggerated wording
- emotional provocation
- implication without evidence
- selective or misleading presentation
- commands telling the audience how to feel or react

Return valid JSON only in this exact shape:
{{
  "overall_risk": "low" | "medium" | "high",
  "summary": "...",
  "signals": [
    {{
      "label": "...",
      "explanation": "...",
      "score": 1
    }}
  ]
}}

Rules:
- Include 1 to 4 signals.
- Scores must be integers from 1 to 5.
- If the text is mostly neutral, include one low-score signal explaining that.
- Judge only the framing visible in the provided text.

Text to analyze:
{text}
""".strip()


class AnalyzerError(RuntimeError):
    """Raised when framing analysis fails in a user-actionable way."""


def analyze_framing(text: str) -> FramingAnalysis:
    normalized_text = text.strip()
    if not normalized_text:
        return FramingAnalysis(
            overall_risk="low",
            summary="No text was available to analyze for framing.",
            signals=[
                FramingSignal(
                    label="No readable text",
                    explanation="The upload did not provide enough text to assess framing.",
                    score=1,
                )
            ],
        )

    api_key = get_settings().gemini_api_key.strip()
    if not api_key:
        raise AnalyzerError("GEMINI_API_KEY is not set.")

    prompt = ANALYZER_PROMPT_TEMPLATE.format(text=normalized_text)
    model_name = os.getenv("GEMINI_ANALYZER_MODEL", DEFAULT_ANALYZER_MODEL)

    try:
        response_text = _analyze_with_google_genai(
            prompt=prompt,
            api_key=api_key,
            model_name=model_name,
        )
    except ImportError:
        try:
            response_text = _analyze_with_deprecated_sdk(
                prompt=prompt,
                api_key=api_key,
                model_name=model_name,
            )
        except ImportError as exc:
            raise AnalyzerError(
                "No Gemini Python SDK is installed. Install dependencies with "
                "`python -m pip install -r requirements.txt`."
            ) from exc
        except Exception as exc:
            raise AnalyzerError(f"Gemini framing analysis failed: {exc}") from exc
    except Exception as exc:
        raise AnalyzerError(f"Gemini framing analysis failed: {exc}") from exc

    payload = _parse_analysis_payload(response_text)
    signals = [
        FramingSignal(
            label=signal["label"],
            explanation=signal["explanation"],
            score=signal["score"],
        )
        for signal in payload["signals"]
    ]

    return FramingAnalysis(
        overall_risk=payload["overall_risk"],
        summary=payload["summary"],
        signals=signals,
    )


def _analyze_with_google_genai(*, prompt: str, api_key: str, model_name: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1),
    )
    return _extract_response_text(response)


def _analyze_with_deprecated_sdk(*, prompt: str, api_key: str, model_name: str) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        genai = importlib.import_module("google.generativeai")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name)
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.1},
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


def _parse_analysis_payload(response_text: str) -> dict[str, Any]:
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AnalyzerError(f"Analyzer model returned non-JSON output: {response_text}") from exc

    risk = payload.get("overall_risk")
    if risk not in {"low", "medium", "high"}:
        raise AnalyzerError("Analyzer model returned an invalid `overall_risk` field.")

    summary = payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise AnalyzerError("Analyzer model returned an invalid `summary` field.")

    signals = payload.get("signals")
    if not isinstance(signals, list) or not signals:
        raise AnalyzerError("Analyzer model returned an invalid `signals` field.")

    normalized_signals: list[dict[str, Any]] = []
    for signal in signals[:4]:
        label = signal.get("label")
        explanation = signal.get("explanation")
        score = signal.get("score")

        if not isinstance(label, str) or not label.strip():
            raise AnalyzerError("Analyzer model returned a signal with an invalid `label`.")
        if not isinstance(explanation, str) or not explanation.strip():
            raise AnalyzerError("Analyzer model returned a signal with an invalid `explanation`.")
        if not isinstance(score, int) or not 1 <= score <= 5:
            raise AnalyzerError("Analyzer model returned a signal with an invalid `score`.")

        normalized_signals.append(
            {
                "label": label.strip(),
                "explanation": explanation.strip(),
                "score": score,
            }
        )

    return {
        "overall_risk": risk,
        "summary": summary.strip(),
        "signals": normalized_signals,
    }
