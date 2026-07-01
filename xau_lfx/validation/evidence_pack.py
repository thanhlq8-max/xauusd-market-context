from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REVIEW_GROUP_ORDER = ("ACCEPTED", "NEEDS_DATA", "REJECTED", "REVIEWED", "NEW")


def _load_case_index(path: str | Path) -> dict[str, Any]:
    index_path = Path(path)
    with index_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("case index payload must be a JSON object")
    return payload


def _empty_result(path: str | Path, error: str) -> dict[str, Any]:
    return {
        "status": "ERROR",
        "path": str(path),
        "errors": [error],
        "group_count": 0,
        "case_count": 0,
        "groups": {},
        "review_checklist": [],
        "monitor_only": True,
    }


def _case_summary(case: dict[str, Any]) -> dict[str, Any]:
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
        "quality_label": case.get("quality_label"),
        "review_status": case.get("review_status"),
        "review_priority": case.get("review_priority"),
        "node_id": case.get("node_id"),
        "cluster_id": case.get("cluster_id"),
        "review_notes": case.get("review_notes") or "",
        "reviewer_notes": case.get("reviewer_notes") or "",
        "monitor_only": True,
    }


def _build_group(cases: list[dict[str, Any]]) -> dict[str, Any]:
    sorted_cases = sorted(
        cases,
        key=lambda case: (
            0 if case.get("review_priority") == "HIGH" else 1 if case.get("review_priority") == "MEDIUM" else 2,
            str(case.get("ts_utc") or ""),
            str(case.get("case_id") or ""),
        ),
    )
    return {
        "case_count": len(sorted_cases),
        "high_priority_count": sum(1 for case in sorted_cases if case.get("review_priority") == "HIGH"),
        "cases": [_case_summary(case) for case in sorted_cases],
        "monitor_only": True,
    }


def _review_checklist(groups: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "item": "Review NEEDS_DATA cases first and attach missing screenshot/session context.",
            "target_group": "NEEDS_DATA",
            "required": groups.get("NEEDS_DATA", {}).get("case_count", 0) > 0,
            "monitor_only": True,
        },
        {
            "item": "Confirm ACCEPTED cases have matching lifecycle and delivery evidence before using them as examples.",
            "target_group": "ACCEPTED",
            "required": groups.get("ACCEPTED", {}).get("case_count", 0) > 0,
            "monitor_only": True,
        },
        {
            "item": "Keep REJECTED cases as negative examples and do not promote them into reference cases.",
            "target_group": "REJECTED",
            "required": groups.get("REJECTED", {}).get("case_count", 0) > 0,
            "monitor_only": True,
        },
        {
            "item": "Leave NEW cases unchanged until manual review adds a status or notes.",
            "target_group": "NEW",
            "required": groups.get("NEW", {}).get("case_count", 0) > 0,
            "monitor_only": True,
        },
    ]


def build_evidence_pack(path: str | Path) -> dict[str, Any]:
    """Build an offline monitor-only evidence pack from a case review index."""

    payload = _load_case_index(path)
    if payload.get("monitor_only") is not True:
        return _empty_result(path, "case index must preserve monitor_only=true")
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        return _empty_result(path, "case index cases must be a list")

    grouped: dict[str, list[dict[str, Any]]] = {status: [] for status in REVIEW_GROUP_ORDER}
    for case in cases:
        if not isinstance(case, dict):
            continue
        status = str(case.get("review_status") or "NEW").upper()
        if status not in grouped:
            status = "NEW"
        grouped[status].append(case)

    groups = {status: _build_group(items) for status, items in grouped.items() if items}
    return {
        "status": "OK",
        "path": str(path),
        "case_count": sum(group["case_count"] for group in groups.values()),
        "group_count": len(groups),
        "groups": groups,
        "review_checklist": _review_checklist(groups),
        "monitor_only": True,
    }


def write_evidence_pack(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "evidence_pack.json"
    md_path = output_dir / "evidence_pack.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Case Review Evidence Pack",
        "",
        f"STATUS: {result.get('status')}",
        f"CASE_COUNT: {result.get('case_count')}",
        f"GROUP_COUNT: {result.get('group_count')}",
        "MONITOR_ONLY: YES",
        "",
    ]
    for status in REVIEW_GROUP_ORDER:
        group = result.get("groups", {}).get(status)
        if not group:
            continue
        lines.extend(
            [
                f"## {status}",
                "",
                f"CASE_COUNT: {group.get('case_count')}",
                f"HIGH_PRIORITY_COUNT: {group.get('high_priority_count')}",
                "",
                "| case_id | source | lifecycle | delivery | quality | priority |",
                "|---|---|---|---|---|---|",
            ]
        )
        for case in group.get("cases", []):
            lines.append(
                "| {case_id} | {source} | {lifecycle_state} | {delivery_state} | {quality_label} | {review_priority} |".format(
                    **case
                )
            )
        lines.append("")
    lines.extend(["## Review Checklist", ""])
    for item in result.get("review_checklist", []):
        required = "required" if item.get("required") else "optional"
        lines.append(f"- [{required}] {item.get('item')}")
    if result.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
