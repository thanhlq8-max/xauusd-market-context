from pathlib import Path

from xau_lfx.validation.event_log import validate_event_log


ROOT = Path(__file__).resolve().parents[1]
HEADER = (
    "event_id,ts_utc,symbol,broker_source,timeframe,session,shock_slot,manual_news_block,"
    "spread_state,dashboard_state,trader_mode,sweep_source,sweep_level,sweep_side,"
    "sweep_score,lifecycle_state,absorb_score,zone_role,zone_price,route_dir,"
    "route_origin,target_ref,delivery_state,route_age_bars,target_dist_at_lock_atr,"
    "current_target_dist_atr,terminal_state,mfe_5,mae_5,mfe_10,mae_10,mfe_20,"
    "mae_20,time_to_resolution_bars,target_hit,route_failed,manual_review_result,review_notes"
)


def _write_event_log(path: Path, rows: list[str]) -> Path:
    path.write_text(HEADER + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def test_committed_event_log_template_validates():
    result = validate_event_log(ROOT / "data" / "events" / "event_log_template.csv")

    assert result["status"] == "OK"
    assert result["rows_checked"] == 2
    assert result["monitor_only"] is True
    assert result["schema"] == "EVENT_DATASET_SCHEMA_V9"


def test_event_log_validator_rejects_missing_required_columns(tmp_path):
    path = tmp_path / "bad_missing.csv"
    path.write_text("event_id,ts_utc\ne1,2026-07-01T08:00:00Z\n", encoding="utf-8")

    result = validate_event_log(path)

    assert result["status"] == "ERROR"
    assert any("missing required columns" in error for error in result["errors"])


def test_event_log_validator_rejects_sensitive_columns(tmp_path):
    path = tmp_path / "bad_sensitive.csv"
    path.write_text(HEADER + ",api_token\n" + _valid_row("e1") + ",secret-value\n", encoding="utf-8")

    result = validate_event_log(path)

    assert result["status"] == "ERROR"
    assert any("forbidden sensitive columns" in error for error in result["errors"])


def test_event_log_validator_rejects_delivery_cross_field_conflict(tmp_path):
    path = _write_event_log(
        tmp_path / "bad_cross_field.csv",
        [_valid_row("e1").replace(",D_ACTIVE,", ",D_TARGET_HIT,").replace(",false,false,", ",false,true,")],
    )

    result = validate_event_log(path)

    assert result["status"] == "ERROR"
    assert any("D_TARGET_HIT cannot have route_failed=true" in error for error in result["errors"])


def test_event_log_validator_warns_for_active_route_without_target(tmp_path):
    path = _write_event_log(
        tmp_path / "warn_active_without_target.csv",
        [_valid_row("e1").replace(",4076.015,D_ACTIVE,", ",,D_ACTIVE,")],
    )

    result = validate_event_log(path)

    assert result["status"] == "WARN"
    assert any("D_ACTIVE without target_ref" in warning for warning in result["warnings"])


def _valid_row(event_id: str) -> str:
    return (
        f"{event_id},2026-07-01T08:00:00Z,XAUUSD,SYNTHETIC,M15,LONDON,Normal clock,"
        "false,stable,Reclaim route active,TRACK ROUTE HEALTH,PDH,4044.140,DN,"
        "0.62,RECLAIM,0.71,TargetRef,4076.015,UP,4044.140,4076.015,"
        "D_ACTIVE,3,2.1,1.4,OPEN,,,,,,,,false,false,MATCH,synthetic test row"
    )
