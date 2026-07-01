from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS: tuple[str, ...] = (
    "event_id",
    "ts_utc",
    "symbol",
    "broker_source",
    "timeframe",
    "session",
    "dashboard_state",
    "trader_mode",
    "lifecycle_state",
    "delivery_state",
)

EXPECTED_COLUMNS: tuple[str, ...] = (
    "event_id",
    "ts_utc",
    "symbol",
    "broker_source",
    "timeframe",
    "session",
    "shock_slot",
    "manual_news_block",
    "spread_state",
    "dashboard_state",
    "trader_mode",
    "sweep_source",
    "sweep_level",
    "sweep_side",
    "sweep_score",
    "lifecycle_state",
    "absorb_score",
    "zone_role",
    "zone_price",
    "route_dir",
    "route_origin",
    "target_ref",
    "delivery_state",
    "route_age_bars",
    "target_dist_at_lock_atr",
    "current_target_dist_atr",
    "terminal_state",
    "mfe_5",
    "mae_5",
    "mfe_10",
    "mae_10",
    "mfe_20",
    "mae_20",
    "time_to_resolution_bars",
    "target_hit",
    "route_failed",
    "manual_review_result",
    "review_notes",
)

OPTIONAL_FLOAT_COLUMNS: tuple[str, ...] = (
    "sweep_level",
    "sweep_score",
    "absorb_score",
    "zone_price",
    "route_origin",
    "target_ref",
    "target_dist_at_lock_atr",
    "current_target_dist_atr",
    "mfe_5",
    "mae_5",
    "mfe_10",
    "mae_10",
    "mfe_20",
    "mae_20",
)

OPTIONAL_INT_COLUMNS: tuple[str, ...] = (
    "route_age_bars",
    "time_to_resolution_bars",
)

OPTIONAL_BOOL_COLUMNS: tuple[str, ...] = (
    "manual_news_block",
    "target_hit",
    "route_failed",
)

ALLOWED_TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"}
ALLOWED_SESSIONS = {"ASIA", "LONDON", "NY", "OFF", "UNKNOWN"}
ALLOWED_SIDES = {"UP", "DN", "NONE", ""}
ALLOWED_LIFECYCLE = {
    "NO_SWEEP",
    "RAW_SPIKE",
    "RECLAIM",
    "ACCEPT",
    "REJECT",
    "RECLAIM_FAIL",
    "ACCEPT_FAIL",
}
ALLOWED_DELIVERY = {
    "D_NONE",
    "D_ACTIVE",
    "D_STALL",
    "D_COUNTERFLOW",
    "D_TARGET_HIT",
    "D_FAILED",
}
ALLOWED_TERMINAL = {"HIT", "FAILED", "RESET", "OPEN", ""}
ALLOWED_REVIEW = {"MATCH", "PARTIAL", "WRONG", "UNCLEAR", ""}
FORBIDDEN_COLUMNS = {
    "api_key",
    "api_token",
    "token",
    "secret",
    "password",
    "account_balance",
    "equity",
    "position_size",
    "lot_size",
}


def _normalize_header(value: str | None) -> str:
    return (value or "").strip()


def _cell(row: dict[str, str], column: str) -> str:
    return (row.get(column) or "").strip()


def _parse_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized == "":
        return None
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"expected boolean, got {value!r}")


