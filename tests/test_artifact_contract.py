import json

from xau_lfx.artifact_contract import ARTIFACT_CONTRACT_VERSION, validate_artifact_contract
from xau_lfx.config import artifact_paths
from xau_lfx.pipeline import run_once


def test_artifact_contract_accepts_generated_sample_artifacts(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)

    result = validate_artifact_contract(tmp_path)

    assert result["schema_contract_version"] == ARTIFACT_CONTRACT_VERSION
    assert result["status"] == "OK"
    assert result["checked_artifact_count"] == 10
    assert result["errors"] == []


def test_artifact_contract_reports_missing_files(tmp_path):
    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert result["errors"]
    assert any("missing artifact" in error for error in result["errors"])


def test_artifact_contract_rejects_missing_monitor_only_flag(tmp_path):
    paths = artifact_paths(tmp_path)
    paths["artifact_quality"].parent.mkdir(parents=True, exist_ok=True)
    paths["artifact_quality"].write_text(
        json.dumps(
            {
                "ts_utc": "2026-06-19T00:00:00+00:00",
                "symbol": "XAUUSD",
                "status": "OK",
                "quality_score": 90.0,
                "quality_grade": "A",
                "source_count": 1,
                "warnings": [],
                "errors": [],
                "confidence_cap": 0.75,
            }
        ),
        encoding="utf-8",
    )

    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert any("xau_artifact_quality.json: missing required keys: monitor_only" in error for error in result["errors"])
    assert any("xau_artifact_quality.json: monitor_only must be true" in error for error in result["errors"])
