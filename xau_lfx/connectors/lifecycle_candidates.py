from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from xau_lfx.validation.event_log import validate_event_log

CANDIDATE_STATE = "NEEDS_MANUAL_REVIEW"


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("quality report must be a JSON object")
    return payload


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _candidate_id(row: dict[str, str]) -> str:
    raw = f"{row.get('event_id', '')}:{row.get('ts_utc', '')}:{row.get('broker_source', '')}:{row.get('timeframe', '')}"
    safe = raw.replace(":", "").replace("+", "Z").replace(" ", "_").replace("/", "_")
    return f"LCAND:{safe}"


def _candidate(row: dict[str, str]) -> dict[str, Any]:
    evidence = [
        f"event_id={row.get('event_id', '')}",
        f"source={row.get('broker_source', '')}",
        f"timeframe={row.get('timeframe', '')}",
        f"session={row.get('session', '')}",
        f"lifecycle_state={row.get('lifecycle_state', '')}",
        f"delivery_state={row.get('delivery_state', '')}",
        "candidate_only=true",
    ]
    if row.get("dashboard_state") == "SNAPSHOT_ONLY":
        evidence.append("snapshot_only_row=true")
    if row.get("lifecycle_state") == "NO_SWEEP" and row.get("delivery_state") == "D_NONE":
        evidence.append("no_lifecycle_inference=true")
    return {
        "candidate_id": _candidate_id(row),
        "event_id": row.get("event_id", ""),
        "ts_utc": row.get("ts_utc", ""),
        "symbol": row.get("symbol", ""),
        "broker_source": row.get("broker_source", ""),
        "timeframe": row.get("timeframe", ""),
        "candidate_state": CANDIDATE_STATE,
        "candidate_reference": "NONE",
        "candidate_evidence": evidence,
        "required_review": True,
        "source_lifecycle_state": row.get("lifecycle_state", ""),
        "source_delivery_state": row.get("delivery_state", ""),
        "monitor_only": True,
    }


def build_lifecycle_candidates(*, dataset_csv: str | Path, quality_json: str | Path) -> dict[str, Any]:
    dataset_validation = validate_event_log(dataset_csv)
    if dataset_validation.get("status") != "OK":
        return {
            "status": "ERROR",
            "dataset_csv": str(dataset_csv),
            "quality_json": str(quality_json),
            "errors": ["rolling dataset validation must be OK before candidate build"],
            "warnings": list(dataset_validation.get("warnings", [])),
            "candidate_count": 0,
            "candidates": [],
            "monitor_only": True,
            "dataset_mutated": False,
        }
    quality = _load_json(quality_json)
    if quality.get("status") != "OK":
        return {
            "status": "ERROR",
            "dataset_csv": str(dataset_csv),
            "quality_json": str(quality_json),
            "errors": ["rolling dataset quality status must be OK before candidate build"],
            "warnings": list(quality.get("warnings", [])),
            "candidate_count": 0,
            "candidates": [],
            "monitor_only": True,
            "dataset_mutated": False,
        }
    candidates = [_candidate(row) for row in _read_rows(dataset_csv)]
    counts = Counter(candidate["candidate_state"] for candidate in candidates)
    return {
        "status": "OK" if candidates else "WARN",
        "dataset_csv": str(dataset_csv),
        "quality_json": str(quality_json),
        "candidate_count": len(candidates),
        "candidate_state_counts": dict(sorted(counts.items())),
        "candidates": candidates,
        "errors": [],
        "warnings": [] if candidates else ["NO_CANDIDATES_BUILT"],
        "monitor_only": True,
        "dataset_mutated": False,
        "lifecycle_field_overwrite": "NO",
    }


def write_lifecycle_candidates(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "lifecycle_candidates.json"
    md_path = output_dir / "lifecycle_candidates.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Lifecycle Candidates",
        "",
        f"STATUS: {result.get('status')}",
        f"CANDIDATE_COUNT: {result.get('candidate_count')}",
        "MONITOR_ONLY: YES",
        f"DATASET_MUTATED: {result.get('dataset_mutated', False)}",
        f"LIFECYCLE_FIELD_OVERWRITE: {result.get('lifecycle_field_overwrite', 'NO')}",
        "",
    ]
    counts = result.get("candidate_state_counts", {})
    if counts:
        lines.extend(["## Candidate State Counts", ""])
        lines.extend(f"- {state}: {count}" for state, count in counts.items())
        lines.append("")
    if result.get("errors"):
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
