import csv
import json
import subprocess
import sys
from pathlib import Path

from xau_lfx.connectors.rolling_event_dataset import append_event_log_draft, write_append_report
from xau_lfx.connectors.snapshot_event_mapper import build_event_log_draft_from_snapshot, write_event_log_draft
from xau_lfx.validation.event_log import EXPECTED_COLUMNS, validate_event_log


def _snapshot_payload(ts_utc="2026-07-02T01:00:00+00:00"):
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
                        "ts_utc": ts_utc,
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


def _validation_payload():
    return {"status": "OK", "source_id": "OANDA_REST", "source_type": "BROKER_REST", "symbol": "XAUUSD", "timeframe": "M1", "rows_checked": 1, "monitor_only": True}


def _write_json(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _draft_csv(tmp_path: Path, ts_utc="2026-07-02T01:00:00+00:00") -> Path:
    snapshot_path = _write_json(tmp_path, "normalized_ohlcv.json", _snapshot_payload(ts_utc))
    validation_path = _write_json(tmp_path, "ohlcv_snapshot_validation.json", _validation_payload())
    result = build_event_log_draft_from_snapshot(snapshot_path, validation_path)
    paths = write_event_log_draft(result, tmp_path / "draft")
    return Path(paths["csv"])


def _copy_dataset(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dst


def test_append_event_log_draft_creates_new_dataset(tmp_path):
    draft = _draft_csv(tmp_path)
    dataset = tmp_path / "dataset" / "rolling.csv"

    result = append_event_log_draft(draft_csv=draft, dataset_csv=dataset, out_dir=tmp_path / "out")

    assert result["status"] == "OK"
    assert result["existing_count"] == 0
    assert result["draft_count"] == 1
    assert result["appended_count"] == 1
    assert result["skipped_duplicate_count"] == 0
    output_csv = Path(result["output_csv"])
    assert output_csv.exists()
    assert validate_event_log(output_csv)["status"] == "OK"


def test_append_event_log_draft_skips_duplicate_rows(tmp_path):
    draft = _draft_csv(tmp_path)
    dataset = _copy_dataset(draft, tmp_path / "dataset" / "rolling.csv")

    result = append_event_log_draft(draft_csv=draft, dataset_csv=dataset, out_dir=tmp_path / "out")

    assert result["status"] == "OK"
    assert result["existing_count"] == 1
    assert result["draft_count"] == 1
    assert result["appended_count"] == 0
    assert result["skipped_duplicate_count"] == 1
    with Path(result["output_csv"]).open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1


def test_append_event_log_draft_appends_new_row_to_existing_dataset(tmp_path):
    existing_draft = _draft_csv(tmp_path / "existing", ts_utc="2026-07-02T01:00:00+00:00")
    new_draft = _draft_csv(tmp_path / "new", ts_utc="2026-07-02T01:01:00+00:00")
    dataset = _copy_dataset(existing_draft, tmp_path / "dataset" / "rolling.csv")

    result = append_event_log_draft(draft_csv=new_draft, dataset_csv=dataset, out_dir=tmp_path / "out")

    assert result["status"] == "OK"
    assert result["existing_count"] == 1
    assert result["draft_count"] == 1
    assert result["appended_count"] == 1
    with Path(result["output_csv"]).open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2


def test_append_event_log_draft_rejects_invalid_draft(tmp_path):
    bad_draft = tmp_path / "bad.csv"
    bad_draft.write_text("event_id,ts_utc\nmissing-columns,2026-07-02T01:00:00Z\n", encoding="utf-8")

    result = append_event_log_draft(draft_csv=bad_draft, dataset_csv=tmp_path / "dataset.csv", out_dir=tmp_path / "out")

    assert result["status"] == "ERROR"
    assert result["appended_count"] == 0
    assert any("draft event log validation failed" in error for error in result["errors"])


def test_write_append_report_outputs_markdown(tmp_path):
    draft = _draft_csv(tmp_path)
    result = append_event_log_draft(draft_csv=draft, dataset_csv=tmp_path / "dataset.csv", out_dir=tmp_path / "out")
    paths = write_append_report(result, tmp_path / "report")

    assert Path(paths["json"]).exists()
    md_text = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in md_text
    assert "APPENDED_COUNT: 1" in md_text


def test_rolling_event_dataset_cli_writes_outputs(tmp_path):
    draft = _draft_csv(tmp_path)
    out_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.rolling_event_dataset_cli",
            "--draft-csv",
            str(draft),
            "--dataset-csv",
            str(tmp_path / "dataset.csv"),
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
    assert Path(payload["report_paths"]["markdown"]).exists()
