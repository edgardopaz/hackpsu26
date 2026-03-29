from __future__ import annotations

import mimetypes
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".webm"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}

IMAGE_MIME_PREFIX = "image/"
AUDIO_MIME_PREFIX = "audio/"
VIDEO_MIME_PREFIX = "video/"


class MediaError(RuntimeError):
    """Raised when uploaded media cannot be validated or prepared."""


def classify_media(filename: str, content_type: str | None = None) -> str:
    if not filename:
        raise MediaError("Uploaded file is missing a filename.")

    if content_type:
        if content_type.startswith(IMAGE_MIME_PREFIX):
            return "image"
        if content_type.startswith(AUDIO_MIME_PREFIX):
            return "audio"
        if content_type.startswith(VIDEO_MIME_PREFIX):
            return "video"

    extension = Path(filename).suffix.lower()
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension in AUDIO_EXTENSIONS:
        return "audio"
    if extension in VIDEO_EXTENSIONS:
        return "video"

    raise MediaError(
        "Unsupported media type. Upload an image, audio file, or video file."
    )


def guess_mime_type(filename: str, content_type: str | None = None) -> str:
    if content_type:
        return content_type

    mime_type, _ = mimetypes.guess_type(filename)
    media_type = classify_media(filename, content_type)

    if mime_type:
        return mime_type
    if media_type == "image":
        return "image/png"
    if media_type == "audio":
        return "audio/mpeg"
    return "video/mp4"


def prepare_transcription_media(
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None,
) -> tuple[bytes, str, str, str]:
    media_type = classify_media(filename, content_type)
    mime_type = guess_mime_type(filename, content_type)

    if media_type == "audio":
        return file_bytes, filename, mime_type, media_type

    if media_type == "video":
        audio_bytes, audio_filename, audio_mime = _extract_audio_from_video(
            file_bytes=file_bytes,
            filename=filename,
        )
        return audio_bytes, audio_filename, audio_mime, media_type

    raise MediaError("Only audio or video files can be prepared for transcription.")


def _extract_audio_from_video(
    *,
    file_bytes: bytes,
    filename: str,
) -> tuple[bytes, str, str]:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise MediaError(
            "Video uploads require ffmpeg to extract audio, but ffmpeg is not installed."
        )

    video_suffix = Path(filename).suffix.lower() or ".mp4"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        video_path = temp_path / f"input{video_suffix}"
        audio_path = temp_path / "audio.mp3"
        video_path.write_bytes(file_bytes)

        command = [
            ffmpeg_path,
            "-y",
            "-i",
            os.fspath(video_path),
            "-vn",
            "-acodec",
            "libmp3lame",
            "-ar",
            "16000",
            "-ac",
            "1",
            os.fspath(audio_path),
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise MediaError(f"ffmpeg failed to extract audio: {exc.stderr.strip()}") from exc

        if not audio_path.exists():
            raise MediaError("ffmpeg did not produce an audio track for transcription.")

        return audio_path.read_bytes(), f"{Path(filename).stem}.mp3", "audio/mpeg"
