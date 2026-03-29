import argparse
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.media import MediaError, classify_media
from services.transcriber import TranscriptionError, transcribe_media


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Smoke test audio/video transcription against the backend media pipeline.",
    )
    parser.add_argument("media_path", help="Path to an audio or video file")
    args = parser.parse_args()

    media_path = Path(args.media_path).expanduser().resolve()
    if not media_path.exists():
        print(f"Media file not found: {media_path}")
        raise SystemExit(1)

    try:
        media_type = classify_media(media_path.name)
        transcript = transcribe_media(media_path.read_bytes(), media_path.name)
    except (MediaError, TranscriptionError) as exc:
        print(f"Media smoke test failed: {exc}")
        raise SystemExit(1) from exc

    print({"media_type": media_type, "filename": media_path.name, "transcript": transcript})


if __name__ == "__main__":
    main()
