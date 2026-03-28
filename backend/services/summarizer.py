from schemas.analysis import CoverageItem, FramingAnalysis, NeutralSummary, SummaryResult


def build_summary(
    extracted_text: str,
    framing: FramingAnalysis,
    coverage: list[CoverageItem],
) -> SummaryResult:
    known = (
        "The uploaded image contains text that can now be passed through the analysis pipeline. "
        "The current backend scaffold produces a framing assessment and preserves room for broader news comparison."
    )
    unclear = (
        "The search step is not yet connected to Tavily, so no external reporting has been retrieved to confirm or rebut the claim."
        if not coverage
        else "External coverage was found, but the comparison logic should still be tightened with a stronger prompt."
    )
    takeaway = (
        "Treat the framing score as an early warning, not a truth rating. "
        "A final verdict should depend on broader reporting once search is wired in."
    )

    verdict = {
        "high": "High-risk framing detected, but factual verification is still incomplete.",
        "medium": "Some persuasive or bait-like framing detected; compare against broader coverage before trusting it.",
        "low": "No strong bait-like signals detected in the current heuristic pass, but verification is still incomplete.",
    }[framing.overall_risk]

    if not extracted_text.strip():
        verdict = "No usable text was extracted from the upload."

    return SummaryResult(
        neutral_summary=NeutralSummary(
            what_is_known=known,
            what_is_unclear=unclear,
            user_takeaway=takeaway,
        ),
        verdict=verdict,
    )