def _parse_utc_datetime(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def _validate_numeric(row: dict[str, str], row_number: int, errors: list[str]) -> None:
    for column in OPTIONAL_FLOAT_COLUMNS:
        value = _cell(row, column)
        if value == "":
            continue
        try:
            float(value)
        except ValueError:
            errors.append(f"row {row_number}: {column} must be numeric")

    for column in OPTIONAL_INT_COLUMNS:
        value = _cell(row, column)
        if value == "":
            continue
        try:
            parsed = int(value)
        except ValueError:
            errors.append(f"row {row_number}: {column} must be an integer")
            continue
        if parsed < 0:
            errors.append(f"row {row_number}: {column} must be non-negative")


def _validate_bools(row: dict[str, str], row_number: int, errors: list[str]) -> dict[str, bool | None]:
    parsed: dict[str, bool | None] = {}
    for column in OPTIONAL_BOOL_COLUMNS:
        value = _cell(row, column)
        try:
            parsed[column] = _parse_bool(value)
        except ValueError as exc:
            errors.append(f"row {row_number}: {column} {exc}")
            parsed[column] = None
    return parsed


def _validate_enum(value: str, allowed: set[str], column: str, row_number: int, errors: list[str]) -> None:
    if value.upper() not in allowed:
        allowed_text = ", ".join(sorted(item for item in allowed if item))
        errors.append(f"row {row_number}: {column} must be one of: {allowed_text}")


def _validate_cross_fields(
    row: dict[str, str],
    bools: dict[str, bool | None],
    row_number: int,
    errors: list[str],
    warnings: list[str],
) -> None:
    delivery_state = _cell(row, "delivery_state").upper()
    lifecycle_state = _cell(row, "lifecycle_state").upper()
    target_hit = bools.get("target_hit")
    route_failed = bools.get("route_failed")
    target_ref = _cell(row, "target_ref")

    if delivery_state == "D_TARGET_HIT" and route_failed is True:
        errors.append(f"row {row_number}: D_TARGET_HIT cannot have route_failed=true")
    if delivery_state == "D_FAILED" and target_hit is True:
        errors.append(f"row {row_number}: D_FAILED cannot have target_hit=true")
    if delivery_state == "D_ACTIVE" and target_ref == "":
        warnings.append(f"row {row_number}: D_ACTIVE without target_ref limits route-quality analysis")
    if lifecycle_state in {"RECLAIM", "ACCEPT"} and delivery_state == "D_NONE":
        warnings.append(f"row {row_number}: resolved lifecycle with D_NONE should be reviewed")


def validate_event_log(path: str | Path) -> dict[str, Any]:
    """Validate a v9 forward-validation event log CSV.

    The validator checks schema compatibility and monitor-only research boundaries.
    It does not score predictive usefulness and does not infer trade direction.
    """

    csv_path = Path(path)
    errors: list[str] = []
    warnings: list[str] = []

    if not csv_path.exists():
        return {
            "status": "ERROR",
            "path": str(csv_path),
            "rows_checked": 0,
            "errors": [f"event log not found: {csv_path}"],
            "warnings": [],
        }

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = [_normalize_header(header) for header in (reader.fieldnames or [])]
            if not headers:
                return {
                    "status": "ERROR",
                    "path": str(csv_path),
                    "rows_checked": 0,
                    "errors": ["event log has no header row"],
                    "warnings": [],
                }

            header_set = set(headers)
            missing = [column for column in REQUIRED_COLUMNS if column not in header_set]
            if missing:
                errors.append("missing required columns: " + ", ".join(missing))

            forbidden = sorted(header_set & FORBIDDEN_COLUMNS)
            if forbidden:
                errors.append("forbidden sensitive columns present: " + ", ".join(forbidden))

            extra_columns = sorted(header_set - set(EXPECTED_COLUMNS))
            if extra_columns:
                warnings.append("extra columns ignored by validator: " + ", ".join(extra_columns))

            seen_ids: set[str] = set()
            rows_checked = 0
            for rows_checked, row in enumerate(reader, start=1):
                row_number = rows_checked + 1
                for column in REQUIRED_COLUMNS:
                    if _cell(row, column) == "":
                        errors.append(f"row {row_number}: {column} is required")

                event_id = _cell(row, "event_id")
                if event_id:
                    if event_id in seen_ids:
                        errors.append(f"row {row_number}: duplicate event_id {event_id!r}")
                    seen_ids.add(event_id)

                timestamp = _cell(row, "ts_utc")
                if timestamp:
                    try:
                        _parse_utc_datetime(timestamp)
                    except ValueError as exc:
                        errors.append(f"row {row_number}: ts_utc {exc}")

                if _cell(row, "timeframe"):
                    _validate_enum(_cell(row, "timeframe"), ALLOWED_TIMEFRAMES, "timeframe", row_number, errors)
                if _cell(row, "session"):
                    _validate_enum(_cell(row, "session"), ALLOWED_SESSIONS, "session", row_number, errors)
                if _cell(row, "sweep_side"):
                    _validate_enum(_cell(row, "sweep_side"), ALLOWED_SIDES, "sweep_side", row_number, errors)
                if _cell(row, "route_dir"):
                    _validate_enum(_cell(row, "route_dir"), ALLOWED_SIDES, "route_dir", row_number, errors)
                if _cell(row, "lifecycle_state"):
                    _validate_enum(
                        _cell(row, "lifecycle_state"),
                        ALLOWED_LIFECYCLE,
                        "lifecycle_state",
                        row_number,
                        errors,
                    )
                if _cell(row, "delivery_state"):
                    _validate_enum(
                        _cell(row, "delivery_state"),
                        ALLOWED_DELIVERY,
                        "delivery_state",
                        row_number,
                        errors,
                    )
                if _cell(row, "terminal_state"):
                    _validate_enum(
                        _cell(row, "terminal_state"),
                        ALLOWED_TERMINAL,
                        "terminal_state",
                        row_number,
                        errors,
                    )
                if _cell(row, "manual_review_result"):
                    _validate_enum(
                        _cell(row, "manual_review_result"),
                        ALLOWED_REVIEW,
                        "manual_review_result",
                        row_number,
                        errors,
                    )

                _validate_numeric(row, row_number, errors)
                bools = _validate_bools(row, row_number, errors)
                _validate_cross_fields(row, bools, row_number, errors, warnings)
    except csv.Error as exc:
        return {
            "status": "ERROR",
            "path": str(csv_path),
            "rows_checked": 0,
            "errors": [f"CSV parser error: {exc}"],
            "warnings": warnings,
        }

    status = "ERROR" if errors else ("WARN" if warnings else "OK")
    return {
        "status": status,
        "path": str(csv_path),
        "rows_checked": rows_checked,
        "errors": errors,
        "warnings": warnings,
        "monitor_only": True,
        "schema": "EVENT_DATASET_SCHEMA_V9",
    }
