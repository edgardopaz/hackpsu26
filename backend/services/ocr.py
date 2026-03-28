def extract_text(image_bytes: bytes, filename: str) -> str:
    size_hint = len(image_bytes)

    return (
        "OCR placeholder output. "
        f"Received `{filename}` with approximately {size_hint} bytes. "
        "Wire Gemini Vision here to replace this synthetic extraction with real text."
    )

