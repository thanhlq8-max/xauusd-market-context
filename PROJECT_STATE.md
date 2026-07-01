# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9 Foundation

STATUS: V9_CASE_LIBRARY_CLI_ARTIFACT_BOUNDARY_BRANCH
PROJECT: xauusd-market-context
UPSTREAM_SYSTEM: LFX-2 — Liquidity Field Engine
CURRENT_REPO_PACKAGE_VERSION: v2.8.0
TARGET_DEVELOPMENT_TRACK: v9.0 — Desk-like Hybrid Research Stack
PRIMARY_MODE: CONTROL
TARGET_SYMBOL: XAUUSD
TRADING_MODE: MONITOR_ONLY
AUTO_ENTRY: NO
BUY_SELL_SIGNAL: NO
STRATEGY_MODE: NO
REAL_MM_INVENTORY_CLAIM: NO
REAL_RETAIL_POSITIONING_CLAIM: NO
STATISTICAL_EDGE_CLAIM: NO

---

## 1. Purpose

This repository is being prepared as the GitHub foundation for a hybrid LFX-2 research/tooling stack.

The current Python package remains a monitor-only market-context sidecar. The v9 track adds repository structure, validation discipline, event dataset design, compact lifecycle primitives, replay validation, liquidity node schema, node graph replay reports, case library seeds, offline case-library CLI boundary, and future extension points without changing market-context artifact generation behavior.

Current locked LFX-2 Pine reference outside this repository:

```text
LFX-2 v8.1-D — COUNTERFLOW ROUTE ORIGIN TEXT
```

This branch does **not** add or modify the Pine source. Pine source inclusion requires a separate explicit PR and must preserve the monitor-only contract.

---

## 2. Objective lock

Build toward a practical desk-like hybrid stack for XAUUSD behavior monitoring:

```text
TradingView Pine monitor
+ Python data/event engine
+ validation dataset
+ case library
+ research reports
+ optional alert bridge
```

The system must answer these operator questions:

1. MM đã làm gì?
2. MM đang làm gì?
3. MM có thể làm gì tiếp?
4. Trader nên theo dõi gì để đi theo MM?

The repository must support those questions through auditable data, logs, and documentation. It must not become an unvalidated signal/auto-trading project.

---

## 3. Hard rules

- No BUY/SELL commands.
- No direct entry signal.
- No SL/TP instruction.
- No auto execution.
- No `strategy()` conversion as default path.
- No broker execution logic without separate explicit approval.
- No claim of real MM inventory.
- No claim of real retail positioning.
- No claim of statistical edge without a formal logged validation dataset.
- No claim of guaranteed profit.
- No hidden behavior change under documentation or validation cleanup.
- No deletion or file moves without a separate cleanup PR listing exact paths.

---

## 4. Current repository role

Current repo role:

```text
XAUUSD market-context artifact generator + validation/documentation sidecar.
```

v9 target role:

```text
Hybrid MM-behavior research and validation toolkit.
```

The correct near-term use is:

- keep the existing CSV/OANDA artifact pipeline stable;
- validate event logs before building replay/dashboards;
- port compact lifecycle primitives only under tests;
- replay logged rows against compact lifecycle outputs;
- build liquidity node graph reports from replay-validated rows;
- seed case-library summaries from node graph outputs;
- expose case-library seed generation through an offline CLI boundary;
- keep future alert bridges monitor-only.

---

## 5. Target v9 layers

| Layer | Status | Rule |
|---|---|---|
| Pine monitor | External locked reference | Do not import in this branch |
| Python artifact sidecar | Existing | Preserve artifact-generation behavior |
| Event dataset schema | Validator added in v9.0-B | No data inference claim |
| Compact lifecycle engine | Added in v9.0-C | Isolated tested primitives |
| Event replay harness | Added in v9.0-D | CLI/report only; no live connection |
| Liquidity node graph | Added in v9.0-E | Schema/scoring only; no live connection |
| Node graph replay integration | Added in v9.0-F | Offline report only; no live connection |
| Case library seed | Added in v9.0-G | Offline evidence summary only |
| Case library CLI boundary | Added in v9.0-H branch | Explicit offline command only |
| Research notebooks/reports | Future | Must use generated/logged data |
| Alert bridge | Future | Monitor-only alerts first; no execution |

---

## 6. Current branch scope

This branch implements Gate H case-library CLI / artifact boundary.

Allowed in this branch:

- add `xau_lfx.validation.case_library_cli`;
- expose case-library seed generation through `python -m xau_lfx.validation.case_library_cli`;
- write JSON/Markdown case-library seed outputs to explicit operator-selected `--out-dir`;
- add tests for CLI success and error behavior;
- add CI coverage and documentation.

Forbidden in this branch:

- change market-context artifact generation behavior;
- connect case library to live pipeline;
- connect case library to alert bridge;
- add `xau-lfx` main-pipeline command if it creates runtime coupling;
- move existing modules;
- delete current docs/tests/examples;
- add Pine source;
- add trading signal semantics;
- add broker execution;
- publish package/release.

---

## 7. Development gates

### Gate A — Repo foundation

Status: COMPLETE / MERGED.

- v9 roadmap exists.
- repo structure target exists.
- event schema draft exists.
- cleanup audit exists.
- CI passed before merge.

### Gate B — Validation dataset

Status: COMPLETE / MERGED SCAFFOLD.

- event log schema exists;
- committed synthetic template exists;
- `xau-lfx validate-event-log` exists;
- CI validates the event-log template.

### Gate C — Python engine port

Status: COMPLETE / MERGED SCAFFOLD.

- compact lifecycle primitives exist;
- route target and delivery health skeleton exist;
- tests cover core lifecycle and delivery states;
- not connected to dashboard/live pipeline.

### Gate D — Logged event replay harness

Status: COMPLETE / MERGED SCAFFOLD.

- replay compares event-log rows with compact lifecycle outputs;
- replay report exists;
- CI fails on replay mismatch;
- still no live connection.

### Gate E — Liquidity node graph schema

Status: COMPLETE / MERGED SCAFFOLD.

- node object exists;
- historical reaction fields exist;
- node scoring skeleton exists;
- clustering primitive exists;
- node graph remains outside live operation.

### Gate F — Node graph replay integration

Status: COMPLETE / MERGED SCAFFOLD.

- node updates from replay rows exist;
- node/cluster reports exist;
- reports remain descriptive and monitor-only.

### Gate G — Node graph quality report / case library seed

Status: COMPLETE / MERGED SCAFFOLD.

- curated case summaries from replay and node graph outputs exist;
- case library remains descriptive and evidence-based.

### Gate H — Case library CLI / artifact boundary

Status: IN PROGRESS.

- expose case-library generation as an explicit offline command;
- keep output under explicit artifact boundary;
- no live dashboard connection.

### Gate I — Alert bridge

Status: FUTURE.

- only emit monitor-only states such as `TRACK_RECLAIM`, `TRACK_ACCEPT`, `D_ACTIVE`, `D_STALL`, `D_FAILED`, `TARGET_HIT`;
- no order placement.

---

## 8. Current decision

```text
DECISION: Add case library CLI / artifact boundary as v9.0-H scaffold.
PATCH_TYPE: offline CLI module + tests + docs + CI.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
