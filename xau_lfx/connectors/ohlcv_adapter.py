from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from xau_lfx.utils import utc_now_iso

VALID_TIMEFRAMES = {"M1", "M5", "M15", "H1"}
VALID_SOURCE_TYPES = {"BROKER_REST", "MT5_TERMINAL", "VENDOR_REST", "LOCAL_FILE"}


class OhlcvAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class NormalizedCandle:
    source_id: str
    source_type: str
    symbol: str
    timeframe: str
    ts_utc: str
    open: float
    high: float
    low: float
    close: float
    tick_volume: float
    spread: float | None
    is_complete: bool
    source_latency_ms: float | None
    received_at_utc: str
    volume_type: str = "tick_volume"
    monitor_only: bool = True


def _parse_ts_utc(value: str | int | float | datetime) -> str:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, (int, float)):
        parsed = datetime.fromtimestamp(float(value), tz=timezone.utc)
    else:
        raw = str(value).strip()
        if raw == "":
            raise OhlcvAdapterError("ts_utc is empty")
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise OhlcvAdapterError(f"ts_utc has no timezone: {value}")
    return parsed.astimezone(timezone.utc).isoformat()


def _to_float(value: Any, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise OhlcvAdapterError(f"{field} is not numeric: {value}") from exc
    if not math.isfinite(parsed):
        raise OhlcvAdapterError(f"{field} is not finite: {value}")
    return parsed


def normalize_candle(
    *,
    source_id: str,
    source_type: str,
    symbol: str,
    timeframe: str,
    ts_utc: str | int | float | datetime,
    open_price: Any,
    high_price: Any,
    low_price: Any,
    close_price: Any,
    tick_volume: Any = 0,
    spread: Any | None = None,
    is_complete: bool = True,
    source_latency_ms: Any | None = None,
    received_at_utc: str | None = None,
) -> dict[str, Any]:
    normalized_timeframe = timeframe.upper()
    if normalized_timeframe not in VALID_TIMEFRAMES:
        raise OhlcvAdapterError(f"unsupported timeframe: {timeframe}")
    normalized_source_type = source_type.upper()
    if normalized_source_type not in VALID_SOURCE_TYPES:
        raise OhlcvAdapterError(f"unsupported source_type: {source_type}")

    open_px = _to_float(open_price, "open")
    high_px = _to_float(high_price, "high")
    low_px = _to_float(low_price, "low")
    close_px = _to_float(close_price, "close")
    tick_volume_value = _to_float(tick_volume, "tick_volume")
    spread_value = None if spread in {None, ""} else _to_float(spread, "spread")
    latency_value = None if source_latency_ms in {None, ""} else _to_float(source_latency_ms, "source_latency_ms")

    if high_px < low_px:
        raise OhlcvAdapterError("high is below low")
    if high_px < max(open_px, close_px):
        raise OhlcvAdapterError("high is below open/close")
    if low_px > min(open_px, close_px):
        raise OhlcvAdapterError("low is above open/close")
    if tick_volume_value < 0:
        raise OhlcvAdapterError("tick_volume is negative")
    if spread_value is not None and spread_value < 0:
        raise OhlcvAdapterError("spread is negative")
    if latency_value is not None and latency_value < 0:
        raise OhlcvAdapterError("source_latency_ms is negative")

    candle = NormalizedCandle(
        source_id=source_id,
        source_type=normalized_source_type,
        symbol=symbol,
        timeframe=normalized_timeframe,
        ts_utc=_parse_ts_utc(ts_utc),
        open=open_px,
        high=high_px,
        low=low_px,
        close=close_px,
        tick_volume=tick_volume_value,
        spread=spread_value,
        is_complete=bool(is_complete),
        source_latency_ms=latency_value,
        received_at_utc=received_at_utc or utc_now_iso(),
    )
    return asdict(candle)


def build_ohlcv_connector_payload(
    *,
    source_id: str,
    symbol: str,
    timeframe: str,
    rows: list[dict[str, Any]],
    errors: list[str] | None = None,
    quality_flags: list[str] | None = None,
    source_type: str,
) -> dict[str, Any]:
    errors = list(errors or [])
    quality_flags = sorted(set(quality_flags or []))
    if errors:
        status = "ERROR"
    elif rows:
        status = "OK"
    else:
        status = "WARN"
        quality_flags = sorted(set(quality_flags + ["NO_COMPLETED_CANDLES"]))
    return {
        "ts_utc": utc_now_iso(),
        "source_id": source_id,
        "source_type": source_type,
        "symbol": symbol,
        "timeframe": timeframe,
        "status": status,
        "payload": {
            "ohlcv": {timeframe: rows},
            "spread": [],
            "volume_policy": "tick_volume is source quote activity, not centralized traded volume",
            "monitor_only": True,
        },
        "row_counts": {"ohlcv": {timeframe: len(rows)}, "spread": 0},
        "errors": errors,
        "quality_flags": quality_flags,
        "monitor_only": True,
    }
