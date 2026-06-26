from xau_lfx.config import artifact_paths
from xau_lfx.forbidden_language import assert_clean_language
from xau_lfx.pipeline import run_once
from xau_lfx.utils import read_json


def test_context_summary_artifact_is_generated_from_sample_data(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)
    summary = read_json(artifact_paths(tmp_path)["context_summary"])

    assert summary["monitor_only"] is True
    assert summary["symbol"] == "XAUUSD"
    assert summary["latest_close"] is not None
    assert summary["spread_state"] in {"STABLE", "WATCH", "UNSTABLE", "MISSING"}
    assert isinstance(summary["confidence_explanation"], list)
    assert summary["confidence_explanation"]
    assert isinstance(summary["monitor_focus"], list)
    assert summary["monitor_focus"]
    assert isinstance(summary["practical_zone_deck"], list)
    assert summary["practical_zone_deck"]
    lead_zone = summary["practical_zone_deck"][0]
    assert lead_zone["rank"] == 1
    assert lead_zone["role"].endswith("_REFERENCE")
    assert lead_zone["side_from_latest"] in {"above", "below", "at"}
    assert lead_zone["distance_points"] >= 0
    assert "operator_read" in lead_zone
    assert_clean_language(summary)


def test_context_summary_handles_empty_sources_without_signal_language():
    from xau_lfx.engines.context_summary import build_context_summary

    summary = build_context_summary(
        {"symbol": "XAUUSD", "quality_flags": ["SPREAD_SOURCE_MISSING"], "present_timeframes": [], "freshness_score": 0.0},
        {"bars": [], "latest_by_timeframe": {}, "median_latest_close": None},
        {"session_ranges": {}},
        {"risk_state": "CAUTION", "event_count": 0, "quality_flags": []},
        {"status": "WARN", "quality_grade": "F", "confidence_cap": 0.0},
    )

    assert summary["latest_close"] is None
    assert summary["nearest_session_level"] is None
    assert summary["practical_zone_deck"] == []
    assert summary["spread_state"] == "MISSING"
    assert_clean_language(summary)
