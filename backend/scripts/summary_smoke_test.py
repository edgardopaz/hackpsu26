from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.analyzer import analyze_framing
from services.ocr import extract_text
from services.search import fetch_related_coverage
from services.summarizer import SummaryError, build_summary


def main() -> None:
    image_path = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "src"
        / "assets"
        / "test-post.png"
    )
    extracted_text = extract_text(image_path.read_bytes(), image_path.name)
    framing = analyze_framing(extracted_text)
    coverage = fetch_related_coverage(extracted_text)

    try:
        summary = build_summary(extracted_text, framing, coverage)
    except SummaryError as exc:
        print(f"Summary failed: {exc}")
        raise SystemExit(1) from exc

    print(summary.model_dump())


if __name__ == "__main__":
    main()
