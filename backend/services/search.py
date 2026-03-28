from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from core.config import get_settings
from schemas.analysis import CoverageItem


DEFAULT_MAX_RESULTS = 3
MAX_QUERY_LENGTH = 400


class SearchError(RuntimeError):
    """Raised when external coverage lookup fails in a user-actionable way."""


def fetch_related_coverage(query: str) -> list[CoverageItem]:
    normalized_query = _normalize_query(query)
    if not normalized_query:
        return []

    api_key = get_settings().tavily_api_key.strip()
    if not api_key:
        raise SearchError("TAVILY_API_KEY is not set.")

    try:
        from tavily import TavilyClient
    except ImportError as exc:
        raise SearchError(
            "Tavily SDK is not installed. Install dependencies with "
            "`python -m pip install -r requirements.txt`."
        ) from exc

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=normalized_query,
            topic="news",
            search_depth="advanced",
            max_results=DEFAULT_MAX_RESULTS,
            include_answer=False,
            include_raw_content=False,
        )
    except Exception as exc:
        raise SearchError(f"Tavily search request failed: {exc}") from exc

    results = response.get("results", [])
    coverage_items = [_to_coverage_item(item) for item in results if _is_usable_result(item)]
    return coverage_items[:DEFAULT_MAX_RESULTS]


def _normalize_query(query: str) -> str:
    collapsed = re.sub(r"\s+", " ", query).strip()
    if not collapsed:
        return ""

    if len(collapsed) <= MAX_QUERY_LENGTH:
        return collapsed

    truncated = collapsed[:MAX_QUERY_LENGTH]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return truncated.strip()


def _to_coverage_item(result: dict[str, Any]) -> CoverageItem:
    url = result.get("url")
    published_date = result.get("published_date")
    return CoverageItem(
        outlet=_extract_outlet_name(url),
        title=result.get("title", "Untitled result"),
        angle=_build_angle(result),
        url=url,
        published_date=published_date,
    )


def _is_usable_result(result: dict[str, Any]) -> bool:
    return bool(result.get("title") and result.get("url"))


def _build_angle(result: dict[str, Any]) -> str:
    content = (result.get("content") or "").strip()
    published_date = result.get("published_date")

    if content:
        if published_date:
            return f"{content} Published: {published_date}."
        return content

    if published_date:
        return f"Coverage result published on {published_date}."

    return "Coverage retrieved, but no descriptive snippet was returned."


def _extract_outlet_name(url: str | None) -> str:
    if not url:
        return "Unknown outlet"

    hostname = urlparse(url).netloc.lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]

    if not hostname:
        return "Unknown outlet"

    outlet = hostname.split(".")[0].replace("-", " ").replace("_", " ").strip()
    if not outlet:
        return hostname

    acronym_map = {
        "ap": "AP",
        "bbc": "BBC",
        "cnn": "CNN",
        "npr": "NPR",
        "wsj": "WSJ",
    }
    return acronym_map.get(outlet, outlet.title())
