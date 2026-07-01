from __future__ import annotations

import json
from pathlib import Path
from typing import Any

VALID_REVIEW_STATUSES = {"NEW", "REVIEWED", "ACCEPTED", "REJECTED", "NEEDS_DATA"}


def _load_case_library(path: str | Path) -> dict[str, Any]:
    case_path = Path(path)
    with case_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("case library payload must be a JSON object")
    return payload


def _review_status(case: dict[str, Any]) -> str:
    explicit = str(case.get("review_status") or "").upper().strip()
    if explicit in VALID_REVIEW_STATUSES:
        return explicit
    manual = str(case.get("manual_review_result") or "").upper().strip()
    quality = str(case.get("quality_label") or "").upper().strip()
    if manual == "WRONG" or quality == "REJECT":
        return "REJECTED"
    if manual == "MATCH" and quality in {"STRONG", "VALID"}:
        return "ACCEPTED"
    if manual in {"PARTIAL", "UNCLEAR"} or quality == "REVIEW":
        return "NEEDS_DATA"
    if manual:
        return "REVIEWED"
    return "NEW"


def _case_priority(case: dict[str, Any], review_status: str) -> str:
    quality = str(case.get("quality_label") or "").upper().strip()
    if review_status == "NEEDS_DATA":
        return "HIGH"
    if review_status == "REJECTED":
        return "LOW"
    if quality == "STRONG":
        return "HIGH"
    if quality == "VALID":
        return "MEDIUM"
    return "LOW"


def _index_row(case: dict[str, Any]) -> dict[str, Any]:
    review_status = _review_status(case)
    return {
        "case_id": case.get("case_id"),
        "event_id": case.get("event_id"),
        "ts_utc": case.get("ts_utc"),
        "symbol": case.get("symbol"),
        "timeframe": case.get("timeframe"),
        "session": case.get("session"),
        "source": case.get("source"),
        "lifecycle_state": case.get("lifecycle_state"),
        "delivery_state": case.get("delivery_state"),
        "node_id": case.get("node_id"),
        "node_score_after": case.get("node_score_after"),
        "cluster_id": case.get("cluster_id"),
        "cluster_score": case.get("cluster_score"),
        "quality_label": case.get("quality_label"),
        "review_status": review_status,
        "review_priority": _case_priority(case, review_status),
        "review_notes": str(case.get("review_notes") or ""),
        "reviewer_notes": str(case.get("reviewer_notes") or ""),
        "monitor_only": True,
    }


def build_case_index(path: str | Path) -> dict[str, Any]:
    """Build an offline review index from a case-library seed artifact."""

    payload = _load_case_library(path)
    if payload.get("monitor_only") is not True:
        return {
            "status": "ERROR",
            "path": str(path),
            "errors": ["case library must preserve monitor_only=true"],
            "cases": [],
            "monitor_only": True,
        }
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        return {
            "status": "ERROR",
            "path": str(path),
            "errors": ["case library cases must be a list"],
            "cases": [],
            "monitor_only": True,
        }

    index_rows = [_index_row(case) for case in cases if isinstance(case, dict)]
    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    for row in index_rows:
        status = str(row.get("review_status") or "UNKNOWN")
        priority = str(row.get("review_priority") or "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    return {
        "status": "OK",
        "path": str(path),
        "case_count": len(index_rows),
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "cases": index_rows,
        "monitor_only": True,
    }


def write_case_index(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "case_index.json"
    md_path = output_dir / "case_index.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Case Library Review Index",
        "",
        f"STATUS: {result.get('status')}",
        f"CASE_COUNT: {result.get('case_count')}",
        "MONITOR_ONLY: YES",
        "",
        "| case_id | source | lifecycle | delivery | quality | review_status | priority |",
        "|---|---|---|---|---|---|---|",
    ]
    for case in result.get("cases", []):
        lines.append(
            "| {case_id} | {source} | {lifecycle_state} | {delivery_state} | {quality_label} | {review_status} | {review_priority} |".format(
                **case
            )
        )
    if result.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
