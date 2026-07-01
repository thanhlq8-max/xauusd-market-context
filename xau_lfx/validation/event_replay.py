from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from xau_lfx.engines.compact_lifecycle import Candle, LiquidityLevel, build_lifecycle_snapshot
from xau_lfx.validation.event_log import validate_event_log

REQUIRED_REPLAY_COLUMNS: tuple[str, ...] = (
    "open",
    "high",
    "low",
    "close",
    "atr",
    "trigger_source",
    "trigger_price",
    "trigger_side",
)

OPTIONAL_TARGET_COLUMNS: tuple[str, ...] = (
    "target_source",
    "target_price",
    "target_side",
    "target_score",
)


def _cell(row: dict[str, str], column: str) -> str:
    return (row.get(column) or "").strip()


def _parse_float(row: dict[str, str], column: str, row_number: int, errors: list[str]) -> float | None:
    value = _cell(row, column)
    if value == "":
        errors.append(f"row {row_number}: {column} is required")
        return None
    try:
        return float(value)
    except ValueError:
        errors.append(f"row {row_number}: {column} must be numeric")
        return None


def _parse_optional_float(row: dict[str, str], column: str, row_number: int, errors: list[str]) -> float | None:
    value = _cell(row, column)
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        errors.append(f"row {row_number}: {column} must be numeric")
        return None


def _parse_int(row: dict[str, str], column: str, row_number: int, errors: list[str]) -> int:
    value = _cell(row, column)
    if value == "":
        return 0
    try:
        parsed = int(value)
    except ValueError:
        errors.append(f"row {row_number}: {column} must be an integer")
        return 0
    if parsed < 0:
        errors.append(f"row {row_number}: {column} must be non-negative")
        return 0
    return parsed


def _load_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        headers = [header.strip() for header in (reader.fieldnames or [])]
    return rows, headers


def _build_candle(row: dict[str, str], row_number: int, errors: list[str]) -> Candle | None:
    open_ = _parse_float(row, "open", row_number, errors)
    high = _parse_float(row, "high", row_number, errors)
    low = _parse_float(row, "low", row_number, errors)
    close = _parse_float(row, "close", row_number, errors)
    atr = _parse_float(row, "atr", row_number, errors)
    tick_activity = _parse_optional_float(row, "tick_activity", row_number, errors) or 0.0
    if None in {open_, high, low, close, atr}:
        return None
    if high is not None and low is not None and high < low:
        errors.append(f"row {row_number}: high must be greater than or equal to low")
        return None
    if atr is not None and atr <= 0:
        errors.append(f"row {row_number}: atr must be positive")
        return None
    return Candle(open=float(open_), high=float(high), low=float(low), close=float(close), atr=float(atr), tick_activity=tick_activity)


def _build_trigger(row: dict[str, str], row_number: int, errors: list[str]) -> LiquidityLevel | None:
    price = _parse_float(row, "trigger_price", row_number, errors)
    score = _parse_optional_float(row, "trigger_score", row_number, errors)
    if price is None:
        return None
    return LiquidityLevel(
        source=_cell(row, "trigger_source") or _cell(row, "sweep_source") or "UNKNOWN",
        price=price,
        side=(_cell(row, "trigger_side") or _cell(row, "sweep_side") or "NONE").upper(),
        score=1.0 if score is None else score,
    )


def _build_targets(row: dict[str, str], row_number: int, errors: list[str]) -> list[LiquidityLevel]:
    target_price = _parse_optional_float(row, "target_price", row_number, errors)
    if target_price is None:
        target_price = _parse_optional_float(row, "target_ref", row_number, errors)
    if target_price is None:
        return []
    score = _parse_optional_float(row, "target_score", row_number, errors)
    target_source = _cell(row, "target_source") or _cell(row, "zone_role") or "TARGET"
    target_side = (_cell(row, "target_side") or _cell(row, "route_dir") or "NONE").upper()
    return [
        LiquidityLevel(
            source=target_source,
            price=target_price,
            side=target_side,
            score=1.0 if score is None else score,
        )
    ]


