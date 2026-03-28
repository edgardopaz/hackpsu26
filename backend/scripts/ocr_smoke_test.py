from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.ocr import OCRError, extract_text


def main() -> None:
    image_path = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "src"
        / "assets"
        / "test-post.png"
    )
    image_bytes = image_path.read_bytes()

    try:
        result = extract_text(image_bytes, image_path.name)
    except OCRError as exc:
        print(f"OCR failed: {exc}")
        raise SystemExit(1) from exc

    print(repr(result))


if __name__ == "__main__":
    main()
