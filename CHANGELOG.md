# Changelog

## Unreleased - v9 cleanup foundation

### Added

- Added root `PROJECT_STATE.md` for the LFX-2 v9 repository-governance track.
- Added `docs/V9_DESK_LIKE_HYBRID_STACK_ROADMAP.md` for the hybrid Pine + Python + validation roadmap.
- Added `docs/REPO_STRUCTURE_TARGET_v9.md` to define future repository layout without moving current runtime modules.
- Added `docs/EVENT_DATASET_SCHEMA_V9.md` as a draft event-log schema for forward validation.
- Added `docs/REPO_CLEANUP_V9.md` documenting the non-destructive cleanup decision.
- Added placeholder boundary READMEs under `data/`, `pine/`, `research/`, and `bridges/`.

### Changed

- Expanded `.gitignore` for local v9 research data, generated reports, patch/archive scratch files, and notebook checkpoints.
- Updated README navigation with v9 transition links and monitor-only boundaries.

### Preserved

- No package version change.
- No runtime calculation changes.
- No CSV ingestion, OANDA Practice dashboard, report, site, context-summary, schema validation, or artifact-generation behavior changes.
- No Pine source import.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

## v2.8.0 - Package publication preflight

### Added

- Added `docs/PACKAGE_PUBLICATION_READINESS.md` as a decision gate before TestPyPI or PyPI publication.
- Added test coverage for the package-name decision requirement, publication commands, credential boundary, and monitor-only publication contract.
- Added release-readiness checks so the publication decision document remains present and complete.

### Preserved

- No package-name change and no TestPyPI or PyPI upload automation.
- No artifact generation changes.
- No CSV ingestion, OANDA Practice dashboard, report, site, context-summary, or schema validation behavior changes.
- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.

## v2.7.0 - Deeper nested artifact schema coverage

### Changed

- Expanded artifact JSON Schemas with conservative nested `properties` and array `items` coverage derived from existing sample artifact structures.
- Added recursive schema validation for nested object and array values, including readable error paths such as `bars[0].close`.
- Kept built-in schema registry fallback aligned with the committed schema files.

### Preserved

- No artifact generation changes.
- No CSV ingestion, OANDA Practice dashboard, report, site, or context-summary behavior changes.
- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.

## v2.6.1 - Packaged schema fallback

### Changed

- Added a built-in artifact schema registry inside the Python package so wheel installs can validate artifacts when repository-root schema files are unavailable.
- Kept explicit `--schema-dir` behavior strict: a missing operator-selected schema directory remains an error.
- Added tests for built-in fallback behavior and packaged-install documentation.

### Preserved

- No artifact generation changes.
- No CSV ingestion, OANDA Practice dashboard, report, site, or context-summary behavior changes.
- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.

## v2.6.0 - Artifact JSON Schema validation

### Added

- Committed JSON Schema files for the ten generated JSON artifacts.
- Integrated schema checks into `xau-lfx validate-artifacts`.
- Added docs and tests so schema files remain part of release readiness.

### Preserved

- No artifact generation changes.
- No CSV ingestion, OANDA Practice dashboard, report, site, or context-summary behavior changes.
- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.

## v2.5.2 - Repository hygiene release gate

### Changed

- Removed generated patch/apply helper artifacts from the repository root.
- Added release-readiness blocking for root-level generated patch/apply/archive artifacts.
- Bumped package metadata consistently to `2.5.2`.

### Preserved

- No runtime calculation changes.
- No CSV ingestion, OANDA Practice dashboard, report, site, artifact contract, or context-summary behavior changes.
- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.

## v2.5.1 - Context summary snapshot coverage

### Added

- Deterministic snapshot coverage for `xau_context_summary.json` monitor-only wording and key public fields.
- Static fixture under `tests/fixtures/` for context-summary review.

### Preserved

- No runtime calculation changes.
- No CSV ingestion, OANDA Practice dashboard, report, site, or artifact contract behavior changes.
- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.

## v2.5.0 - Artifact contract validation

### Added

- `xau-lfx validate-artifacts` command for generated JSON artifact compatibility checks.
- `xau_lfx.artifact_contract` module with a stable top-level required-key contract.
- `docs/ARTIFACT_CONTRACT.md` documenting the current artifact contract and validation scope.
- CI smoke step for the artifact contract validator.
- Tests for generated sample artifacts, missing artifact handling, and CLI output.
