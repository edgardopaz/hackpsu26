from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.analysis import AnalysisResponse
from services.analyzer import analyze_framing
from services.ocr import extract_text
from services.search import fetch_related_coverage
from services.summarizer import build_summary

router = APIRouter(tags=["analysis"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_upload(file: UploadFile = File(...)) -> AnalysisResponse:
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
    framing = analyze_framing(extracted_text)
    coverage = fetch_related_coverage(extracted_text)
    summary = build_summary(extracted_text, framing, coverage)

    return AnalysisResponse(
        filename=file.filename,
        extracted_text=extracted_text,
        framing=framing,
        coverage=coverage,
        neutral_summary=summary.neutral_summary,
        verdict=summary.verdict,
    )

