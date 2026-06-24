# Artifact Schema Compatibility Policy

This document defines compatibility rules for generated JSON artifacts. It is documentation only. It does not change artifact fields, validator behavior, runtime calculations, or the monitor-only project boundary.

The earlier v2.1.0 schema implementation milestone is treated as skipped and not delivered. Current compatibility enforcement is the top-level artifact contract documented in [`ARTIFACT_CONTRACT.md`](ARTIFACT_CONTRACT.md).

## Scope

This policy applies to generated JSON artifacts emitted by `xau-lfx run-once` and `xau-lfx demo`:

- `xau_raw_scan.json`
- `xau_data_quality.json`
- `xau_composite_ohlcv.json`
- `xau_session_context.json`
- `xau_macro_pressure.json`
- `xau_event_risk_state.json`
- `xau_lfx_external_state.json`
- `xau_user_insight.json`
- `xau_artifact_quality.json`
- `xau_context_summary.json`

The Markdown report and static site are presentation outputs. Their wording may evolve independently, but they must preserve the same public safety boundary.

## Compatible changes

These changes are compatible when existing required keys keep their meaning:

- adding a new optional top-level key;
- adding a new optional nested key;
- adding a new non-required artifact file;
- adding a new warning, limitation, or quality flag value;
- improving wording inside user-facing explanation fields while preserving monitor-only meaning;
- tightening validation so invalid input is rejected earlier with a clearer error.

Compatible additions should be documented in the changelog when they are user-visible.

## Breaking changes

These changes are breaking and require a new artifact contract version plus a changelog note:

- removing a required artifact file;
- renaming a required artifact file;
- removing a required top-level key;
- renaming a required top-level key;
- changing the meaning of a required key;
- changing a required key from scalar to object, object to list, or list to scalar;
- replacing monitor-only source-quality context with decision automation semantics;
- silently treating missing source data as valid source coverage.

A breaking change must not be hidden inside a patch release.

## Contract versioning guidance

Use the artifact contract version to communicate compatibility expectations:

- patch change: compatible optional addition or wording clarification;
- minor change: new required artifact or new required top-level key with migration notes;
- major change: removal, rename, or semantic change to required artifacts or required keys.

The package version and artifact contract version do not have to be identical, but release notes should explain their relationship when the artifact contract changes.

## Required release checklist

Before a release that changes artifacts or artifact docs:

1. Run `xau-lfx demo` from committed synthetic fixtures.
2. Run `xau-lfx validate-artifacts --artifact-dir artifacts`.
3. Update `ARTIFACT_CONTRACT.md` when required keys or required files change.
4. Update this document when compatibility rules change.
5. Add or update tests that protect required files, required top-level keys, and monitor-only flags.
6. Add changelog notes for user-visible compatibility changes.

## Non-goals

This policy does not introduce full JSON Schema files. Full schema coverage should be handled by a separately locked issue with explicit ownership, validation scope, and migration rules.

This policy does not score market outcomes. Artifact compatibility is a data-interface concern only.