def _row_result(
    row: dict[str, str],
    row_number: int,
    errors: list[str],
) -> dict[str, Any] | None:
    candle = _build_candle(row, row_number, errors)
    trigger = _build_trigger(row, row_number, errors)
    if candle is None or trigger is None:
        return None
    targets = _build_targets(row, row_number, errors)
    flow_skew = _parse_optional_float(row, "flow_skew", row_number, errors) or 0.0
    route_age_bars = _parse_int(row, "route_age_bars", row_number, errors)
    if errors:
        return None

    snapshot = build_lifecycle_snapshot(
        candle=candle,
        trigger_level=trigger,
        target_levels=targets,
        flow_skew=flow_skew,
        route_age_bars=route_age_bars,
    )
    actual_lifecycle = str(snapshot.lifecycle.get("state", ""))
    actual_delivery = str(snapshot.delivery.get("state", ""))
    expected_lifecycle = _cell(row, "expected_lifecycle_state") or _cell(row, "lifecycle_state")
    expected_delivery = _cell(row, "expected_delivery_state") or _cell(row, "delivery_state")
    lifecycle_match = actual_lifecycle == expected_lifecycle
    delivery_match = actual_delivery == expected_delivery
    return {
        "event_id": _cell(row, "event_id"),
        "row_number": row_number,
        "expected_lifecycle_state": expected_lifecycle,
        "actual_lifecycle_state": actual_lifecycle,
        "lifecycle_match": lifecycle_match,
        "expected_delivery_state": expected_delivery,
        "actual_delivery_state": actual_delivery,
        "delivery_match": delivery_match,
        "route_dir": snapshot.route.get("route_dir"),
        "target_ref": snapshot.route.get("target_ref"),
        "monitor_only": True,
    }


def replay_event_log(path: str | Path) -> dict[str, Any]:
    """Replay a v9 event log through compact lifecycle primitives.

    The replay harness validates schema compatibility first, then compares expected
    lifecycle and delivery states against deterministic compact-engine output.
    It does not connect to live feeds and does not infer trade actions.
    """

    csv_path = Path(path)
    validation = validate_event_log(csv_path)
    errors: list[str] = list(validation.get("errors", []))
    warnings: list[str] = list(validation.get("warnings", []))
    if validation.get("status") == "ERROR":
        return {
            "status": "ERROR",
            "path": str(csv_path),
            "rows_checked": 0,
            "matches": 0,
            "mismatches": 0,
            "errors": errors,
            "warnings": warnings,
            "results": [],
            "monitor_only": True,
        }

    try:
        rows, headers = _load_rows(csv_path)
    except csv.Error as exc:
        return {
            "status": "ERROR",
            "path": str(csv_path),
            "rows_checked": 0,
            "matches": 0,
            "mismatches": 0,
            "errors": [f"CSV parser error: {exc}"],
            "warnings": warnings,
            "results": [],
            "monitor_only": True,
        }

    missing_replay = [column for column in REQUIRED_REPLAY_COLUMNS if column not in set(headers)]
    if missing_replay:
        errors.append("missing replay columns: " + ", ".join(missing_replay))

    results: list[dict[str, Any]] = []
    if not errors:
        for index, row in enumerate(rows, start=2):
            row_errors: list[str] = []
            result = _row_result(row, index, row_errors)
            errors.extend(row_errors)
            if result is not None:
                results.append(result)

    mismatches = [result for result in results if not result["lifecycle_match"] or not result["delivery_match"]]
    matches = len(results) - len(mismatches)
    status = "ERROR" if errors else ("MISMATCH" if mismatches else ("WARN" if warnings else "OK"))
    return {
        "status": status,
        "path": str(csv_path),
        "rows_checked": len(rows),
        "matches": matches,
        "mismatches": len(mismatches),
        "errors": errors,
        "warnings": warnings,
        "results": results,
        "monitor_only": True,
    }


def write_replay_report(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "event_replay_report.json"
    md_path = output_dir / "event_replay_report.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Event Replay Report",
        "",
        f"STATUS: {result.get('status')}",
        f"ROWS_CHECKED: {result.get('rows_checked')}",
        f"MATCHES: {result.get('matches')}",
        f"MISMATCHES: {result.get('mismatches')}",
        "MONITOR_ONLY: YES",
        "",
        "| event_id | lifecycle | delivery |",
        "|---|---|---|",
    ]
    for row in result.get("results", []):
        lifecycle = f"{row.get('expected_lifecycle_state')} => {row.get('actual_lifecycle_state')}"
        delivery = f"{row.get('expected_delivery_state')} => {row.get('actual_delivery_state')}"
        lines.append(f"| {row.get('event_id')} | {lifecycle} | {delivery} |")
    if result.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    if result.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result["warnings"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
