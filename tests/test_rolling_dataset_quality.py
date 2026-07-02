import csv
import json
import subprocess
import sys
from pathlib import Path

from xau_lfx.connectors.rolling_dataset_quality import build_rolling_dataset_quality_report, write_rolling_dataset_quality_report
from xau_lfx.validation.event_log import EXPECTED_COLUMNS


def _event_row(event_id="event-1", ts_utc="2026-07-02T01:00:00+00:00", broker_source="OANDA_REST", timeframe="M1"):
    row = {column: "" for column in EXPECTED_COLUMNS}
    row.update(
        {
            "event_id": event_id,
            "ts_utc": ts_utc,
            "symbol": "XAUUSD",
            "broker_source": broker_source,
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
            "review_notes": "monitor_only=true; no_lifecycle_inference",
        }
    )
    return row


def _write_dataset(tmp_path: Path, rows: list[dict[str, str]]) -> Path:
    path = tmp_path / "rolling_event_dataset.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in EXPECTED_COLUMNS})
    return path


def test_rolling_dataset_quality_counts_source_timeframe_and_placeholders(tmp_path):
    dataset = _write_dataset(
        tmp_path,
        [
            _event_row(event_id="event-1", broker_source="OANDA_REST", timeframe="M1"),
            _event_row(event_id="event-2", broker_source="MT5_BRIDGE", timeframe="M5"),
            _event_row(event_id="event-3", broker_source="OANDA_REST", timeframe="M1"),
        ],
    )

    result = build_rolling_dataset_quality_report(dataset)

    assert result["status"] == "OK"
    assert result["row_count"] == 3
    assert result["source_coverage"] == {"OANDA_REST": 2, "MT5_BRIDGE": 1}
    assert result["timeframe_coverage"] == {"M1": 2, "M5": 1}
    assert result["lifecycle_distribution"] == {"NO_SWEEP": 3}
    assert result["delivery_distribution"] == {"D_NONE": 3}
    assert result["placeholder_summary"]["snapshot_only_rows"] == 3
    assert result["lifecycle_inference"] == "NO"
    assert result["monitor_only"] is True


def test_rolling_dataset_quality_rejects_invalid_dataset(tmp_path):
    dataset = tmp_path / "bad.csv"
    dataset.write_text("event_id,ts_utc\nevent-1,2026-07-02T01:00:00Z\n", encoding="utf-8")

    result = build_rolling_dataset_quality_report(dataset)

    assert result["status"] == "ERROR"
    assert result["row_count"] == 0
    assert any("rolling dataset validation failed" in error for error in result["errors"])


def test_write_rolling_dataset_quality_report_outputs_markdown(tmp_path):
    dataset = _write_dataset(tmp_path, [_event_row()])
    result = build_rolling_dataset_quality_report(dataset)
    paths = write_rolling_dataset_quality_report(result, tmp_path / "quality")

    assert Path(paths["json"]).exists()
    md_text = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in md_text
    assert "ROW_COUNT: 1" in md_text
    assert "OANDA_REST: 1" in md_text


def test_rolling_dataset_quality_cli_writes_outputs(tmp_path):
    dataset = _write_dataset(tmp_path, [_event_row()])
    out_dir = tmp_path / "quality"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.rolling_dataset_quality_cli",
            "--dataset-csv",
            str(dataset),
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
    assert payload["row_count"] == 1
    assert Path(payload["report_paths"]["json"]).exists()
    assert Path(payload["report_paths"]["markdown"]).exists()
