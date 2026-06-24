from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from xau_lfx.artifact_schema_registry import BUILTIN_ARTIFACT_SCHEMAS
from xau_lfx.config import PACKAGE_ROOT, artifact_paths
from xau_lfx.forbidden_language import assert_clean_language


ARTIFACT_CONTRACT_VERSION = "1.0.0"
ARTIFACT_SCHEMA_SET_VERSION = "1.0.0"
ARTIFACT_SCHEMA_DIR = PACKAGE_ROOT / "schemas" / "artifacts"

ARTIFACT_REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "raw_scan": ("ts_utc", "symbol", "monitor_only", "source_payloads"),
    "data_quality": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "freshness_score",
        "coverage_score",
        "schema_score",
        "source_count",
        "confidence_cap",
        "present_timeframes",
        "errors",
        "quality_flags",
    ),
    "composite_ohlcv": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "timeframes",
        "primary_timeframe",
        "bars",
    ),
    "session_context": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "session_state",
        "primary_timeframe",
        "session_ranges",
        "confidence_cap",
        "quality_flags",
    ),
    "macro_pressure": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "pressure_state",
        "drivers",
        "confidence_cap",
        "quality_flags",
    ),
    "event_risk": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "risk_state",
        "event_count",
        "high_impact_events",
        "near_high_impact_events",
        "confidence_cap",
        "quality_flags",
    ),
    "state": ("ts_utc", "symbol", "monitor_only", "state", "summary", "evidence", "quality"),
    "user_insight": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "headline",
        "now_read",
        "operator_focus",
        "evidence_map",
        "useful_limits",
        "upgrade_requirements",
        "quality_flags",
    ),
    "artifact_quality": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "status",
        "quality_score",
        "quality_grade",
        "source_count",
        "warnings",
        "errors",
        "confidence_cap",
    ),
    "context_summary": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "latest_close",
        "spread_state",
        "event_risk_state",
        "quality_status",
        "quality_grade",
        "confidence_cap",
        "confidence_explanation",
        "monitor_focus",
        "limitations",
        "quality_flags",
    ),
}

ARTIFACT_SCHEMA_FILES: dict[str, str] = {
    "raw_scan": "xau_raw_scan.schema.json",
    "data_quality": "xau_data_quality.schema.json",
    "composite_ohlcv": "xau_composite_ohlcv.schema.json",
    "session_context": "xau_session_context.schema.json",
    "macro_pressure": "xau_macro_pressure.schema.json",
    "event_risk": "xau_event_risk_state.schema.json",
    "state": "xau_lfx_external_state.schema.json",
    "user_insight": "xau_user_insight.schema.json",
    "artifact_quality": "xau_artifact_quality.schema.json",
    "context_summary": "xau_context_summary.schema.json",
}

_JSON_TYPE_NAMES = ("object", "array", "string", "number", "integer", "boolean", "null")


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name}: invalid JSON at line {exc.lineno} column {exc.colno}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name}: top-level JSON value must be an object")
    return payload


def _schema_path(artifact_key: str, schema_dir: str | Path | None = None) -> Path:
    root = Path(schema_dir) if schema_dir is not None else ARTIFACT_SCHEMA_DIR
    return root / ARTIFACT_SCHEMA_FILES[artifact_key]


def _load_schema_document(
    artifact_key: str,
    schema_dir: str | Path | None = None,
) -> tuple[dict[str, Any], str, str]:
    schema_path = _schema_path(artifact_key, schema_dir=schema_dir)
    if schema_path.exists():
        return _read_json_object(schema_path), schema_path.name, "file"

    if schema_dir is not None:
        raise ValueError(f"{schema_path.name}: missing artifact schema")

    builtin_schema = BUILTIN_ARTIFACT_SCHEMAS.get(artifact_key)
    if not isinstance(builtin_schema, dict):
        raise ValueError(f"{schema_path.name}: missing built-in artifact schema")
    return copy.deepcopy(builtin_schema), schema_path.name, "built_in"


def _type_names(type_value: Any) -> tuple[str, ...]:
    if isinstance(type_value, str):
        return (type_value,)
    if isinstance(type_value, list) and all(isinstance(item, str) for item in type_value):
        return tuple(type_value)
    return ()


def _json_type_matches(value: Any, allowed_types: tuple[str, ...]) -> bool:
    for allowed in allowed_types:
        if allowed == "object" and isinstance(value, dict):
            return True
        if allowed == "array" and isinstance(value, list):
            return True
        if allowed == "string" and isinstance(value, str):
            return True
        if allowed == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if allowed == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if allowed == "boolean" and isinstance(value, bool):
            return True
        if allowed == "null" and value is None:
            return True
    return False


def _format_schema_path(parent: str, child: str) -> str:
    return f"{parent}.{child}" if parent else child


def _validate_schema_fragment(schema: dict[str, Any], schema_file: str, path: str) -> list[str]:
    errors: list[str] = []
    allowed = _type_names(schema.get("type"))
    if allowed and any(name not in _JSON_TYPE_NAMES for name in allowed):
        errors.append(f"{schema_file}: schema fragment {path or '$'} has unsupported JSON type")

    properties = schema.get("properties")
    if properties is not None:
        if not isinstance(properties, dict):
            errors.append(f"{schema_file}: schema fragment {path or '$'} properties must be an object")
        else:
            for key, child_schema in properties.items():
                child_path = _format_schema_path(path, key)
                if not isinstance(child_schema, dict):
                    errors.append(f"{schema_file}: schema fragment {child_path} must be an object")
                else:
                    errors.extend(_validate_schema_fragment(child_schema, schema_file, child_path))

    items = schema.get("items")
    if items is not None:
        item_path = f"{path or '$'}[]"
        if not isinstance(items, dict):
            errors.append(f"{schema_file}: schema fragment {item_path} items must be an object")
        else:
            errors.extend(_validate_schema_fragment(items, schema_file, item_path))
    return errors


