import json
from pathlib import Path

from xau_lfx.artifact_contract import ARTIFACT_REQUIRED_KEYS, ARTIFACT_SCHEMA_FILES, validate_artifact_contract
from xau_lfx.config import artifact_paths
from xau_lfx.pipeline import run_once


ROOT = Path(__file__).resolve().parents[1]


def test_generated_artifacts_validate_against_json_schemas(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)

    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "OK"
    assert result["checked_schema_count"] == 10
    assert result["schema_errors"] == []


def test_schema_files_match_artifact_contract_required_keys():
    schema_dir = ROOT / "schemas" / "artifacts"

    assert set(ARTIFACT_SCHEMA_FILES) == set(ARTIFACT_REQUIRED_KEYS)
    for artifact_key, schema_file in ARTIFACT_SCHEMA_FILES.items():
        payload = json.loads((schema_dir / schema_file).read_text(encoding="utf-8"))
        assert payload["required"] == list(ARTIFACT_REQUIRED_KEYS[artifact_key])
        assert payload["properties"]["monitor_only"]["const"] is True


def test_schema_validation_rejects_wrong_artifact_type(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)
    paths = artifact_paths(tmp_path)
    payload = json.loads(paths["artifact_quality"].read_text(encoding="utf-8"))
    payload["quality_score"] = "not-a-number"
    paths["artifact_quality"].write_text(json.dumps(payload), encoding="utf-8")

    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert any("quality_score expected JSON type number" in error for error in result["schema_errors"])
