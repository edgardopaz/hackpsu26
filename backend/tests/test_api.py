from api.routes import analyze_upload, healthcheck
from schemas.analysis import CoverageItem, FramingAnalysis, FramingSignal, NeutralSummary, SummaryResult


class FakeUploadFile:
    def __init__(self, filename: str, content: bytes) -> None:
        self.filename = filename
        self._content = content

    async def read(self) -> bytes:
        return self._content


def test_healthcheck() -> None:
    import asyncio

    response = asyncio.run(healthcheck())

    assert response == {"status": "ok"}


def test_analyze_upload_returns_composed_response(monkeypatch) -> None:
    import asyncio

    monkeypatch.setattr("api.routes.extract_text", lambda *_args, **_kwargs: "Breaking: Test OCR text")
    monkeypatch.setattr(
        "api.routes.analyze_framing",
        lambda _text: FramingAnalysis(
            overall_risk="medium",
            summary="Some urgency framing detected.",
            signals=[
                FramingSignal(
                    label="Urgency cues",
                    explanation="Uses breaking-news style wording.",
                    score=3,
                )
            ],
        ),
    )
    monkeypatch.setattr(
        "api.routes.fetch_related_coverage",
        lambda _text: [
            CoverageItem(
                outlet="Reuters",
                title="Test coverage",
                angle="A neutral test snippet.",
                url="https://example.com/story",
                published_date="2026-03-28",
            )
        ],
    )
    monkeypatch.setattr(
        "api.routes.build_summary",
        lambda *_args, **_kwargs: SummaryResult(
            neutral_summary=NeutralSummary(
                what_is_known="Known test fact.",
                what_is_unclear="Unknown test fact.",
                user_takeaway="Read carefully.",
            ),
            verdict="Mixed support.",
        ),
    )

    upload = FakeUploadFile(filename="post.png", content=b"fake-image-bytes")
    payload = asyncio.run(analyze_upload(upload, ""))

    assert payload.source_type == "screenshot"
    assert payload.source_url is None
    assert payload.filename == "post.png"
    assert payload.extracted_text == "Breaking: Test OCR text"
    assert payload.framing.overall_risk == "medium"
    assert payload.coverage[0].outlet == "Reuters"
    assert payload.neutral_summary.what_is_known == "Known test fact."
    assert payload.verdict == "Mixed support."
