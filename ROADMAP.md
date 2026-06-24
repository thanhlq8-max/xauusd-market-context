# Roadmap

This roadmap tracks public utility and community adoption for the external Python repository. Every milestone remains monitor-only and must preserve the LFX external baseline contract in `docs/LFX_EXTERNAL_BASELINE.md`.

## Shipped

- `v1.8.0`: committed synthetic demo artifacts and walkthrough.
- `v1.9.0`: one-command demo, generated-file paths, CLI documentation, and CLI smoke tests.
- `v2.3.0`: community backlog, maintainer policy, feedback path, and issue triage automation.
- `v2.4.0`: synthetic real-world usage cases, sanitized report sharing, and an optional private OANDA Practice live dashboard.
- `v2.5.0`: artifact contract validation for generated JSON bundles.
- `v2.5.1`: context-summary snapshot coverage for operator-facing wording stability.
- `v2.5.2`: repository hygiene guard for generated patch/apply artifacts.
- `v2.6.0`: artifact JSON Schema validation for generated JSON bundles.
- `v2.6.1`: packaged schema fallback for wheel-installed validation.

## Explicit version decision

The maintainer explicitly authorized moving from v1.9.0 to Phase E v2.3.0. The planned Phase C v2.1.0 schema work and Phase D v2.2.0 docs-site work were skipped, not delivered under those version numbers.

Skipped-version work must not be described as complete under v2.1.0 or v2.2.0. Later shipped replacements are tracked above:

- static demo screenshot documentation shipped after v2.5.2;
- artifact JSON Schema validation shipped in v2.6.0;
- wheel-installed schema fallback shipped in v2.6.1;
- deeper nested semantic schema coverage remains future work.

## Phase F delivery

Phase F provides:

- four synthetic validation/context case studies;
- a sanitized report-sharing procedure and export-issue template;
- OANDA v20 Practice M5/M15/H1 candle ingestion with fixed five-second refresh;
- a mobile-first dashboard served from a local private host;
- explicit `NOT_INFERRED` states for MM mission and inventory claims unsupported by OHLC alone.

## Next separately locked work

The following work requires its own scope decision before implementation:

- deeper nested artifact schema coverage beyond the current top-level schema set;
- package-name decision before TestPyPI or PyPI publication;
- static documentation and demo-site expansion;
- optional local reference-data adapters;
- any external density module derived from the LFX v7.2-A-R5 reference.

## Adoption evidence

Technical releases are not adoption proof. The project will track public stars, forks, watchers, external issues, external pull requests, package downloads after publication, Pages usage when available, and documented user workflows. Artificial engagement is not acceptable evidence.


## v2.6.0 - Artifact JSON Schema Validation

Status: shipped.

- Committed JSON Schema files for the ten generated JSON artifacts.
- Integrated schema checks into `validate-artifacts`.
- Added docs/tests so schema files remain part of release readiness.
