# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9 Foundation

STATUS: V9_REVIEWER_NOTES_PATCH_WORKFLOW_BRANCH
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

The current Python package remains a monitor-only market-context sidecar. The v9 track adds repository structure, validation discipline, event dataset design, compact lifecycle primitives, replay validation, liquidity node schema, node graph replay reports, case library seeds, offline case-library CLI boundary, case review index, evidence-pack workflow, reviewer-note patch workflow, and future extension points without changing market-context artifact generation behavior.

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
- build offline case review index from generated case-library seeds;
- build evidence packs from case review index artifacts;
- apply controlled reviewer-note patches to offline case-index artifacts;
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
| Case library CLI boundary | Added in v9.0-H | Explicit offline command only |
| Case library index | Added in v9.0-I | Offline review workflow only |
| Evidence pack | Added in v9.0-J | Offline grouped review pack only |
| Reviewer notes patch workflow | Added in v9.0-K branch | Offline controlled patch only |
| Research notebooks/reports | Future | Must use generated/logged data |
| Alert bridge | Future | Monitor-only alerts first; no execution |

---

## 6. Current branch scope

This branch implements Gate K evidence pack index / reviewer notes patch workflow.

Allowed in this branch:

- add `xau_lfx.validation.review_patch`;
- add `xau_lfx.validation.review_patch_cli`;
- add committed reviewer-note patch template;
- apply controlled `review_status` / `reviewer_notes` patches to `case_index.json`;
- validate allowed review statuses;
- reject unsupported patch keys;
- write `updated_case_index.json` and `updated_case_index.md`;
- add tests and documentation.

Forbidden in this branch:

- change market-context artifact generation behavior;
- connect patch workflow to live pipeline;
- connect patch workflow to alert bridge;
- add Pine source;
- add trading signal semantics;
- add broker execution;
- publish package/release.

---

## 7. Development gates

### Gate A — Repo foundation

Status: COMPLETE / MERGED.

### Gate B — Validation dataset

Status: COMPLETE / MERGED SCAFFOLD.

### Gate C — Python engine port

Status: COMPLETE / MERGED SCAFFOLD.

### Gate D — Logged event replay harness

Status: COMPLETE / MERGED SCAFFOLD.

### Gate E — Liquidity node graph schema

Status: COMPLETE / MERGED SCAFFOLD.

### Gate F — Node graph replay integration

Status: COMPLETE / MERGED SCAFFOLD.

### Gate G — Node graph quality report / case library seed

Status: COMPLETE / MERGED SCAFFOLD.

### Gate H — Case library CLI / artifact boundary

Status: COMPLETE / MERGED SCAFFOLD.

### Gate I — Case library index / review workflow

Status: COMPLETE / MERGED SCAFFOLD.

### Gate J — Case review batch workflow / evidence pack

Status: COMPLETE / MERGED SCAFFOLD.

### Gate K — Evidence pack index / reviewer notes patch workflow

Status: IN PROGRESS.

- apply controlled reviewer-note patches to offline case-index artifacts;
- keep patch workflow auditable and monitor-only.

### Gate L — Evidence pack review cycle lock / v9.0 final governance

Status: FUTURE.

- lock offline validation/review workflow;
- document requirements before any alert bridge proposal.

### Gate M — Alert bridge

Status: FUTURE.

- only emit monitor-only states such as `TRACK_RECLAIM`, `TRACK_ACCEPT`, `D_ACTIVE`, `D_STALL`, `D_FAILED`, `TARGET_HIT`;
- no order placement.

---

## 8. Current decision

```text
DECISION: Add reviewer notes patch workflow as v9.0-K scaffold.
PATCH_TYPE: offline patch module + CLI + tests + docs + CI.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
