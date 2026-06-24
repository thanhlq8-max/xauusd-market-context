from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from xau_lfx.config import artifact_paths
from xau_lfx.forbidden_language import assert_clean_language


ARTIFACT_CONTRACT_VERSION = "1.0.0"

ARTIFACT_REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "raw_scan": ("ts_utc", "symbol", "monitor_only", "source_payloads"),
    "data_quality": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "freshness_score",
        "coverage_score",
        "schema_score",
        "source_count",
        "confidence_cap",
        "present_timeframes",
        "errors",
        "quality_flags",
    ),
    "composite_ohlcv": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "timeframes",
        "primary_timeframe",
        "bars",
    ),
    "session_context": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "session_state",
        "primary_timeframe",
        "session_ranges",
        "confidence_cap",
        "quality_flags",
    ),
    "macro_pressure": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "pressure_state",
        "drivers",
        "confidence_cap",
        "quality_flags",
    ),
    "event_risk": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "risk_state",
        "event_count",
        "high_impact_events",
        "near_high_impact_events",
        "confidence_cap",
        "quality_flags",
    ),
    "state": ("ts_utc", "symbol", "monitor_only", "state", "summary", "evidence", "quality"),
    "user_insight": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "headline",
        "now_read",
        "operator_focus",
        "evidence_map",
        "useful_limits",
        "upgrade_requirements",
        "quality_flags",
    ),
    "artifact_quality": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "status",
        "quality_score",
        "quality_grade",
        "source_count",
        "warnings",
        "errors",
        "confidence_cap",
    ),
    "context_summary": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "latest_close",
        "spread_state",
        "event_risk_state",
        "quality_status",
        "quality_grade",
        "confidence_cap",
        "confidence_explanation",
        "monitor_focus",
        "limitations",
        "quality_flags",
    ),
}


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name}: invalid JSON at line {exc.lineno} column {exc.colno}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name}: top-level JSON value must be an object")
    return payload


def validate_artifact_contract(artifact_dir: str | Path) -> dict[str, Any]:
    paths = artifact_paths(artifact_dir)
    errors: list[str] = []
    checked_artifacts: list[dict[str, Any]] = []

    for artifact_key, required_keys in ARTIFACT_REQUIRED_KEYS.items():
        path = paths[artifact_key]
        checked = {
            "artifact_key": artifact_key,
            "file": path.name,
            "required_keys": list(required_keys),
            "missing_keys": [],
        }
        checked_artifacts.append(checked)

        if not path.exists():
            errors.append(f"{path.name}: missing artifact")
            continue

        try:
            payload = _read_json_object(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        missing_keys = [key for key in required_keys if key not in payload]
        checked["missing_keys"] = missing_keys
        if missing_keys:
            errors.append(f"{path.name}: missing required keys: {', '.join(missing_keys)}")
        if payload.get("monitor_only") is not True:
            errors.append(f"{path.name}: monitor_only must be true")

    result = {
        "schema_contract_version": ARTIFACT_CONTRACT_VERSION,
        "status": "ERROR" if errors else "OK",
        "artifact_dir": str(Path(artifact_dir)),
        "checked_artifact_count": len(checked_artifacts),
        "checked_artifacts": checked_artifacts,
        "errors": errors,
    }
    assert_clean_language(result)
    return result
