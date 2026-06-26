from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from xau_lfx.forbidden_language import assert_clean_language
from xau_lfx.utils import parse_iso_utc, utc_now_iso


def _latest_close(composite: dict[str, Any]) -> float | None:
    value = composite.get("median_latest_close")
    if value is not None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    rows = composite.get("bars", [])
    if rows:
        try:
            return float(rows[-1]["close"])
        except (KeyError, TypeError, ValueError):
            return None
    return None


def _freshness_age_minutes(composite: dict[str, Any]) -> float | None:
    latest_by_tf = composite.get("latest_by_timeframe", {})
    timestamps: list[datetime] = []
    if isinstance(latest_by_tf, dict):
        for row in latest_by_tf.values():
            if not isinstance(row, dict) or "ts_utc" not in row:
                continue
            try:
                timestamps.append(parse_iso_utc(row["ts_utc"]))
            except ValueError:
                continue
    if not timestamps:
        rows = composite.get("bars", [])
        if rows:
            try:
                timestamps.append(parse_iso_utc(rows[-1]["ts_utc"]))
            except (KeyError, ValueError):
                pass
    if not timestamps:
        return None
    latest_ts = max(timestamps)
    age = max(0.0, (datetime.now(timezone.utc) - latest_ts).total_seconds() / 60.0)
    return round(age, 2)


def _nearest_session_level(session: dict[str, Any], latest_close: float | None) -> dict[str, Any] | None:
    if latest_close is None:
        return None
    best: dict[str, Any] | None = None
    for session_name, block in session.get("session_ranges", {}).items():
        if not isinstance(block, dict):
            continue
        for level_name in ("high", "low"):
            value = block.get(level_name)
            if value is None:
                continue
            try:
                level_price = float(value)
            except (TypeError, ValueError):
                continue
            distance = abs(latest_close - level_price)
            candidate = {
                "session": session_name,
                "level": level_name,
                "price": round(level_price, 4),
                "distance_points": round(distance, 4),
            }
            if best is None or candidate["distance_points"] < best["distance_points"]:
                best = candidate
    return best


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _side_from_latest(level_price: float, latest_close: float) -> str:
    if level_price > latest_close:
        return "above"
    if level_price < latest_close:
        return "below"
    return "at"


def _practical_zone_deck(session: dict[str, Any], latest_close: float | None) -> list[dict[str, Any]]:
    """Build ranked monitor-only session references for practical inspection.

    The deck is derived only from supplied session high/low levels and the latest
    composite close. It does not infer direction, execution, or profitability.
    """
    if latest_close is None:
        return []

    deck: list[dict[str, Any]] = []
    for session_name, block in session.get("session_ranges", {}).items():
        if not isinstance(block, dict):
            continue

        bar_count = _optional_int(block.get("bar_count"))
        range_points = _optional_float(block.get("range_points"))

        for level_name in ("high", "low"):
            level_price = _optional_float(block.get(level_name))
            if level_price is None:
                continue

            distance = abs(latest_close - level_price)
            side = _side_from_latest(level_price, latest_close)
            deck.append(
                {
                    "rank": 0,
                    "role": f"{session_name}_{level_name.upper()}_REFERENCE",
                    "session": session_name,
                    "level": level_name,
                    "price": round(level_price, 4),
                    "side_from_latest": side,
                    "distance_points": round(distance, 4),
                    "range_points": round(range_points, 4) if range_points is not None else None,
                    "bar_count": bar_count,
                    "why_it_matters": (
                        "Ranked session reference from supplied M15 context; useful for observing "
                        "accept, reject, or rotation behavior without directional instruction."
                    ),
                    "operator_read": (
                        f"Observe accept or reject behavior around {session_name} {level_name} "
                        "reference; use M5 only as confirmation context."
                    ),
                }
            )

    deck.sort(key=lambda item: (item["distance_points"], item["session"], item["level"]))
    practical_deck = deck[:4]
    for rank, item in enumerate(practical_deck, start=1):
        item["rank"] = rank
    return practical_deck


def _spread_state(data_quality: dict[str, Any]) -> str:
    flags = set(data_quality.get("quality_flags", []))
    stability = float(data_quality.get("spread_stability", 0.0) or 0.0)
    if "SPREAD_SOURCE_MISSING" in flags:
        return "MISSING"
    if stability >= 0.8:
        return "STABLE"
    if stability >= 0.6:
        return "WATCH"
    return "UNSTABLE"


