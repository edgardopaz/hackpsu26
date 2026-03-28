from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.search import SearchError, fetch_related_coverage


def main() -> None:
    query = (
        "Iran War Live Updates U.S. Marines Arrive in Middle East, "
        "as Houthis Enter War"
    )

    try:
        results = fetch_related_coverage(query)
    except SearchError as exc:
        print(f"Search failed: {exc}")
        raise SystemExit(1) from exc

    for item in results:
        print(item.model_dump())


if __name__ == "__main__":
    main()
