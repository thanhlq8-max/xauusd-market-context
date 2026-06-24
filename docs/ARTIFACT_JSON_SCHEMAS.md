# Artifact JSON Schemas

This repository ships JSON Schema files for generated monitor-only artifacts.

Schema directory:

```text
schemas/artifacts/
```

The schema set covers the same ten JSON artifacts checked by `xau-lfx validate-artifacts`:

```text
xau_raw_scan.schema.json
xau_data_quality.schema.json
xau_composite_ohlcv.schema.json
xau_session_context.schema.json
xau_macro_pressure.schema.json
xau_event_risk_state.schema.json
xau_lfx_external_state.schema.json
xau_user_insight.schema.json
xau_artifact_quality.schema.json
xau_context_summary.schema.json
```

## Scope

The schemas define top-level required fields and basic JSON value types. They intentionally remain conservative so artifact producers can add compatible fields without breaking downstream readers.

## Validation command

```bash
xau-lfx validate-artifacts --artifact-dir artifacts
```

The command returns `status: OK` only when artifacts exist, required fields are present, `monitor_only` is true, schema files are present, and schema-defined field checks pass.

## Compatibility

Schema changes must follow `docs/ARTIFACT_SCHEMA_COMPATIBILITY.md`.
