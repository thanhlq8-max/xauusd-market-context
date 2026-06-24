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

The schemas define top-level required fields, basic JSON value types, and conservative nested object/array checks for structures already emitted by the sample artifacts. They intentionally keep additional fields compatible so artifact producers can add compatible fields without breaking downstream readers.

## Nested coverage

The v2.7.0 schema set validates nested `properties` and array `items` for existing emitted structures such as composite OHLCV bars, timeframe bars, event lists, evidence maps, and quality flag arrays. The validator reports nested paths such as `bars[0].close` when a present value has the wrong JSON type.

## Validation command

```bash
xau-lfx validate-artifacts --artifact-dir artifacts
```

The command returns `status: OK` only when artifacts exist, required fields are present, `monitor_only` is true, schema files are usable, and schema-defined field checks pass.

## Packaged install behavior

Source distributions include the JSON files under `schemas/artifacts/`. For wheel install usage, the validator can use the built-in schema registry packaged under `xau_lfx` when the source-tree schema directory is unavailable.

When `--schema-dir` is supplied explicitly, missing schema files remain an error. The built-in fallback is not used to silently fill an operator-selected schema directory.

## Compatibility

Schema changes must follow `docs/ARTIFACT_SCHEMA_COMPATIBILITY.md`.
