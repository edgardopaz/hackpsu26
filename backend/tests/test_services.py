from services.analyzer import _parse_analysis_payload
from services.search import _extract_outlet_name, _normalize_query, _is_usable_result, _sanitize_content
from services.summarizer import _parse_summary_payload


def test_normalize_query_collapses_whitespace() -> None:
    assert _normalize_query("a  b\n\nc") == "a b c"


def test_extract_outlet_name_handles_known_acronyms() -> None:
    assert _extract_outlet_name("https://www.wsj.com/story") == "WSJ"
    assert _extract_outlet_name("https://www.cnn.com/story") == "CNN"


def test_is_usable_result_requires_title_and_url() -> None:
    assert _is_usable_result({"title": "A", "url": "https://example.com"}) is True
    assert _is_usable_result({"title": "A"}) is False
    assert _is_usable_result({"url": "https://example.com"}) is False


def test_sanitize_content_removes_promotional_lines() -> None:
    content = """
    #### Shop now Our best Amazon deals list is full of hidden gems
    Save Saved Read in app
    The USS Gerald R. Ford is docked in Crete for repairs after a fire in the laundry area.
    The Navy says the carrier remains fully mission capable.
    Sign up for our daily newsletter.
    """.strip()

    cleaned = _sanitize_content(content)

    assert "Shop now" not in cleaned
    assert "Read in app" not in cleaned
    assert "newsletter" not in cleaned.lower()
    assert "USS Gerald R. Ford is docked in Crete for repairs" in cleaned


def test_parse_analysis_payload_accepts_valid_json() -> None:
    payload = _parse_analysis_payload(
        '{"overall_risk":"low","summary":"Neutral","signals":[{"label":"Low signal language","explanation":"Mostly neutral.","score":1}]}'
    )

    assert payload["overall_risk"] == "low"
    assert payload["signals"][0]["score"] == 1


def test_parse_summary_payload_accepts_valid_json() -> None:
    payload = _parse_summary_payload(
        '{"article_summary":"Topic summary","what_is_known":"A","what_is_unclear":"B","user_takeaway":"C","verdict":"D"}'
    )

    assert payload["article_summary"] == "Topic summary"
    assert payload["what_is_known"] == "A"
    assert payload["verdict"] == "D"
