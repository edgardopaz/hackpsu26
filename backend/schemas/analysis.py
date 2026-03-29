from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]
SourceType = Literal["screenshot", "link", "audio", "video", "document"]


class FramingSignal(BaseModel):
    label: str
    explanation: str
    score: int = Field(ge=1, le=5)


class FramingAnalysis(BaseModel):
    overall_risk: RiskLevel
    summary: str
    signals: list[FramingSignal]


class CoverageItem(BaseModel):
    outlet: str
    title: str
    angle: str
    url: str | None = None
    published_date: str | None = None


class NeutralSummary(BaseModel):
    what_is_known: str
    what_is_unclear: str
    user_takeaway: str


class AnalysisResponse(BaseModel):
    source_type: SourceType
    source_url: str | None = None
    filename: str | None = None
    extracted_text: str
    article_summary: str
    framing: FramingAnalysis
    coverage: list[CoverageItem]
    neutral_summary: NeutralSummary
    verdict: str


class SummaryResult(BaseModel):
    article_summary: str
    neutral_summary: NeutralSummary
    verdict: str
