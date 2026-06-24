import json
from pathlib import Path
from typing import Any

from xau_lfx.engines.context_summary import build_context_summary
from xau_lfx.forbidden_language import assert_clean_language


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests" / "fixtures" / "context_summary_snapshot.json"


def _normalize(summary: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(summary)
    normalized["ts_utc"] = "<generated>"
    return normalized


def test_context_summary_matches_monitor_only_snapshot():
    summary = build_context_summary(
        data_quality={
            "symbol": "XAUUSD",
            "present_timeframes": ["M5", "M15", "H1"],
            "freshness_score": 1.0,
            "spread_stability": 0.95,
            "confidence_cap": 0.75,
            "errors": [],
            "quality_flags": ["USD_HIGH_IMPACT_EVENT_PRESENT"],
        },
        composite={
            "median_latest_close": 2338.83,
            "latest_by_timeframe": {},
            "bars": [],
        },
        session={
            "session_ranges": {
                "OFF_SESSION": {"high": 2344.2, "low": 2337.15},
                "ASIA": {"high": 2348.0, "low": 2328.0},
            },
        },
        event={
            "risk_state": "CONTEXT",
            "event_count": 1,
            "near_high_impact_events": [],
            "quality_flags": ["USD_HIGH_IMPACT_EVENT_PRESENT"],
        },
        artifact_quality={
            "status": "OK",
            "quality_grade": "A",
            "confidence_cap": 0.75,
        },
    )

    actual = _normalize(summary)
    expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert actual == expected
    assert actual["monitor_only"] is True
    assert_clean_language(actual)
