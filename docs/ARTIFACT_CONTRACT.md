# Artifact Contract

`xau-lfx validate-artifacts` checks generated JSON files against the current public artifact contract.

The command is intended for shared artifact bundles, GitHub Pages demo outputs, and user-submitted validation reports. It checks structure only. It does not score predictive value, infer direction, or validate any market outcome.

See [`ARTIFACT_SCHEMA_COMPATIBILITY.md`](ARTIFACT_SCHEMA_COMPATIBILITY.md) for the compatibility policy that separates compatible additions from breaking changes.

## Command

```bash
xau-lfx validate-artifacts --artifact-dir artifacts
```

The command exits with code `1` when a required artifact file is missing, invalid JSON is found, required top-level keys are missing, or a checked artifact does not keep `monitor_only: true`.

## Contract version

```text
1.0.0
```

This version describes the required top-level keys for the current JSON artifact set. It is not yet a full JSON Schema file set.

## Required artifact files and keys

| Artifact | Required top-level keys |
|---|---|
| `xau_raw_scan.json` | `ts_utc`, `symbol`, `monitor_only`, `source_payloads` |
| `xau_data_quality.json` | `ts_utc`, `symbol`, `monitor_only`, `freshness_score`, `coverage_score`, `schema_score`, `source_count`, `confidence_cap`, `present_timeframes`, `errors`, `quality_flags` |
| `xau_composite_ohlcv.json` | `ts_utc`, `symbol`, `monitor_only`, `timeframes`, `primary_timeframe`, `bars` |
| `xau_session_context.json` | `ts_utc`, `symbol`, `monitor_only`, `session_state`, `primary_timeframe`, `session_ranges`, `confidence_cap`, `quality_flags` |
| `xau_macro_pressure.json` | `ts_utc`, `symbol`, `monitor_only`, `pressure_state`, `drivers`, `confidence_cap`, `quality_flags` |
| `xau_event_risk_state.json` | `ts_utc`, `symbol`, `monitor_only`, `risk_state`, `event_count`, `high_impact_events`, `near_high_impact_events`, `confidence_cap`, `quality_flags` |
| `xau_lfx_external_state.json` | `ts_utc`, `symbol`, `monitor_only`, `state`, `summary`, `evidence`, `quality` |
| `xau_user_insight.json` | `ts_utc`, `symbol`, `monitor_only`, `headline`, `now_read`, `operator_focus`, `evidence_map`, `useful_limits`, `upgrade_requirements`, `quality_flags` |
| `xau_artifact_quality.json` | `ts_utc`, `symbol`, `monitor_only`, `status`, `quality_score`, `quality_grade`, `source_count`, `warnings`, `errors`, `confidence_cap` |
| `xau_context_summary.json` | `ts_utc`, `symbol`, `monitor_only`, `latest_close`, `spread_state`, `event_risk_state`, `quality_status`, `quality_grade`, `confidence_cap`, `confidence_explanation`, `monitor_focus`, `limitations`, `quality_flags` |

## Scope

The validator checks:

- file presence;
- JSON parsing;
- top-level object shape;
- required key presence;
- monitor-only flag preservation.

The validator does not check:

- statistical reliability;
- future market behavior;
- data vendor correctness beyond the emitted artifacts;
- full nested object schemas.

## Compatibility rule

Patch releases may add optional keys.

Removing a required key, changing an artifact file name, or changing the meaning of a required key requires a new contract version and a changelog note.

## Safety boundary

The contract is a data compatibility gate only. It does not convert artifacts into a trading system and does not relax the monitor-only project rules.
