from schemas.analysis import FramingAnalysis, FramingSignal


BAIT_PHRASES = {
    "breaking": ("Urgency framing", "Uses urgency language that can push people to react before verifying."),
    "shocking": ("Sensational wording", "Relies on exaggerated wording instead of precise description."),
    "you won't believe": ("Curiosity bait", "Uses a hook designed to provoke clicks rather than inform."),
    "must see": ("Imperative framing", "Tells the viewer how to react instead of presenting evidence."),
    "exposed": ("Conflict framing", "Suggests revelation or scandal without establishing context."),
}


def analyze_framing(text: str) -> FramingAnalysis:
    lowered_text = text.lower()
    signals: list[FramingSignal] = []

    for phrase, (label, explanation) in BAIT_PHRASES.items():
        if phrase in lowered_text:
            signals.append(
                FramingSignal(
                    label=label,
                    explanation=explanation,
                    score=4,
                )
            )

    if not signals:
        signals.append(
            FramingSignal(
                label="Low signal language",
                explanation="No obvious bait-like phrasing was detected in the extracted text.",
                score=1,
            )
        )

    risk = "low"
    if len(signals) >= 3:
        risk = "high"
    elif any(signal.score >= 4 for signal in signals):
        risk = "medium"

    return FramingAnalysis(
        overall_risk=risk,
        summary=(
            "This is a heuristic scaffold. Replace it with an LLM prompt or classifier "
            "once your OCR output and search coverage are connected."
        ),
        signals=signals,
    )

