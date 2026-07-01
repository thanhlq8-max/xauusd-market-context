from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from xau_lfx.engines.liquidity_nodes import (
    REACTION_ACCEPT,
    REACTION_FAIL,
    REACTION_RECLAIM,
    REACTION_REJECT,
    REACTION_SWEEP,
    REACTION_TOUCH,
    LiquidityNode,
    NodeReaction,
    cluster_nodes,
    create_liquidity_node,
    serialize_cluster,
    serialize_node,
    update_node_reaction,
)
from xau_lfx.validation.event_replay import replay_event_log


def _cell(row: dict[str, str], column: str) -> str:
    return (row.get(column) or "").strip()


def _parse_float(value: str) -> float | None:
    if value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _reaction_from_row(row: dict[str, str]) -> str:
    delivery_state = (_cell(row, "delivery_state") or _cell(row, "expected_delivery_state")).upper()
    lifecycle_state = (_cell(row, "lifecycle_state") or _cell(row, "expected_lifecycle_state")).upper()
    if delivery_state == "D_FAILED" or lifecycle_state.endswith("_FAIL"):
        return REACTION_FAIL
    if lifecycle_state == "RECLAIM":
        return REACTION_RECLAIM
    if lifecycle_state == "ACCEPT":
        return REACTION_ACCEPT
    if lifecycle_state == "REJECT":
        return REACTION_REJECT
    if lifecycle_state == "RAW_SPIKE":
        return REACTION_SWEEP
    return REACTION_TOUCH


def _node_source(row: dict[str, str]) -> str:
    return _cell(row, "trigger_source") or _cell(row, "sweep_source") or "UNKNOWN"


def _node_price(row: dict[str, str]) -> float | None:
    return _parse_float(_cell(row, "trigger_price")) or _parse_float(_cell(row, "sweep_level"))


def _node_side(row: dict[str, str]) -> str:
    return (_cell(row, "trigger_side") or _cell(row, "sweep_side") or "NONE").upper()


def _node_score(row: dict[str, str]) -> float:
    score = _parse_float(_cell(row, "trigger_score"))
    if score is None:
        score = _parse_float(_cell(row, "sweep_score"))
    return 0.0 if score is None else score


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_node_graph_from_replay(
    path: str | Path,
    cluster_band: float = 1.0,
) -> dict[str, Any]:
    """Build a monitor-only liquidity-node report from a replay event log.

    The event log is replayed through compact lifecycle validation first. Node
    updates are derived from the logged lifecycle/delivery states. The report is
    descriptive and does not infer order placement, position sizing, or PnL.
    """

    csv_path = Path(path)
    replay_result = replay_event_log(csv_path)
    if replay_result.get("status") in {"ERROR", "MISMATCH"}:
        return {
            "status": "ERROR",
            "path": str(csv_path),
            "errors": ["event replay must pass before node graph build"],
            "replay_status": replay_result.get("status"),
            "nodes": [],
            "clusters": [],
            "monitor_only": True,
        }

    rows = _load_rows(csv_path)
    nodes: dict[str, LiquidityNode] = {}
    errors: list[str] = []
    updates: list[dict[str, Any]] = []

    for index, row in enumerate(rows, start=2):
        price = _node_price(row)
        if price is None:
            errors.append(f"row {index}: missing trigger_price/sweep_level for node graph")
            continue
        source = _node_source(row)
        side = _node_side(row)
        score = _node_score(row)
        node = create_liquidity_node(
            source=source,
            price=price,
            side=side,
            ts_utc=_cell(row, "ts_utc") or None,
            score=score,
        )
        existing = nodes.get(node.node_id, node)
        reaction_type = _reaction_from_row(row)
        reaction = NodeReaction(
            node_id=existing.node_id,
            reaction=reaction_type,
            ts_utc=_cell(row, "ts_utc") or None,
            price=price,
            timeframe=_cell(row, "timeframe") or None,
            session=_cell(row, "session") or None,
            notes=_cell(row, "event_id"),
        )
        updated = update_node_reaction(existing, reaction)
        nodes[updated.node_id] = updated
        updates.append(
            {
                "event_id": _cell(row, "event_id"),
                "node_id": updated.node_id,
                "reaction": reaction_type,
                "score_after": updated.score,
                "monitor_only": True,
            }
        )

    node_list = sorted(nodes.values(), key=lambda item: (-item.score, item.price, item.node_id))
    clusters = cluster_nodes(node_list, cluster_band) if node_list else []
    status = "ERROR" if errors else ("WARN" if replay_result.get("status") == "WARN" else "OK")
    return {
        "status": status,
        "path": str(csv_path),
        "replay_status": replay_result.get("status"),
        "rows_checked": len(rows),
        "node_count": len(node_list),
        "cluster_count": len(clusters),
        "errors": errors,
        "warnings": list(replay_result.get("warnings", [])),
        "updates": updates,
        "nodes": [serialize_node(node) for node in node_list],
        "clusters": [serialize_cluster(cluster) for cluster in clusters],
        "monitor_only": True,
    }


def write_node_graph_report(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "node_graph_report.json"
    md_path = output_dir / "node_graph_report.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Liquidity Node Graph Report",
        "",
        f"STATUS: {result.get('status')}",
        f"REPLAY_STATUS: {result.get('replay_status')}",
        f"ROWS_CHECKED: {result.get('rows_checked')}",
        f"NODE_COUNT: {result.get('node_count')}",
        f"CLUSTER_COUNT: {result.get('cluster_count')}",
        "MONITOR_ONLY: YES",
        "",
        "## Nodes",
        "",
        "| node_id | source | side | price | score | touch | sweep | reclaim | accept | reject | fail |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for node in result.get("nodes", []):
        lines.append(
            "| {node_id} | {source} | {side} | {price} | {score} | {touch_count} | {sweep_count} | {reclaim_count} | {accept_count} | {reject_count} | {fail_count} |".format(
                **node
            )
        )
    lines.extend(
        [
            "",
            "## Clusters",
            "",
            "| cluster_id | center | lower | upper | score | node_count |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for cluster in result.get("clusters", []):
        lines.append(
            "| {cluster_id} | {center_price} | {lower_price} | {upper_price} | {score} | {node_count} |".format(
                **cluster
            )
        )
    if result.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    if result.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result["warnings"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