def _confidence_explanation(data_quality: dict[str, Any], event: dict[str, Any], spread_state: str) -> list[str]:
    lines: list[str] = []
    present = data_quality.get("present_timeframes", [])
    if set(present) >= {"M5", "M15", "H1"}:
        lines.append("M5/M15/H1 local bar coverage is complete.")
    else:
        lines.append("MTF coverage is incomplete; confidence remains capped.")

    freshness = float(data_quality.get("freshness_score", 0.0) or 0.0)
    if freshness >= 0.8:
        lines.append("Latest local bars are fresh relative to the 72-hour freshness window.")
    elif freshness > 0.0:
        lines.append("Latest local bars are aging; refresh source exports before relying on the report.")
    else:
        lines.append("No valid fresh OHLCV rows are available.")

    if spread_state == "STABLE":
        lines.append("Spread source is stable enough for monitor context.")
    elif spread_state == "WATCH":
        lines.append("Spread source is usable but should be watched for expansion.")
    elif spread_state == "MISSING":
        lines.append("Spread source is missing; confidence is reduced.")
    else:
        lines.append("Spread instability is present; confidence is reduced.")

    if event.get("near_high_impact_events"):
        lines.append("A high-impact USD event is inside the local risk window; confidence is capped.")
    elif event.get("event_count", 0):
        lines.append("Event file is loaded and used as risk context only.")
    else:
        lines.append("Event source is not configured; confidence is reduced.")
    if data_quality.get("errors"):
        lines.append("Source validation errors are present; inspect xau_data_quality.json before using artifacts.")
    return lines


def _monitor_focus(
    nearest_level: dict[str, Any] | None,
    spread_state: str,
    event: dict[str, Any],
    practical_zones: list[dict[str, Any]],
) -> list[str]:
    focus: list[str] = []
    if nearest_level:
        focus.append(
            "Observe behavior around "
            f"{nearest_level['session']} {nearest_level['level']} "
            f"({nearest_level['price']}); distance {nearest_level['distance_points']} points."
        )
    else:
        focus.append("Observe whether new local exports create usable session reference levels.")
    if practical_zones:
        lead_zone = practical_zones[0]
        focus.append(
            "Start inspection with practical zone rank "
            f"{lead_zone['rank']}: {lead_zone['session']} {lead_zone['level']} "
            f"at {lead_zone['price']}."
        )
    focus.append("Compare M15 context with M5 confirmation behavior and H1 structural context.")
    if spread_state in {"WATCH", "UNSTABLE", "MISSING"}:
        focus.append("Reduce confidence if spread remains unstable, unavailable, or widens during the session.")
    else:
        focus.append("Keep spread stability on the monitor list during active sessions.")
    if event.get("near_high_impact_events"):
        focus.append("Treat nearby high-impact USD events as a risk block for context interpretation.")
    else:
        focus.append("Keep the event file current before major USD macro windows.")
    return focus


def build_context_summary(
    data_quality: dict[str, Any],
    composite: dict[str, Any],
    session: dict[str, Any],
    event: dict[str, Any],
    artifact_quality: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact monitor-only summary for human inspection.

    This is an interpretation aid for artifact users. It does not infer direction,
    order timing, account risk, or execution actions.
    """
    latest_close = _latest_close(composite)
    freshness_age_minutes = _freshness_age_minutes(composite)
    nearest_level = _nearest_session_level(session, latest_close)
    practical_zones = _practical_zone_deck(session, latest_close)
    spread_state = _spread_state(data_quality)
    explanation = _confidence_explanation(data_quality, event, spread_state)
    focus = _monitor_focus(nearest_level, spread_state, event, practical_zones)

    summary = {
        "ts_utc": utc_now_iso(),
        "symbol": data_quality.get("symbol", "XAUUSD"),
        "monitor_only": True,
        "latest_close": round(latest_close, 4) if latest_close is not None else None,
        "freshness_age_minutes": freshness_age_minutes,
        "nearest_session_level": nearest_level,
        "practical_zone_deck": practical_zones,
        "spread_state": spread_state,
        "event_risk_state": event.get("risk_state", "UNKNOWN"),
        "quality_status": artifact_quality.get("status", "UNKNOWN"),
        "quality_grade": artifact_quality.get("quality_grade", "n/a"),
        "confidence_cap": artifact_quality.get("confidence_cap", data_quality.get("confidence_cap", 0.0)),
        "confidence_explanation": explanation,
        "monitor_focus": focus,
        "limitations": [
            "Monitor-only context summary; not an execution plan.",
            "Broker tick activity remains a local activity proxy, not centralized volume.",
            "Session levels are references from supplied CSV data only.",
            "Practical zone deck ranks supplied session references by distance only; it does not infer direction.",
        ],
        "quality_flags": sorted(set(data_quality.get("quality_flags", [])) | set(event.get("quality_flags", []))),
    }
    assert_clean_language(summary)
    return summary
