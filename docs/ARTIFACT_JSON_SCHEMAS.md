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

The command returns `status: OK` only when artifacts exist, required fields are present, `monitor_only` is true, schema files are usable, and schema-defined field checks pass.

## Packaged install behavior

Source distributions include the JSON files under `schemas/artifacts/`. Wheel install paths may not expose repository-root schema files, so the package also includes a built-in schema registry used only as the default fallback when the standard schema directory is unavailable.

When `--schema-dir` is supplied explicitly, missing schema files remain an error. The fallback is not used to silently fill an operator-selected schema directory.

## Packaged fallback

For wheel install usage, the validator can use the built-in schema registry packaged under `xau_lfx` when the source-tree `schemas/artifacts/` directory is not present. An explicit `--schema-dir` still requires files to exist in that selected schema directory.

## Compatibility

Schema changes must follow `docs/ARTIFACT_SCHEMA_COMPATIBILITY.md`.
