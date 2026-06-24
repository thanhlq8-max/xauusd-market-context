# Optional Local Reference Data Adapter Contract

This document proposes rules for future optional local reference CSV adapters. It is documentation only. It does not add an adapter, change the base run, change generated artifacts, or add remote collection.

Primary boundary reference: [`LFX_EXTERNAL_BASELINE.md`](LFX_EXTERNAL_BASELINE.md).

## Scope

A future adapter may read user-owned, synthetic, or rights-cleared CSV files from an explicit local path. The current base pipeline must continue to work when no reference file is present.

Reference data is optional context only. It must stay subordinate to source validation, artifact quality, and the monitor-only project boundary.

## Required contract

Any future implementation must define all of the following before code is added:

| Area | Requirement |
|---|---|
| Source rights | Files must be user-owned, synthetic, or rights-cleared for the intended local use. Repository fixtures must be synthetic or explicitly rights-cleared. |
| File path | The user must provide the directory or file path explicitly. Missing optional files must not block the base run. |
| Timezone | Timestamp columns must be documented and normalized to UTC before artifact generation. |
| Freshness | The adapter must expose freshness age or a freshness limitation. Stale reference data must remain visible as limited context. |
| Schema | Required columns, numeric fields, timestamp format, and ordering rules must be documented and tested. |
| Validation | Malformed rows must be reported as errors or limitations. Missing values must not be silently filled. |
| Confidence impact | Weak, stale, missing, or inconsistent reference data may reduce confidence. It must not upgrade weak core evidence. |
| Artifact impact | New artifact keys or new required fields must follow the artifact compatibility policy. |

## Candidate local CSV families

Future proposals may consider these local CSV families only after a separate scope is locked:

- local futures-reference CSV;
- local macro proxy CSV;
- local rate or index reference CSV;
- local session or calendar reference CSV.

Each family must document what the file represents, what it does not represent, and what limitations should appear in generated outputs.

## Base-run preservation rule

The base run must remain valid with the current required local CSV fixtures. Optional reference data absence must be treated as unavailable optional context only when a future feature explicitly reports it. Absence must not become a blocker for users who only want the current local XAUUSD context artifacts.

## Future implementation acceptance

A future implementation issue is acceptable only when it includes:

1. exact CSV columns;
2. explicit UTC handling;
3. malformed fixture tests;
4. source-rights documentation;
5. confidence-impact documentation;
6. artifact compatibility review;
7. release-readiness updates when required;
8. no change to base-run behavior when optional data is absent.
