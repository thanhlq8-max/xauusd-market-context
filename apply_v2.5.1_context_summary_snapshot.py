from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old!r}")
    write(path, text.replace(old, new, 1))


# Version/documentation metadata only. Runtime behavior is unchanged.
replace_once("README.md", "# XAUUSD Market Context v2.5.0", "# XAUUSD Market Context v2.5.1")
replace_once(
    "README.md",
    "Generate auditable XAUUSD market-context artifacts from local MT5/broker CSV exports, spread snapshots, manual USD event files, or an optional private OANDA v20 Practice dashboard. v2.5.0 adds an artifact contract validator so shared JSON bundles can be checked before downstream inspection. The package is a monitor-only sidecar for XAU research workflows; it uses the LFX-2 material as a semantic and safety baseline without modifying or reproducing the Pine source.",
    "Generate auditable XAUUSD market-context artifacts from local MT5/broker CSV exports, spread snapshots, manual USD event files, or an optional private OANDA v20 Practice dashboard. v2.5.0 adds an artifact contract validator so shared JSON bundles can be checked before downstream inspection. v2.5.1 adds deterministic context-summary snapshot coverage so operator-facing wording changes are intentional. The package is a monitor-only sidecar for XAU research workflows; it uses the LFX-2 material as a semantic and safety baseline without modifying or reproducing the Pine source.",
)
replace_once("pyproject.toml", 'version = "2.5.0"', 'version = "2.5.1"')
replace_once(
    "CHANGELOG.md",
    "# Changelog\n\n## v2.5.0 - Artifact contract validation",
    "# Changelog\n\n## v2.5.1 - Context summary snapshot coverage\n\n### Added\n\n- Deterministic snapshot coverage for `xau_context_summary.json` monitor-only wording and key public fields.\n- Static fixture under `tests/fixtures/` for context-summary review.\n\n### Preserved\n\n- No runtime calculation changes.\n- No CSV ingestion, OANDA Practice dashboard, report, site, or artifact contract behavior changes.\n- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.\n\n## v2.5.0 - Artifact contract validation",
)
replace_once(
    "ROADMAP.md",
    "- `v2.5.0`: artifact contract validation for generated JSON bundles.\n",
    "- `v2.5.0`: artifact contract validation for generated JSON bundles.\n- `v2.5.1`: context-summary snapshot coverage for operator-facing wording stability.\n",
)
replace_once(
    "docs/REAL_WORLD_USAGE.md",
    "## Live OANDA Practice case",
    "## Case 7: context-summary wording is snapshot-guarded\n\n**Input condition:** synthetic context inputs are passed directly into the context-summary builder.\n\n**Expected result:** `tests/fixtures/context_summary_snapshot.json` records the expected public shape and monitor-only wording after normalizing the generated timestamp.\n\n**Practical value:** future edits to operator-facing wording or public fields become intentional review changes instead of silent drift.\n\nInspect:\n\n```text\ntests/test_context_summary_snapshot.py\ntests/fixtures/context_summary_snapshot.json\n```\n\n## Live OANDA Practice case",
)

write(
    "tests/fixtures/context_summary_snapshot.json",
    """{\n  \"ts_utc\": \"<generated>\",\n  \"symbol\": \"XAUUSD\",\n  \"monitor_only\": true,\n  \"latest_close\": 2338.83,\n  \"freshness_age_minutes\": null,\n  \"nearest_session_level\": {\n    \"session\": \"OFF_SESSION\",\n    \"level\": \"low\",\n    \"price\": 2337.15,\n    \"distance_points\": 1.68\n  },\n  \"spread_state\": \"STABLE\",\n  \"event_risk_state\": \"CONTEXT\",\n  \"quality_status\": \"OK\",\n  \"quality_grade\": \"A\",\n  \"confidence_cap\": 0.75,\n  \"confidence_explanation\": [\n    \"M5/M15/H1 local bar coverage is complete.\",\n    \"Latest local bars are fresh relative to the 72-hour freshness window.\",\n    \"Spread source is stable enough for monitor context.\",\n    \"Event file is loaded and used as risk context only.\"\n  ],\n  \"monitor_focus\": [\n    \"Observe behavior around OFF_SESSION low (2337.15); distance 1.68 points.\",\n    \"Compare M15 context with M5 confirmation behavior and H1 structural context.\",\n    \"Keep spread stability on the monitor list during active sessions.\",\n    \"Keep the event file current before major USD macro windows.\"\n  ],\n  \"limitations\": [\n    \"Monitor-only context summary; not an execution plan.\",\n    \"Broker tick activity remains a local activity proxy, not centralized volume.\",\n    \"Session levels are references from supplied CSV data only.\"\n  ],\n  \"quality_flags\": [\n    \"USD_HIGH_IMPACT_EVENT_PRESENT\"\n  ]\n}\n""",
)

write(
    "tests/test_context_summary_snapshot.py",
    """import json\nfrom pathlib import Path\nfrom typing import Any\n\nfrom xau_lfx.engines.context_summary import build_context_summary\nfrom xau_lfx.forbidden_language import assert_clean_language\n\n\nROOT = Path(__file__).resolve().parents[1]\nSNAPSHOT = ROOT / \"tests\" / \"fixtures\" / \"context_summary_snapshot.json\"\n\n\ndef _normalize(summary: dict[str, Any]) -> dict[str, Any]:\n    normalized = dict(summary)\n    normalized[\"ts_utc\"] = \"<generated>\"\n    return normalized\n\n\ndef test_context_summary_matches_monitor_only_snapshot():\n    summary = build_context_summary(\n        data_quality={\n            \"symbol\": \"XAUUSD\",\n            \"present_timeframes\": [\"M5\", \"M15\", \"H1\"],\n            \"freshness_score\": 1.0,\n            \"spread_stability\": 0.95,\n            \"confidence_cap\": 0.75,\n            \"errors\": [],\n            \"quality_flags\": [\"USD_HIGH_IMPACT_EVENT_PRESENT\"],\n        },\n        composite={\n            \"median_latest_close\": 2338.83,\n            \"latest_by_timeframe\": {},\n            \"bars\": [],\n        },\n        session={\n            \"session_ranges\": {\n                \"OFF_SESSION\": {\"high\": 2344.2, \"low\": 2337.15},\n                \"ASIA\": {\"high\": 2348.0, \"low\": 2328.0},\n            },\n        },\n        event={\n            \"risk_state\": \"CONTEXT\",\n            \"event_count\": 1,\n            \"near_high_impact_events\": [],\n            \"quality_flags\": [\"USD_HIGH_IMPACT_EVENT_PRESENT\"],\n        },\n        artifact_quality={\n            \"status\": \"OK\",\n            \"quality_grade\": \"A\",\n            \"confidence_cap\": 0.75,\n        },\n    )\n\n    actual = _normalize(summary)\n    expected = json.loads(SNAPSHOT.read_text(encoding=\"utf-8\"))\n\n    assert actual == expected\n    assert actual[\"monitor_only\"] is True\n    assert_clean_language(actual)\n""",
)

print("Applied v2.5.1 context-summary snapshot coverage.")
