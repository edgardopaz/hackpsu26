from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_upload_returns_scaffolded_response() -> None:
    response = client.post(
        "/api/analyze",
        files={"file": ("post.png", b"fake-image-bytes", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "post.png"
    assert "OCR placeholder output" in payload["extracted_text"]
    assert "framing" in payload
    assert "neutral_summary" in payload

