from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from schemas.analysis import AnalysisResponse
from services.analyzer import analyze_framing
from services.link_extractor import extract_text_from_link
from services.ocr import extract_text
from services.search import fetch_related_coverage
from services.summarizer import build_summary

router = APIRouter(tags=["analysis"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


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

        extracted_text = extract_text(contents, file.filename)
        source_type = "screenshot"
        source_url = None
        filename = file.filename

    # Link mode
    else:
        try:
            extracted_text = extract_text_from_link(post_link)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from link: {str(e)}",
            )
        source_type = "link"
        source_url = post_link
        filename = None

    framing = analyze_framing(extracted_text)
    coverage = fetch_related_coverage(extracted_text)
    summary = build_summary(extracted_text, framing, coverage)

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
