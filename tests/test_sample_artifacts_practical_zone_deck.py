import json
from pathlib import Path

from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ARTIFACTS = ROOT / "examples" / "sample-artifacts"


def test_sample_context_summary_includes_practical_zone_deck():
    payload = json.loads((SAMPLE_ARTIFACTS / "xau_context_summary.json").read_text(encoding="utf-8"))

    assert payload["monitor_only"] is True
    assert payload["practical_zone_deck"]
    assert payload["practical_zone_deck"][0]["rank"] == 1
    assert payload["practical_zone_deck"][0]["session"] == "OFF_SESSION"
    assert payload["practical_zone_deck"][0]["level"] == "low"
    assert payload["practical_zone_deck"][0]["side_from_latest"] == "below"
    assert payload["practical_zone_deck"][0]["distance_points"] == 1.68
    assert "Practical zone deck ranks supplied session references by distance only" in payload["limitations"][-1]
    assert_clean_language(payload)


def test_sample_market_report_renders_practical_zone_deck():
    text = (SAMPLE_ARTIFACTS / "xau_market_context_report.md").read_text(encoding="utf-8")

    assert "## Practical Zone Deck" in text
    assert "Rank 1: OFF_SESSION low at 2337.15" in text
    assert "Start inspection with practical zone rank 1" in text
    assert "Practical zone deck ranks supplied session references by distance only" in text
    assert_clean_language(text)
