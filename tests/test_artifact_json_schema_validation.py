import json
from pathlib import Path

import xau_lfx.artifact_contract as artifact_contract_module
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


def test_default_schema_validation_falls_back_to_builtin_registry(tmp_path, monkeypatch):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)
    monkeypatch.setattr(artifact_contract_module, "ARTIFACT_SCHEMA_DIR", tmp_path / "missing-schema-dir")

    result = artifact_contract_module.validate_artifact_contract(tmp_path)

    assert result["status"] == "OK"
    assert result["checked_schema_count"] == 10
    assert {item["schema_source"] for item in result["checked_artifacts"]} == {"built_in"}


def test_explicit_missing_schema_dir_is_not_silently_filled(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)

    result = validate_artifact_contract(tmp_path, schema_dir=tmp_path / "missing-schema-dir")

    assert result["status"] == "ERROR"
    assert any("missing artifact schema" in error for error in result["schema_errors"])


def test_schema_validation_rejects_wrong_artifact_type(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)
    paths = artifact_paths(tmp_path)
    payload = json.loads(paths["artifact_quality"].read_text(encoding="utf-8"))
    payload["quality_score"] = "not-a-number"
    paths["artifact_quality"].write_text(json.dumps(payload), encoding="utf-8")

    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert any("quality_score expected JSON type number" in error for error in result["schema_errors"])


def test_schema_validation_rejects_nested_bar_value_type(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)
    paths = artifact_paths(tmp_path)
    payload = json.loads(paths["composite_ohlcv"].read_text(encoding="utf-8"))
    payload["bars"][0]["close"] = "not-a-number"
    paths["composite_ohlcv"].write_text(json.dumps(payload), encoding="utf-8")

    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert any("bars[0].close expected JSON type number" in error for error in result["schema_errors"])


def test_schema_validation_rejects_practical_zone_deck_item_value_type(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)
    paths = artifact_paths(tmp_path)
    payload = json.loads(paths["context_summary"].read_text(encoding="utf-8"))
    assert payload["practical_zone_deck"]
    payload["practical_zone_deck"][0]["distance_points"] = "not-a-number"
    paths["context_summary"].write_text(json.dumps(payload), encoding="utf-8")

    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert any("practical_zone_deck[0].distance_points expected JSON type number" in error for error in result["schema_errors"])


def test_builtin_schema_validation_rejects_practical_zone_deck_item_value_type(tmp_path, monkeypatch):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)
    monkeypatch.setattr(artifact_contract_module, "ARTIFACT_SCHEMA_DIR", tmp_path / "missing-schema-dir")
    paths = artifact_paths(tmp_path)
    payload = json.loads(paths["context_summary"].read_text(encoding="utf-8"))
    assert payload["practical_zone_deck"]
    payload["practical_zone_deck"][0]["distance_points"] = "not-a-number"
    paths["context_summary"].write_text(json.dumps(payload), encoding="utf-8")

    result = artifact_contract_module.validate_artifact_contract(tmp_path)

    assert {item["schema_source"] for item in result["checked_artifacts"]} == {"built_in"}
    assert result["status"] == "ERROR"
    assert any("practical_zone_deck[0].distance_points expected JSON type number" in error for error in result["schema_errors"])


def test_schema_files_include_nested_array_item_properties():
    schema_dir = ROOT / "schemas" / "artifacts"
    composite_schema = json.loads((schema_dir / ARTIFACT_SCHEMA_FILES["composite_ohlcv"]).read_text(encoding="utf-8"))

    bar_properties = composite_schema["properties"]["bars"]["items"]["properties"]

    assert bar_properties["ts_utc"]["type"] == "string"
    assert bar_properties["open"]["type"] == "number"
    assert bar_properties["high"]["type"] == "number"
    assert bar_properties["low"]["type"] == "number"
    assert bar_properties["close"]["type"] == "number"
    assert bar_properties["tick_volume"]["type"] == "number"
    assert bar_properties["volume_type"]["type"] == "string"


def test_context_summary_schema_includes_practical_zone_deck_item_properties():
    schema_dir = ROOT / "schemas" / "artifacts"
    context_schema = json.loads((schema_dir / ARTIFACT_SCHEMA_FILES["context_summary"]).read_text(encoding="utf-8"))

    zone_properties = context_schema["properties"]["practical_zone_deck"]["items"]["properties"]

    assert zone_properties["rank"]["type"] == "integer"
    assert zone_properties["price"]["type"] == "number"
    assert zone_properties["side_from_latest"]["enum"] == ["above", "below", "at"]
    assert zone_properties["distance_points"]["type"] == "number"
    assert zone_properties["range_points"]["type"] == ["number", "null"]
    assert zone_properties["bar_count"]["type"] == ["integer", "null"]
    assert zone_properties["operator_read"]["type"] == "string"


def test_builtin_schema_registry_matches_nested_schema_files():
    schema_dir = ROOT / "schemas" / "artifacts"
    composite_schema = json.loads((schema_dir / ARTIFACT_SCHEMA_FILES["composite_ohlcv"]).read_text(encoding="utf-8"))
    builtin_schema = artifact_contract_module.BUILTIN_ARTIFACT_SCHEMAS["composite_ohlcv"]

    assert builtin_schema["properties"]["bars"]["items"]["properties"] == composite_schema["properties"]["bars"]["items"]["properties"]
