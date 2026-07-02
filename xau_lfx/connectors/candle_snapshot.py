from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from xau_lfx.utils import utc_now_iso

ALLOWED_SOURCE_STATUS = {"OK", "WARN"}
DEFAULT_MAX_AGE_SECONDS = {"M1": 180.0, "M5": 600.0, "M15": 1800.0, "H1": 7200.0}


class CandleSnapshotValidationError(ValueError):
    pass


def _load_snapshot(path: str | Path) -> dict[str, Any]:
    snapshot_path = Path(path)
    with snapshot_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise CandleSnapshotValidationError("snapshot payload must be a JSON object")
    return payload


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise CandleSnapshotValidationError(f"timestamp has no timezone: {value}")
    return parsed.astimezone(timezone.utc)


def _rows(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    timeframe = str(payload.get("timeframe") or "").upper()
    ohlcv = payload.get("payload", {}).get("ohlcv", {})
    if not isinstance(ohlcv, dict):
        raise CandleSnapshotValidationError("payload.ohlcv must be an object")
    if not timeframe:
        if len(ohlcv) == 1:
            timeframe = str(next(iter(ohlcv))).upper()
        else:
            raise CandleSnapshotValidationError("snapshot timeframe is missing")
    rows = ohlcv.get(timeframe, [])
    if not isinstance(rows, list):
        raise CandleSnapshotValidationError(f"payload.ohlcv.{timeframe} must be a list")
    return timeframe, [row for row in rows if isinstance(row, dict)]


def _freshness_threshold(timeframe: str, max_age_seconds: float | None) -> float | None:
    if max_age_seconds is not None:
        return float(max_age_seconds)
    return DEFAULT_MAX_AGE_SECONDS.get(timeframe.upper())


def validate_ohlcv_snapshot(
    path: str | Path,
    *,
    max_age_seconds: float | None = None,
    skip_freshness_check: bool = False,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    """Validate a monitor-only normalized OHLCV snapshot before downstream review use."""

    errors: list[str] = []
    warnings: list[str] = []
    payload = _load_snapshot(path)
    source_status = str(payload.get("status") or "").upper()
    if source_status not in ALLOWED_SOURCE_STATUS:
        errors.append(f"SOURCE_STATUS_NOT_ALLOWED: {source_status or 'MISSING'}")
    elif source_status == "WARN":
        warnings.append("SOURCE_STATUS_WARN")

    if payload.get("monitor_only") is not True:
        errors.append("SNAPSHOT_MONITOR_ONLY_MISSING")

    timeframe, rows = _rows(payload)
    if not rows:
        errors.append("SNAPSHOT_HAS_NO_ROWS")

    seen_ts: set[str] = set()
    latest: datetime | None = None
    for index, row in enumerate(rows, start=1):
        if row.get("monitor_only") is not True:
            errors.append(f"ROW_{index}_MONITOR_ONLY_MISSING")
        if row.get("is_complete") is not True:
            errors.append(f"ROW_{index}_INCOMPLETE_CANDLE")
        row_timeframe = str(row.get("timeframe") or timeframe).upper()
        if row_timeframe != timeframe:
            errors.append(f"ROW_{index}_TIMEFRAME_MISMATCH")
        ts_raw = str(row.get("ts_utc") or "")
        if not ts_raw:
            errors.append(f"ROW_{index}_TS_UTC_MISSING")
            continue
        if ts_raw in seen_ts:
            errors.append(f"DUPLICATE_TS_UTC: {ts_raw}")
        seen_ts.add(ts_raw)
        try:
            parsed_ts = _parse_utc(ts_raw)
        except (ValueError, CandleSnapshotValidationError) as exc:
            errors.append(f"ROW_{index}_TS_UTC_INVALID: {exc}")
            continue
        latest = parsed_ts if latest is None or parsed_ts > latest else latest

    age_seconds = None
    threshold = None if skip_freshness_check else _freshness_threshold(timeframe, max_age_seconds)
    if latest is not None and threshold is not None:
        reference_now = now_utc or datetime.now(timezone.utc)
        if reference_now.tzinfo is None:
            reference_now = reference_now.replace(tzinfo=timezone.utc)
        reference_now = reference_now.astimezone(timezone.utc)
        age_seconds = round((reference_now - latest).total_seconds(), 3)
        if age_seconds > threshold:
            errors.append(f"SNAPSHOT_STALE: age_seconds={age_seconds}, max_age_seconds={threshold}")

    return {
        "status": "ERROR" if errors else "OK",
        "path": str(path),
        "source_status": source_status,
        "source_id": payload.get("source_id"),
        "source_type": payload.get("source_type"),
        "symbol": payload.get("symbol"),
        "timeframe": timeframe,
        "rows_checked": len(rows),
        "latest_ts_utc": latest.isoformat() if latest is not None else None,
        "max_age_seconds": threshold,
        "age_seconds": age_seconds,
        "errors": errors,
        "warnings": warnings,
        "quality_flags": payload.get("quality_flags", []),
        "ts_utc": utc_now_iso(),
        "monitor_only": True,
    }


def write_snapshot_validation(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "ohlcv_snapshot_validation.json"
    md_path = output_dir / "ohlcv_snapshot_validation.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# OHLCV Snapshot Validation",
        "",
        f"STATUS: {result.get('status')}",
        f"SOURCE_STATUS: {result.get('source_status')}",
        f"SOURCE_ID: {result.get('source_id')}",
        f"SYMBOL: {result.get('symbol')}",
        f"TIMEFRAME: {result.get('timeframe')}",
        f"ROWS_CHECKED: {result.get('rows_checked')}",
        f"LATEST_TS_UTC: {result.get('latest_ts_utc')}",
        f"MAX_AGE_SECONDS: {result.get('max_age_seconds')}",
        f"AGE_SECONDS: {result.get('age_seconds')}",
        "MONITOR_ONLY: YES",
        "",
    ]
    if result.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result["warnings"])
        lines.append("")
    if result.get("errors"):
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
