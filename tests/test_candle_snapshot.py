import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from xau_lfx.connectors.candle_snapshot import validate_ohlcv_snapshot, write_snapshot_validation


def _snapshot_payload(ts_utc: str, *, is_complete=True, duplicate=False, status="OK"):
    row = {
        "source_id": "TEST",
        "source_type": "BROKER_REST",
        "symbol": "XAUUSD",
        "timeframe": "M1",
        "ts_utc": ts_utc,
        "open": 3300.0,
        "high": 3301.0,
        "low": 3299.0,
        "close": 3300.5,
        "tick_volume": 12.0,
        "spread": None,
        "is_complete": is_complete,
        "source_latency_ms": 1.0,
        "received_at_utc": ts_utc,
        "monitor_only": True,
    }
    rows = [row, dict(row)] if duplicate else [row]
    return {
        "ts_utc": ts_utc,
        "source_id": "TEST",
        "source_type": "BROKER_REST",
        "symbol": "XAUUSD",
        "timeframe": "M1",
        "status": status,
        "payload": {"ohlcv": {"M1": rows}, "monitor_only": True},
        "row_counts": {"ohlcv": {"M1": len(rows)}},
        "errors": [],
        "quality_flags": [],
        "monitor_only": True,
    }


def _write_snapshot(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "normalized_ohlcv.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_snapshot_validation_accepts_fresh_completed_rows(tmp_path):
    now = datetime(2026, 7, 2, 1, 2, tzinfo=timezone.utc)
    path = _write_snapshot(tmp_path, _snapshot_payload("2026-07-02T01:00:30+00:00"))

    result = validate_ohlcv_snapshot(path, max_age_seconds=180, now_utc=now)

    assert result["status"] == "OK"
    assert result["rows_checked"] == 1
    assert result["age_seconds"] == 90.0
    assert result["monitor_only"] is True


def test_snapshot_validation_rejects_incomplete_rows(tmp_path):
    now = datetime(2026, 7, 2, 1, 2, tzinfo=timezone.utc)
    path = _write_snapshot(tmp_path, _snapshot_payload("2026-07-02T01:00:30+00:00", is_complete=False))

    result = validate_ohlcv_snapshot(path, max_age_seconds=180, now_utc=now)

    assert result["status"] == "ERROR"
    assert any("INCOMPLETE_CANDLE" in error for error in result["errors"])


def test_snapshot_validation_rejects_duplicate_timestamps(tmp_path):
    now = datetime(2026, 7, 2, 1, 2, tzinfo=timezone.utc)
    path = _write_snapshot(tmp_path, _snapshot_payload("2026-07-02T01:00:30+00:00", duplicate=True))

    result = validate_ohlcv_snapshot(path, max_age_seconds=180, now_utc=now)

    assert result["status"] == "ERROR"
    assert any("DUPLICATE_TS_UTC" in error for error in result["errors"])


def test_snapshot_validation_rejects_stale_payload(tmp_path):
    now = datetime(2026, 7, 2, 1, 10, tzinfo=timezone.utc)
    path = _write_snapshot(tmp_path, _snapshot_payload("2026-07-02T01:00:30+00:00"))

    result = validate_ohlcv_snapshot(path, max_age_seconds=180, now_utc=now)

    assert result["status"] == "ERROR"
    assert any("SNAPSHOT_STALE" in error for error in result["errors"])


def test_snapshot_validation_allows_source_warn_with_warning(tmp_path):
    now = datetime(2026, 7, 2, 1, 2, tzinfo=timezone.utc)
    path = _write_snapshot(tmp_path, _snapshot_payload("2026-07-02T01:00:30+00:00", status="WARN"))

    result = validate_ohlcv_snapshot(path, max_age_seconds=180, now_utc=now)

    assert result["status"] == "OK"
    assert "SOURCE_STATUS_WARN" in result["warnings"]


def test_snapshot_validation_cli_writes_reports(tmp_path):
    now = datetime.now(timezone.utc) - timedelta(seconds=30)
    path = _write_snapshot(tmp_path, _snapshot_payload(now.isoformat()))
    out_dir = tmp_path / "validation"

    cli_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.candle_snapshot_cli",
            "--snapshot",
            str(path),
            "--out-dir",
            str(out_dir),
            "--max-age-seconds",
            "180",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert cli_result.returncode == 0
    payload = json.loads(cli_result.stdout)
    assert payload["status"] == "OK"
    assert Path(payload["report_paths"]["json"]).exists()
    assert Path(payload["report_paths"]["markdown"]).exists()


def test_write_snapshot_validation_outputs_markdown(tmp_path):
    result = {"status": "OK", "source_status": "OK", "source_id": "TEST", "symbol": "XAUUSD", "timeframe": "M1", "rows_checked": 1, "monitor_only": True}
    paths = write_snapshot_validation(result, tmp_path)
    md_text = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in md_text
