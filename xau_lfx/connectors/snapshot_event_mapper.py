from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from xau_lfx.validation.event_log import EXPECTED_COLUMNS, validate_event_log


def _load_json(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload must be an object: {json_path}")
    return payload


def _snapshot_rows(snapshot: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    timeframe = str(snapshot.get("timeframe") or "").upper()
    ohlcv = snapshot.get("payload", {}).get("ohlcv", {})
    if not isinstance(ohlcv, dict):
        raise ValueError("snapshot payload.ohlcv must be an object")
    if not timeframe and len(ohlcv) == 1:
        timeframe = str(next(iter(ohlcv))).upper()
    if not timeframe:
        raise ValueError("snapshot timeframe is missing")
    rows = ohlcv.get(timeframe, [])
    if not isinstance(rows, list):
        raise ValueError(f"snapshot payload.ohlcv.{timeframe} must be a list")
    return timeframe, [row for row in rows if isinstance(row, dict)]


def _event_id(source_id: str, timeframe: str, ts_utc: str) -> str:
    safe_ts = ts_utc.replace(":", "").replace("+", "Z").replace("-", "").replace(".", "")
    return f"snapshot-{source_id.lower()}-{timeframe.lower()}-{safe_ts}"


def _base_event_row(snapshot: dict[str, Any], candle: dict[str, Any], timeframe: str) -> dict[str, Any]:
    source_id = str(snapshot.get("source_id") or candle.get("source_id") or "UNKNOWN")
    source_type = str(snapshot.get("source_type") or candle.get("source_type") or "UNKNOWN")
    ts_utc = str(candle.get("ts_utc") or "")
    symbol = str(snapshot.get("symbol") or candle.get("symbol") or "XAUUSD")
    notes = "; ".join(
        [
            f"source_id={source_id}",
            f"source_type={source_type}",
            "monitor_only=true",
            "draft_from_validated_ohlcv_snapshot",
            "no_lifecycle_inference",
        ]
    )
    row: dict[str, Any] = {column: "" for column in EXPECTED_COLUMNS}
    row.update(
        {
            "event_id": _event_id(source_id, timeframe, ts_utc),
            "ts_utc": ts_utc,
            "symbol": symbol,
            "broker_source": source_id,
            "timeframe": timeframe,
            "session": "UNKNOWN",
            "manual_news_block": "false",
            "spread_state": "UNKNOWN",
            "dashboard_state": "SNAPSHOT_ONLY",
            "trader_mode": "OBSERVE_ONLY",
            "sweep_side": "NONE",
            "lifecycle_state": "NO_SWEEP",
            "route_dir": "NONE",
            "delivery_state": "D_NONE",
            "terminal_state": "OPEN",
            "target_hit": "false",
            "route_failed": "false",
            "review_notes": notes,
        }
    )
    return row


def build_event_log_draft_from_snapshot(snapshot_path: str | Path, validation_path: str | Path) -> dict[str, Any]:
    """Build draft v9 event-log rows from a validated normalized OHLCV snapshot.

    This mapper preserves source metadata and creates schema-compatible rows without lifecycle inference.
    """

    validation = _load_json(validation_path)
    if validation.get("status") != "OK":
        return {
            "status": "ERROR",
            "snapshot_path": str(snapshot_path),
            "validation_path": str(validation_path),
            "errors": ["snapshot validation status must be OK before mapping"],
            "warnings": [],
            "rows": [],
            "monitor_only": True,
        }
    snapshot = _load_json(snapshot_path)
    if snapshot.get("monitor_only") is not True:
        return {
            "status": "ERROR",
            "snapshot_path": str(snapshot_path),
            "validation_path": str(validation_path),
            "errors": ["snapshot must preserve monitor_only=true"],
            "warnings": [],
            "rows": [],
            "monitor_only": True,
        }
    timeframe, candles = _snapshot_rows(snapshot)
    rows = [_base_event_row(snapshot, candle, timeframe) for candle in candles]
    return {
        "status": "OK" if rows else "WARN",
        "snapshot_path": str(snapshot_path),
        "validation_path": str(validation_path),
        "source_id": snapshot.get("source_id"),
        "source_type": snapshot.get("source_type"),
        "symbol": snapshot.get("symbol"),
        "timeframe": timeframe,
        "row_count": len(rows),
        "rows": rows,
        "errors": [],
        "warnings": [] if rows else ["NO_ROWS_MAPPED"],
        "monitor_only": True,
        "lifecycle_inference": "NO",
    }


def write_event_log_draft(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "snapshot_event_log_draft.csv"
    json_path = output_dir / "snapshot_event_log_draft.json"
    validation_path = output_dir / "snapshot_event_log_validation.json"

    rows = result.get("rows", [])
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in EXPECTED_COLUMNS})

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    validation = validate_event_log(csv_path)
    validation_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"csv": str(csv_path), "json": str(json_path), "validation": str(validation_path)}
