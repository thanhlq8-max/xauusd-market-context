import csv
import json
import subprocess
import sys
from pathlib import Path

from xau_lfx.connectors.lifecycle_candidates import build_lifecycle_candidates, write_lifecycle_candidates
from xau_lfx.connectors.rolling_dataset_quality import build_rolling_dataset_quality_report, write_rolling_dataset_quality_report
from xau_lfx.validation.event_log import EXPECTED_COLUMNS


def _event_row(event_id="event-1", ts_utc="2026-07-02T01:00:00+00:00"):
    row = {column: "" for column in EXPECTED_COLUMNS}
    row.update(
        {
            "event_id": event_id,
            "ts_utc": ts_utc,
            "symbol": "XAUUSD",
            "broker_source": "OANDA_REST",
            "timeframe": "M1",
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


def _quality_json(tmp_path: Path, dataset: Path) -> Path:
    result = build_rolling_dataset_quality_report(dataset)
    paths = write_rolling_dataset_quality_report(result, tmp_path / "quality")
    return Path(paths["json"])


def test_lifecycle_candidates_builds_review_required_candidate_artifact(tmp_path):
    dataset = _write_dataset(tmp_path, [_event_row()])
    quality = _quality_json(tmp_path, dataset)

    result = build_lifecycle_candidates(dataset_csv=dataset, quality_json=quality)

    assert result["status"] == "OK"
    assert result["candidate_count"] == 1
    assert result["candidate_state_counts"] == {"NEEDS_MANUAL_REVIEW": 1}
    assert result["dataset_mutated"] is False
    assert result["lifecycle_field_overwrite"] == "NO"
    candidate = result["candidates"][0]
    assert candidate["candidate_state"] == "NEEDS_MANUAL_REVIEW"
    assert candidate["required_review"] is True
    assert candidate["monitor_only"] is True
    assert "no_lifecycle_inference=true" in candidate["candidate_evidence"]


def test_lifecycle_candidates_rejects_bad_dataset(tmp_path):
    dataset = tmp_path / "bad.csv"
    dataset.write_text("event_id,ts_utc\nevent-1,2026-07-02T01:00:00Z\n", encoding="utf-8")
    quality = tmp_path / "quality.json"
    quality.write_text(json.dumps({"status": "OK"}), encoding="utf-8")

    result = build_lifecycle_candidates(dataset_csv=dataset, quality_json=quality)

    assert result["status"] == "ERROR"
    assert result["candidate_count"] == 0
    assert any("validation must be OK" in error for error in result["errors"])


def test_lifecycle_candidates_rejects_non_ok_quality(tmp_path):
    dataset = _write_dataset(tmp_path, [_event_row()])
    quality = tmp_path / "quality.json"
    quality.write_text(json.dumps({"status": "WARN", "warnings": ["test"]}), encoding="utf-8")

    result = build_lifecycle_candidates(dataset_csv=dataset, quality_json=quality)

    assert result["status"] == "ERROR"
    assert result["candidate_count"] == 0
    assert any("quality status must be OK" in error for error in result["errors"])


def test_write_lifecycle_candidates_outputs_json_and_markdown(tmp_path):
    dataset = _write_dataset(tmp_path, [_event_row()])
    quality = _quality_json(tmp_path, dataset)
    result = build_lifecycle_candidates(dataset_csv=dataset, quality_json=quality)
    paths = write_lifecycle_candidates(result, tmp_path / "candidates")

    assert Path(paths["json"]).exists()
    md_text = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in md_text
    assert "DATASET_MUTATED: False" in md_text
    assert "NEEDS_MANUAL_REVIEW: 1" in md_text


def test_lifecycle_candidates_cli_writes_outputs(tmp_path):
    dataset = _write_dataset(tmp_path, [_event_row()])
    quality = _quality_json(tmp_path, dataset)
    out_dir = tmp_path / "candidates"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.connectors.lifecycle_candidates_cli",
            "--dataset-csv",
            str(dataset),
            "--quality-json",
            str(quality),
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
    assert payload["candidate_count"] == 1
    assert Path(payload["report_paths"]["json"]).exists()
    assert Path(payload["report_paths"]["markdown"]).exists()
