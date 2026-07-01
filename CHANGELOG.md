# Changelog

## Unreleased - v9 case library CLI artifact boundary

### Added

- Added `xau_lfx.validation.case_library_cli` as an explicit offline command boundary for case-library seed generation.
- Added `python -m xau_lfx.validation.case_library_cli --event-log <path> --out-dir <path>` command coverage.
- Added CI coverage for building case-library seed artifacts from the committed replay template.
- Added `tests/test_case_library_cli.py` covering successful output writing and non-zero error behavior.
- Added `docs/CASE_LIBRARY_CLI_ARTIFACT_BOUNDARY_V9.md` as the CLI/artifact boundary contract.

### Preserved

- No package version change.
- No main market-context artifact-generation behavior change.
- No OANDA Practice dashboard behavior change.
- No Pine source import.
- No live pipeline connection.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

## Unreleased - v9 case library seed

### Added

- Added `xau_lfx.validation.case_library` for offline case-library seed generation from replay/node graph outputs.
- Added case summaries containing lifecycle, delivery, node, cluster, and manual-review fields.
- Added descriptive quality labels: `STRONG`, `VALID`, `WEAK`, `REVIEW`, and `REJECT`.
- Added JSON and Markdown case-library seed writer.
- Added `tests/test_case_library.py` covering successful seed generation, rejection paths, and report writing.
- Added `docs/CASE_LIBRARY_SEED_V9.md` as the case-library seed contract.

### Preserved

- No package version change.
- No artifact-generation behavior change.
- No OANDA Practice dashboard behavior change.
- No replay or node-graph behavior change.
- No Pine source import.
- No live pipeline connection.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

## Unreleased - v9 node graph replay integration

### Added

- Added `xau_lfx.validation.node_graph_replay` for offline node graph reporting from replay-validated event rows.
- Added node update derivation from trigger/source/price fields and lifecycle/delivery states.
- Added JSON and Markdown node graph report writer.
- Added `tests/test_node_graph_replay.py` covering successful node graph builds, replay rejection, mismatch rejection, and report writing.
- Added `docs/NODE_GRAPH_REPLAY_INTEGRATION_V9.md` as the node graph replay integration contract.

### Preserved

- No package version change.
- No artifact-generation behavior change.
- No OANDA Practice dashboard behavior change.
- No replay harness behavior change.
- No Pine source import.
- No live pipeline connection.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

## Unreleased - v9 liquidity node graph schema

### Added

- Added `xau_lfx.engines.liquidity_nodes` with liquidity node graph schema primitives.
- Added `LiquidityNode`, `NodeReaction`, and `NodeCluster` dataclasses.
- Added node ID normalization, reaction update, freshness aging, quality scoring, serialization, and price-band clustering helpers.
- Added `tests/test_liquidity_nodes.py` covering node creation, reaction updates, scoring, aging, serialization, clustering, and invalid input guards.
- Added `docs/LIQUIDITY_NODE_GRAPH_V9.md` as the node graph schema contract.

### Preserved

- No package version change.
- No artifact-generation behavior change.
- No OANDA Practice dashboard behavior change.
- No replay harness behavior change.
- No Pine source import.
- No live pipeline connection.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

## Unreleased - v9 event replay harness

### Added

- Added `xau_lfx.validation.event_replay` with logged event replay against compact lifecycle primitives.
- Added `xau-lfx replay-event-log --event-log <path> --out-dir <path>` CLI command.
- Added committed `data/events/event_replay_template.csv` synthetic replay template.
- Added JSON and Markdown replay report writer.
- Added `tests/test_event_replay.py` covering template replay, missing replay columns, mismatches, and report writing.
- Added CI coverage for replaying the committed replay template.
- Added `docs/EVENT_REPLAY_HARNESS_V9.md` as the replay harness contract.

### Preserved

- No package version change.
- No artifact-generation behavior change.
- No OANDA Practice dashboard behavior change.
- No Pine source import.
- No live pipeline connection.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

## Unreleased - v9 compact lifecycle engine

### Added

- Added `xau_lfx.engines.compact_lifecycle` with tested lifecycle primitives for v9 research validation.
- Added dataclasses for `Candle`, `LiquidityLevel`, `SweepLifecycle`, `RouteCandidate`, `DeliveryHealth`, and `LifecycleSnapshot`.
- Added compact behavior functions for level interaction, lifecycle classification, route target selection, and delivery health.
- Added `tests/test_compact_lifecycle.py` covering no interaction, reclaim, accept, route target, active, stall, counterflow, fail, target-hit, and monitor-only snapshot cases.
- Added `docs/COMPACT_LIFECYCLE_ENGINE_V9.md` as the module contract.

### Preserved

- No package version change.
- No artifact-generation behavior change.
- No OANDA Practice dashboard behavior change.
- No event-log validator behavior change.
- No Pine source import.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

## Unreleased - v9 event log validator

### Added

- Added `xau_lfx.validation.event_log` with a v9 forward-validation event-log CSV validator.
- Added `xau-lfx validate-event-log --event-log <path>` CLI command.
- Added committed `data/events/event_log_template.csv` synthetic template.
- Added tests for valid templates, missing required columns, sensitive columns, delivery-state conflicts, and warning states.
- Added CI coverage for validating the committed event-log template.

### Preserved

- No package version change.
- No artifact-generation behavior change.
- No OANDA Practice dashboard behavior change.
- No Pine source import.
- No trading signal, broker execution, position sizing, account-risk logic, inventory claim, or profitability claim.

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
