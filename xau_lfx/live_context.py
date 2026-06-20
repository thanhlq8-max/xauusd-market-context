from __future__ import annotations

from datetime import datetime
from typing import Any

from xau_lfx.engines.session_context import SESSION_BUCKETS
from xau_lfx.utils import parse_iso_utc


def _timeframe_candles(snapshot: dict[str, Any], timeframe: str) -> list[dict[str, Any]]:
    try:
        candles = snapshot["timeframes"][timeframe]["candles"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"live snapshot is missing {timeframe} candles") from exc
    if not isinstance(candles, list) or not candles:
        raise ValueError(f"live snapshot has no {timeframe} candles")
    return candles


def _latest_complete(candles: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((candle for candle in reversed(candles) if candle["complete"]), None)


def _session_name(ts_utc: str) -> str | None:
    parsed = parse_iso_utc(ts_utc)
    minutes = parsed.hour * 60 + parsed.minute
    for name, (start, end) in SESSION_BUCKETS.items():
        if start <= minutes < end:
            return name
    return None


def _session_zones(candles: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    latest_date = parse_iso_utc(candles[-1]["ts_utc"]).date()
    grouped: dict[str, list[dict[str, Any]]] = {name: [] for name in SESSION_BUCKETS}
    for candle in candles:
        parsed = parse_iso_utc(candle["ts_utc"])
        if parsed.date() != latest_date:
            continue
        session = _session_name(candle["ts_utc"])
        if session is not None:
            grouped[session].append(candle)

    zones: list[dict[str, Any]] = []
    for name, rows in grouped.items():
        if not rows:
            continue
        zones.append(
            {
                "session": name,
                "high": round(max(float(row["mid"]["high"]) for row in rows), 5),
                "low": round(min(float(row["mid"]["low"]) for row in rows), 5),
                "last_close": round(float(rows[-1]["mid"]["close"]), 5),
                "bar_count": len(rows),
                "last_ts_utc": rows[-1]["ts_utc"],
            }
        )
    return latest_date.isoformat(), zones


def _nearest_zone(zones: list[dict[str, Any]], price: float) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for zone in zones:
        for level in ("high", "low"):
            level_price = float(zone[level])
            candidates.append(
                {
                    "session": zone["session"],
                    "level": level,
                    "price": round(level_price, 5),
                    "distance_price_units": round(abs(price - level_price), 5),
                }
            )
    return min(candidates, key=lambda item: item["distance_price_units"]) if candidates else None


def _candle_fact(candle: dict[str, Any], timeframe: str) -> dict[str, Any]:
    mid = candle["mid"]
    change = float(mid["close"]) - float(mid["open"])
    return {
        "timeframe": timeframe,
        "ts_utc": candle["ts_utc"],
        "complete": candle["complete"],
        "open": mid["open"],
        "high": mid["high"],
        "low": mid["low"],
        "close": mid["close"],
        "change_price_units": round(change, 5),
        "range_price_units": round(float(mid["high"]) - float(mid["low"]), 5),
        "price_count": candle["price_count"],
    }


def build_live_context(snapshot: dict[str, Any], now: datetime) -> dict[str, Any]:
    if now.tzinfo is None:
        raise ValueError("now must include a timezone")

    m5 = _timeframe_candles(snapshot, "M5")
    m15 = _timeframe_candles(snapshot, "M15")
    _timeframe_candles(snapshot, "H1")
    latest_m5 = m5[-1]
    latest_m15_complete = _latest_complete(m15)
    session_date, zones = _session_zones(m15)
    latest_price = float(latest_m5["mid"]["close"])
    nearest = _nearest_zone(zones, latest_price)
    market_age = max(0.0, (now - parse_iso_utc(latest_m5["ts_utc"])).total_seconds())
    spread_proxy = float(latest_m5["ask"]["close"]) - float(latest_m5["bid"]["close"])

    past = {
        "state": "OBSERVED" if latest_m15_complete is not None else "UNAVAILABLE",
        "fact": _candle_fact(latest_m15_complete, "M15") if latest_m15_complete is not None else None,
        "note": (
            "Latest complete M15 candle is reported as an observed price fact."
            if latest_m15_complete is not None
            else "OANDA did not return a complete M15 candle in the requested window."
        ),
    }
    now_block = {
        "state": "FORMING" if not latest_m5["complete"] else "LATEST_COMPLETE",
        "fact": _candle_fact(latest_m5, "M5"),
        "note": (
            "The newest M5 candle is still forming."
            if not latest_m5["complete"]
            else "No forming M5 candle was returned; the newest M5 candle is complete."
        ),
    }
    next_block = {
        "state": "REFERENCE_AVAILABLE" if nearest is not None else "UNAVAILABLE",
        "nearest_session_level": nearest,
        "condition": (
            "Observe the response around the nearest supplied session boundary; no outcome is inferred."
            if nearest is not None
            else "No Asia, London, or New York session boundary is available for the latest market date."
        ),
    }

    return {
        "monitor_only": True,
        "past": past,
        "now": now_block,
        "next": next_block,
        "key_zones": {
            "session_date_utc": session_date,
            "sessions": zones,
        },
        "mission": {
            "state": "NOT_INFERRED",
            "reason": "OANDA OHLC candles alone do not establish an MM mission.",
        },
        "inventory_release": {
            "state": "NOT_INFERRED",
            "reason": "OANDA OHLC candles alone do not establish dealer inventory or a release state.",
        },
        "operator_mode": "OBSERVE",
        "source_risk": {
            "source_family_count": 1,
            "latest_candle_age_seconds": round(market_age, 3),
            "latest_candle_complete": latest_m5["complete"],
            "latest_close_spread_proxy": round(spread_proxy, 5),
            "spread_unit": "price units at the latest M5 candle close",
            "event_context": "NOT_CONFIGURED_IN_OANDA_ONLY_MODE",
        },
    }
