from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from schemas.analysis import AnalysisResponse
from services.analyzer import AnalyzerError, analyze_framing
from services.link_extractor import LinkExtractionError, extract_text_from_link
from services.media import MediaError, classify_media
from services.ocr import OCRError, extract_text
from services.search import SearchError, fetch_related_coverage
from services.summarizer import SummaryError, build_summary
from services.transcriber import TranscriptionError, transcribe_media

router = APIRouter(tags=["analysis"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


def _raise_http_error(
    *,
    detail: str,
    status_code: int = status.HTTP_502_BAD_GATEWAY,
) -> None:
    raise HTTPException(status_code=status_code, detail=detail)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_upload(
    file: UploadFile = File(default=None),
    post_link: str = Form(default="")
) -> AnalysisResponse:
    # Ensure exactly one mode is provided
    if file and post_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either a screenshot or a link, not both.",
        )
    
    if not file and not post_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either upload a screenshot or provide a social media link.",
        )

    # Screenshot mode
    if file:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A file upload is required.",
            )

        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        try:
            media_type = classify_media(file.filename, getattr(file, "content_type", None))
            if media_type in {"image", "document"}:
                try:
                    extracted_text = extract_text(contents, file.filename)
                except OCRError as exc:
                    _raise_http_error(detail=f"Text extraction failed: {exc}")
                source_type = "document" if media_type == "document" else "screenshot"
            else:
                extracted_text = transcribe_media(
                    contents,
                    file.filename,
                    getattr(file, "content_type", None),
                )
                source_type = media_type
        except (MediaError, TranscriptionError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        source_url = None
        filename = file.filename

    # Link mode
    else:
        try:
            extracted_text = extract_text_from_link(post_link)
        except LinkExtractionError as exc:
            _raise_http_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Link extraction failed: {exc}",
            )
        except Exception as exc:
            _raise_http_error(detail=f"Link extraction failed: {exc}")
        source_type = "link"
        source_url = post_link
        filename = None

    try:
        framing = analyze_framing(extracted_text)
    except AnalyzerError as exc:
        _raise_http_error(detail=f"Framing analysis failed: {exc}")

    try:
        coverage = fetch_related_coverage(extracted_text)
    except SearchError as exc:
        _raise_http_error(detail=f"Coverage search failed: {exc}")

    try:
        summary = build_summary(extracted_text, framing, coverage)
    except SummaryError as exc:
        _raise_http_error(detail=f"Summary generation failed: {exc}")

    return AnalysisResponse(
        source_type=source_type,
        source_url=source_url,
        filename=filename,
        extracted_text=extracted_text,
        article_summary=summary.article_summary,
        framing=framing,
        coverage=coverage,
        neutral_summary=summary.neutral_summary,
        verdict=summary.verdict,
    )
