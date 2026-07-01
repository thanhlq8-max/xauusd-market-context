# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9 Foundation

STATUS: V9_REPO_CLEANUP_FOUNDATION_BRANCH
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

This repository is being cleaned and prepared as the GitHub foundation for a hybrid LFX-2 research/tooling stack.

The current Python package remains a monitor-only market-context sidecar. The v9 track adds repository structure, validation discipline, event dataset design, and future extension points without changing runtime behavior in this cleanup branch.

Current locked LFX-2 Pine reference outside this repository:

```text
LFX-2 v8.1-D — COUNTERFLOW ROUTE ORIGIN TEXT
```

This cleanup branch does **not** add or modify the Pine source. Pine source inclusion requires a separate explicit PR and must preserve the monitor-only contract.

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
- No hidden behavior change under documentation cleanup.
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
- add v9 documentation and data schema;
- define future module boundaries;
- collect forward-validation cases;
- only port Pine logic into Python modules after schema and validation contracts are locked.

---

## 5. Target v9 layers

| Layer | Status | Rule |
|---|---|---|
| Pine monitor | External locked reference | Do not import in this cleanup branch |
| Python artifact sidecar | Existing | Preserve runtime behavior |
| Event dataset schema | Added as documentation | No data inference claim |
| Liquidity node graph | Future | Implement only after event schema lock |
| Research notebooks/reports | Future | Must use generated/logged data |
| Alert bridge | Future | Monitor-only alerts first; no execution |

---

## 6. Current cleanup scope

This branch is documentation and repository hygiene only.

Allowed in this branch:

- add project-state pointer;
- add v9 roadmap;
- add target repo structure;
- add event schema draft;
- add local artifact ignore rules;
- add placeholder README files for future directories;
- update README navigation.

Forbidden in this branch:

- change Python package behavior;
- move existing modules;
- delete current docs/tests/examples;
- add Pine source;
- add trading signal semantics;
- publish package/release.

---

## 7. Next development gates

### Gate A — Repo foundation

- v9 roadmap exists.
- repo structure target exists.
- event schema draft exists.
- cleanup audit exists.
- CI still passes.

### Gate B — Validation dataset

- create logged event cases from live sessions;
- record MFE/MAE/time-to-resolution;
- separate screenshots from derived metrics;
- avoid edge/profit claims until sample is sufficient.

### Gate C — Python engine port

- port only compact v8.1-D lifecycle primitives;
- keep Pine and Python output comparable;
- add tests before any dashboard claims.

### Gate D — Alert bridge

- only emit monitor-only states such as `TRACK_RECLAIM`, `TRACK_ACCEPT`, `D_ACTIVE`, `D_STALL`, `D_FAILED`, `TARGET_HIT`;
- no order placement.

---

## 8. Current decision

```text
DECISION: Prepare repository for v9 through non-destructive cleanup.
PATCH_TYPE: documentation + hygiene only.
RUNTIME_BEHAVIOR_CHANGED: NO.
NEXT_ACTION: review PR, run CI, then merge if clean.
```