def _validate_schema_document(artifact_key: str, schema: dict[str, Any], schema_file: str) -> list[str]:
    errors: list[str] = []
    if schema.get("type") != "object":
        errors.append(f"{schema_file}: schema type must be object")

    required = schema.get("required")
    expected_required = list(ARTIFACT_REQUIRED_KEYS[artifact_key])
    if required != expected_required:
        errors.append(f"{schema_file}: required keys do not match artifact contract")

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        errors.append(f"{schema_file}: properties must be an object")
        return errors

    for key in expected_required:
        if key not in properties:
            errors.append(f"{schema_file}: required key {key} is missing from properties")
            continue
        property_schema = properties[key]
        if not isinstance(property_schema, dict):
            errors.append(f"{schema_file}: property {key} schema must be an object")
            continue
        errors.extend(_validate_schema_fragment(property_schema, schema_file, key))

    monitor_schema = properties.get("monitor_only", {})
    if isinstance(monitor_schema, dict) and monitor_schema.get("const") is not True:
        errors.append(f"{schema_file}: monitor_only must declare const true")
    return errors


def _validate_value_against_schema(file_name: str, path: str, value: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{file_name}: {path} must equal {schema['const']!r}")
    enum_values = schema.get("enum")
    if isinstance(enum_values, list) and value not in enum_values:
        errors.append(f"{file_name}: {path} must be one of {enum_values!r}")

    allowed_types = _type_names(schema.get("type"))
    if allowed_types and not _json_type_matches(value, allowed_types):
        errors.append(f"{file_name}: {path} expected JSON type {'/'.join(allowed_types)}")
        return errors

    properties = schema.get("properties")
    if isinstance(value, dict) and isinstance(properties, dict):
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                errors.extend(_validate_value_against_schema(file_name, _format_schema_path(path, key), value[key], child_schema))

    items = schema.get("items")
    if isinstance(value, list) and isinstance(items, dict):
        for index, item in enumerate(value):
            errors.extend(_validate_value_against_schema(file_name, f"{path}[{index}]", item, items))
    return errors


def _validate_payload_with_schema(file_name: str, payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    if not isinstance(required, list) or not isinstance(properties, dict):
        return [f"{file_name}: schema is not usable for payload validation"]

    for key in required:
        if key not in payload:
            errors.append(f"{file_name}: schema missing required key: {key}")

    for key, property_schema in properties.items():
        if key not in payload or not isinstance(property_schema, dict):
            continue
        errors.extend(_validate_value_against_schema(file_name, key, payload[key], property_schema))
    return errors


def validate_artifact_contract(
    artifact_dir: str | Path,
    schema_dir: str | Path | None = None,
) -> dict[str, Any]:
    paths = artifact_paths(artifact_dir)
    contract_errors: list[str] = []
    schema_errors: list[str] = []
    checked_artifacts: list[dict[str, Any]] = []
    checked_schema_count = 0

    for artifact_key, required_keys in ARTIFACT_REQUIRED_KEYS.items():
        path = paths[artifact_key]
        schema_path = _schema_path(artifact_key, schema_dir=schema_dir)
        checked = {
            "artifact_key": artifact_key,
            "file": path.name,
            "schema_file": schema_path.name,
            "schema_source": None,
            "required_keys": list(required_keys),
            "missing_keys": [],
            "schema_errors": [],
        }
        checked_artifacts.append(checked)

        schema: dict[str, Any] | None = None
        try:
            schema, schema_file, schema_source = _load_schema_document(artifact_key, schema_dir=schema_dir)
        except ValueError as exc:
            schema_errors.append(str(exc))
            checked["schema_errors"].append(str(exc))
        else:
            checked_schema_count += 1
            checked["schema_file"] = schema_file
            checked["schema_source"] = schema_source
            schema_doc_errors = _validate_schema_document(artifact_key, schema, schema_file)
            schema_errors.extend(schema_doc_errors)
            checked["schema_errors"].extend(schema_doc_errors)

        if not path.exists():
            contract_errors.append(f"{path.name}: missing artifact")
            continue

        try:
            payload = _read_json_object(path)
        except ValueError as exc:
            contract_errors.append(str(exc))
            continue

        missing_keys = [key for key in required_keys if key not in payload]
        checked["missing_keys"] = missing_keys
        if missing_keys:
            contract_errors.append(f"{path.name}: missing required keys: {', '.join(missing_keys)}")
        if payload.get("monitor_only") is not True:
            contract_errors.append(f"{path.name}: monitor_only must be true")
        if schema is not None:
            payload_schema_errors = _validate_payload_with_schema(path.name, payload, schema)
            schema_errors.extend(payload_schema_errors)
            checked["schema_errors"].extend(payload_schema_errors)

    all_errors = contract_errors + schema_errors
    result = {
        "schema_contract_version": ARTIFACT_CONTRACT_VERSION,
        "artifact_schema_set_version": ARTIFACT_SCHEMA_SET_VERSION,
        "status": "ERROR" if all_errors else "OK",
        "artifact_dir": str(Path(artifact_dir)),
        "checked_artifact_count": len(checked_artifacts),
        "checked_schema_count": checked_schema_count,
        "checked_artifacts": checked_artifacts,
        "errors": all_errors,
        "contract_errors": contract_errors,
        "schema_errors": schema_errors,
    }
    assert_clean_language(result)
    return result
