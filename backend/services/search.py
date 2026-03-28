from schemas.analysis import CoverageItem


def fetch_related_coverage(query: str) -> list[CoverageItem]:
    if not query.strip():
        return []

    return []

