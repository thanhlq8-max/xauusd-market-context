from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from xau_lfx.validation.node_graph_replay import build_node_graph_from_replay


def _cell(row: dict[str, str], column: str) -> str:
    return (row.get(column) or "").strip()


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _index_by_event_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("event_id", "")): item for item in items if item.get("event_id")}


def _cluster_for_node(node_id: str, clusters: list[dict[str, Any]]) -> dict[str, Any] | None:
    for cluster in clusters:
        node_ids = cluster.get("node_ids", [])
        if node_id in node_ids:
            return cluster
    return None


def _case_quality(row: dict[str, str], update: dict[str, Any] | None, cluster: dict[str, Any] | None) -> str:
    review = (_cell(row, "manual_review_result") or "").upper()
    if review == "WRONG":
        return "REJECT"
    if review in {"PARTIAL", "UNCLEAR"}:
        return "REVIEW"
    node_score = float(update.get("score_after", 0.0)) if update else 0.0
    cluster_score = float(cluster.get("score", 0.0)) if cluster else 0.0
    if node_score >= 0.65 or cluster_score >= 0.65:
        return "STRONG"
    if node_score >= 0.45 or cluster_score >= 0.45:
        return "VALID"
    return "WEAK"


def build_case_library_from_replay(path: str | Path, cluster_band: float = 1.0) -> dict[str, Any]:
    """Build a monitor-only case library seed from a replay event log.

    Cases are descriptive evidence summaries. They do not infer trade entries,
    position sizing, profitability, real inventory, or real positioning.
    """

    csv_path = Path(path)
    node_report = build_node_graph_from_replay(csv_path, cluster_band=cluster_band)
    if node_report.get("status") == "ERROR":
        return {
            "status": "ERROR",
            "path": str(csv_path),
            "errors": ["node graph report must pass before case library build"],
            "node_graph_status": node_report.get("status"),
            "cases": [],
            "monitor_only": True,
        }

    rows = _load_rows(csv_path)
    updates_by_event = _index_by_event_id(list(node_report.get("updates", [])))
    clusters = list(node_report.get("clusters", []))
    cases: list[dict[str, Any]] = []

    for index, row in enumerate(rows, start=2):
        event_id = _cell(row, "event_id") or f"row-{index}"
        update = updates_by_event.get(event_id)
        cluster = _cluster_for_node(str(update.get("node_id", "")), clusters) if update else None
        case = {
            "case_id": f"CASE:{event_id}",
            "event_id": event_id,
            "ts_utc": _cell(row, "ts_utc"),
            "symbol": _cell(row, "symbol"),
            "timeframe": _cell(row, "timeframe"),
            "session": _cell(row, "session"),
            "source": _cell(row, "trigger_source") or _cell(row, "sweep_source"),
            "side": _cell(row, "trigger_side") or _cell(row, "sweep_side"),
            "lifecycle_state": _cell(row, "lifecycle_state"),
            "delivery_state": _cell(row, "delivery_state"),
            "terminal_state": _cell(row, "terminal_state"),
            "node_id": update.get("node_id") if update else None,
            "node_reaction": update.get("reaction") if update else None,
            "node_score_after": update.get("score_after") if update else None,
            "cluster_id": cluster.get("cluster_id") if cluster else None,
            "cluster_score": cluster.get("score") if cluster else None,
            "manual_review_result": _cell(row, "manual_review_result"),
            "quality_label": _case_quality(row, update, cluster),
            "review_notes": _cell(row, "review_notes"),
            "monitor_only": True,
        }
        cases.append(case)

    quality_counts: dict[str, int] = {}
    for case in cases:
        quality = str(case.get("quality_label", "UNKNOWN"))
        quality_counts[quality] = quality_counts.get(quality, 0) + 1

    return {
        "status": "WARN" if node_report.get("status") == "WARN" else "OK",
        "path": str(csv_path),
        "node_graph_status": node_report.get("status"),
        "case_count": len(cases),
        "quality_counts": quality_counts,
        "cases": cases,
        "monitor_only": True,
    }


def write_case_library(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "case_library_seed.json"
    md_path = output_dir / "case_library_seed.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Case Library Seed",
        "",
        f"STATUS: {result.get('status')}",
        f"NODE_GRAPH_STATUS: {result.get('node_graph_status')}",
        f"CASE_COUNT: {result.get('case_count')}",
        "MONITOR_ONLY: YES",
        "",
        "| case_id | source | lifecycle | delivery | node_score | cluster | quality |",
        "|---|---|---|---|---:|---|---|",
    ]
    for case in result.get("cases", []):
        lines.append(
            "| {case_id} | {source} | {lifecycle_state} | {delivery_state} | {node_score_after} | {cluster_id} | {quality_label} |".format(
                **case
            )
        )
    if result.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
