import csv
import json
import subprocess
import sys
from pathlib import Path

from xau_lfx.connectors.snapshot_event_mapper import build_event_log_draft_from_snapshot, write_event_log_draft
from xau_lfx.validation.event_log import validate_event_log


def _snapshot_payload():
    return {
        "ts_utc": "2026-07-02T01:01:00+00:00",
        "source_id": "OANDA_REST",
        "source_type": "BROKER_REST",
        "symbol": "XAUUSD",
        "timeframe": "M1",
        "status": "OK",
        "payload": {
            "ohlcv": {
                "M1": [
                    {
                        "source_id": "OANDA_REST",
                        "source_type": "BROKER_REST",
                        "symbol": "XAUUSD",
                        "timeframe": "M1",
                        "ts_utc": "2026-07-02T01:00:00+00:00",
                        "open": 3300.0,
                        "high": 3301.0,
                        "low": 3299.0,
                        "close": 3300.5,
                        "tick_volume": 12.0,
                        "spread": None,
                        "is_complete": True,
                        "monitor_only": True,
                    }
                ]
            },
            "monitor_only": True,
        },
        "monitor_only": True,
    }


def _validation_payload(status="OK"):
    return {
        "status": status,
        "source_status": "OK",
        "source_id": "OANDA_REST",
        "source_type": "BROKER_REST",
        "symbol": "XAUUSD",
        "timeframe": "M1",
        "rows_checked": 1,
        "monitor_only": True,
    }


def _write_json(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_snapshot_event_mapper_builds_no_inference_event_rows(tmp_path):
    snapshot_path = _write_json(tmp_path, "normalized_ohlcv.json", _snapshot_payload())
    validation_path = _write_json(tmp_path, "ohlcv_snapshot_validation.json", _validation_payload())

    result = build_event_log_draft_from_snapshot(snapshot_path, validation_path)

    assert result["status"] == "OK"
    assert result["row_count"] == 1
    assert result["monitor_only"] is True
    row = result["rows"][0]
    assert row["broker_source"] == "OANDA_REST"
    assert row["timeframe"] == "M1"
    assert row["session"] == "UNKNOWN"
    assert row["lifecycle_state"] == "NO_SWEEP"
    assert row["delivery_state"] == "D_NONE"
    assert "source_type=BROKER_REST" in row["review_notes"]
    assert "no_lifecycle_inference" in row["review_notes"]


def test_snapshot_event_mapper_rejects_non_ok_validation(tmp_path):
    snapshot_path = _write_json(tmp_path, "normalized_ohlcv.json", _snapshot_payload())
    validation_path = _write_json(tmp_path, "ohlcv_snapshot_validation.json", _validation_payload(status="ERROR"))

    result = build_event_log_draft_from_snapshot(snapshot_path, validation_path)

    assert result["status"] == "ERROR"
    assert result["rows"] == []
    assert any("validation status must be OK" in error for error in result["errors"])


def test_snapshot_event_mapper_writes_valid_event_log_csv(tmp_path):
    snapshot_path = _write_json(tmp_path, "normalized_ohlcv.json", _snapshot_payload())
    validation_path = _write_json(tmp_path, "ohlcv_snapshot_validation.json", _validation_payload())
    result = build_event_log_draft_from_snapshot(snapshot_path, validation_path)
    paths = write_event_log_draft(result, tmp_path / "mapped")

    csv_path = Path(paths["csv"])
    validation_report = json.loads(Path(paths["validation"]).read_text(encoding="utf-8"))
    assert csv_path.exists()
    assert validation_report["status"] == "OK"
    assert validate_event_log(csv_path)["status"] == "OK"
    with csv_path.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["dashboard_state"] == "SNAPSHOT_ONLY"
    assert rows[0]["target_hit"] == "false"


def test_snapshot_event_mapper_cli_writes_outputs(tmp_path):
    snapshot_path = _write_json(tmp_path, "normalized_ohlcv.json", _snapshot_payload())
    validation_path = _write_json(tmp_path, "ohlcv_snapshot_validation.json", _validation_payload())
    out_dir = tmp_path / "mapped"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.snapshot_event_mapper_cli",
            "--snapshot",
            str(snapshot_path),
            "--validation",
            str(validation_path),
            "--out-dir",
            str(out_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "OK"
    assert Path(payload["report_paths"]["csv"]).exists()
    assert Path(payload["report_paths"]["json"]).exists()
    assert Path(payload["report_paths"]["validation"]).exists()
