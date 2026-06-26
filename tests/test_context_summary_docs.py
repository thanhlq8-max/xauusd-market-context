from pathlib import Path

from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]


def test_context_summary_docs_cover_practical_zone_deck_contract():
    text = (ROOT / "docs" / "CONTEXT_SUMMARY.md").read_text(encoding="utf-8")

    for required_phrase in [
        "practical_zone_deck",
        "side_from_latest",
        "distance_points",
        "above",
        "below",
        "at",
        "distance measurement, not a directional forecast",
        "docs/PRACTICAL_ZONE_DECK.md",
    ]:
        assert required_phrase in text

    assert_clean_language(text)
