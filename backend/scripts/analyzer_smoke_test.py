from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.analyzer import AnalyzerError, analyze_framing
from services.ocr import extract_text


def main() -> None:
    image_path = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "src"
        / "assets"
        / "test-post.png"
    )
    extracted_text = extract_text(image_path.read_bytes(), image_path.name)

    try:
        analysis = analyze_framing(extracted_text)
    except AnalyzerError as exc:
        print(f"Analyzer failed: {exc}")
        raise SystemExit(1) from exc

    print(analysis.model_dump())


if __name__ == "__main__":
    main()
