from fastapi import HTTPException

from api.routes import analyze_upload, healthcheck
from schemas.analysis import CoverageItem, FramingAnalysis, FramingSignal, NeutralSummary, SummaryResult
from services.link_extractor import LinkExtractionError


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
            article_summary="This post is about a breaking development tied to a reported incident.",
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
    assert payload.article_summary == "This post is about a breaking development tied to a reported incident."
    assert payload.framing.overall_risk == "medium"
    assert payload.coverage[0].outlet == "Reuters"
    assert payload.neutral_summary.what_is_known == "Known test fact."
    assert payload.verdict == "Mixed support."


def test_analyze_upload_routes_audio_to_transcriber(monkeypatch) -> None:
    import asyncio

    monkeypatch.setattr("api.routes.classify_media", lambda *_args, **_kwargs: "audio")
    monkeypatch.setattr("api.routes.transcribe_media", lambda *_args, **_kwargs: "Audio transcript text")
    monkeypatch.setattr(
        "api.routes.analyze_framing",
        lambda _text: FramingAnalysis(
            overall_risk="low",
            summary="Mostly neutral spoken framing.",
            signals=[
                FramingSignal(
                    label="Low signal language",
                    explanation="The transcript is mostly descriptive.",
                    score=1,
                )
            ],
        ),
    )
    monkeypatch.setattr("api.routes.fetch_related_coverage", lambda _text: [])
    monkeypatch.setattr(
        "api.routes.build_summary",
        lambda *_args, **_kwargs: SummaryResult(
            article_summary="This clip discusses a spoken claim.",
            neutral_summary=NeutralSummary(
                what_is_known="Known audio fact.",
                what_is_unclear="Unknown audio fact.",
                user_takeaway="Listen critically.",
            ),
            verdict="Needs more corroboration.",
        ),
    )

    upload = FakeUploadFile(filename="clip.mp3", content=b"fake-audio-bytes")
    payload = asyncio.run(analyze_upload(upload, ""))

    assert payload.source_type == "audio"
    assert payload.extracted_text == "Audio transcript text"
    assert payload.article_summary == "This clip discusses a spoken claim."


def test_analyze_upload_routes_pdf_to_document_extraction(monkeypatch) -> None:
    import asyncio

    monkeypatch.setattr("api.routes.classify_media", lambda *_args, **_kwargs: "document")
    monkeypatch.setattr("api.routes.extract_text", lambda *_args, **_kwargs: "PDF extracted text")
    monkeypatch.setattr(
        "api.routes.analyze_framing",
        lambda _text: FramingAnalysis(
            overall_risk="low",
            summary="Document framing is mostly neutral.",
            signals=[
                FramingSignal(
                    label="Low signal language",
                    explanation="The document text is mostly descriptive.",
                    score=1,
                )
            ],
        ),
    )
    monkeypatch.setattr("api.routes.fetch_related_coverage", lambda _text: [])
    monkeypatch.setattr(
        "api.routes.build_summary",
        lambda *_args, **_kwargs: SummaryResult(
            article_summary="This document covers a reported claim.",
            neutral_summary=NeutralSummary(
                what_is_known="Known PDF fact.",
                what_is_unclear="Unknown PDF fact.",
                user_takeaway="Read critically.",
            ),
            verdict="Document analyzed.",
        ),
    )

    upload = FakeUploadFile(filename="report.pdf", content=b"%PDF-test")
    payload = asyncio.run(analyze_upload(upload, ""))

    assert payload.source_type == "document"
    assert payload.extracted_text == "PDF extracted text"
    assert payload.article_summary == "This document covers a reported claim."


def test_analyze_upload_returns_stage_specific_link_error(monkeypatch) -> None:
    import asyncio

    monkeypatch.setattr(
        "api.routes.extract_text_from_link",
        lambda _link: (_ for _ in ()).throw(LinkExtractionError("bad link")),
    )

    try:
        asyncio.run(analyze_upload(None, "https://example.com/post"))
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "Link extraction failed: bad link" == exc.detail
    else:
        raise AssertionError("Expected HTTPException to be raised.")
