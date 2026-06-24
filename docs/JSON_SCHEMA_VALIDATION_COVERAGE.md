# JSON Schema Validation Coverage Proposal

This document inventories the current generated JSON artifacts and proposes validation ownership for a future full JSON Schema milestone. It is documentation only. It does not add schema files, change artifact fields, change runtime calculations, or change the monitor-only project boundary.

The current enforced contract remains [`ARTIFACT_CONTRACT.md`](ARTIFACT_CONTRACT.md). Compatibility rules are defined in [`ARTIFACT_SCHEMA_COMPATIBILITY.md`](ARTIFACT_SCHEMA_COMPATIBILITY.md).

## Scope

This proposal covers the JSON files produced by `xau-lfx run-once` and `xau-lfx demo`. The Markdown report and static site are presentation outputs and are outside JSON Schema coverage.

## Validation ownership model

Future JSON Schema coverage should use three layers:

1. **Contract gate**: required files, top-level required keys, top-level object shape, and `monitor_only: true`.
2. **Artifact schema**: field types, enum-like state names where already stable, nested object shape where already documented.
3. **Fixture regression**: synthetic sample artifacts and focused fixtures for invalid source inputs.

The contract gate should stay in `xau_lfx.artifact_contract`. Full schema files, if added later, should live under a dedicated schema directory and should be exercised by tests. A later implementation issue must lock the directory name, schema dialect, and migration rule before code changes.

## Current artifact inventory

| Artifact | Current contract owner | Future validation recommendation |
|---|---|---|
| `xau_raw_scan.json` | `xau_lfx.artifact_contract` | Validate top-level source payload structure. Keep source-family details permissive because connectors may differ. |
| `xau_data_quality.json` | `xau_lfx.artifact_contract` | Validate numeric quality scores, source counts, present timeframes, errors list, and quality flags list. |
| `xau_composite_ohlcv.json` | `xau_lfx.artifact_contract` | Validate timeframe keys and bar object shape. Do not infer a centralized market feed. |
| `xau_session_context.json` | `xau_lfx.artifact_contract` | Validate session state, primary timeframe, session ranges object, confidence cap, and quality flags. |
| `xau_macro_pressure.json` | `xau_lfx.artifact_contract` | Validate pressure state, drivers list, confidence cap, and quality flags without adding directional semantics. |
| `xau_event_risk_state.json` | `xau_lfx.artifact_contract` | Validate risk state, event counts, high-impact event lists, confidence cap, and quality flags. |
| `xau_lfx_external_state.json` | `xau_lfx.artifact_contract` | Validate monitor state object shape, summary object, evidence object, and quality object. |
| `xau_user_insight.json` | `xau_lfx.artifact_contract` | Validate user-facing string/list fields and evidence map shape while preserving monitor-only language checks. |
| `xau_artifact_quality.json` | `xau_lfx.artifact_contract` | Validate status, score range, grade string, source count, warnings list, errors list, and confidence cap. |
| `xau_context_summary.json` | `xau_lfx.artifact_contract` | Validate compact summary fields and keep fixture snapshots for wording-sensitive fields. |

## Required uncertainty handling

Full schema coverage must not create fake precision. When a field is derived from weak, stale, incomplete, or user-owned source data, validation should check shape and declared limitations rather than assert unsupported certainty.

A future schema implementation should preserve these rules:

- Missing required input must remain visible as an error or quality limitation.
- Optional source families must not become required for the base run unless a separate release scope locks that change.
- Unknown external reference data must not be treated as verified source coverage.
- Validation should reject malformed structure, not upgrade weak evidence into strong evidence.

## Recommended implementation sequence

1. Add schema files for the ten current JSON artifacts.
2. Add tests that validate generated sample artifacts against those schema files.
3. Add negative tests for missing required keys and wrong top-level types.
4. Keep `xau-lfx validate-artifacts` backward compatible unless a new contract version is explicitly released.
5. Document every schema addition in the changelog and compatibility policy.

## Acceptance for a future implementation issue

A future full schema implementation is acceptable only when:

- every current JSON artifact has a schema file;
- generated sample artifacts validate cleanly;
- schema tests run in CI;
- compatibility rules are updated if required;
- no runtime calculation changes are bundled into the schema patch;
- monitor-only language checks remain active.
