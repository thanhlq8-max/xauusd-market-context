# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9.1 Foundation

STATUS: V91_ROLLING_DATASET_QUALITY_BRANCH
PROJECT: xauusd-market-context
UPSTREAM_SYSTEM: LFX-2 — Liquidity Field Engine
CURRENT_REPO_PACKAGE_VERSION: v2.8.0
TARGET_DEVELOPMENT_TRACK: v9.1 — Monitor-only Rolling Dataset Quality Report
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

This repository has completed the v9.0 offline validation/review governance lock and the v9.1-A through v9.1-F OHLCV ingestion/review dataset scaffolds.

The current branch implements v9.1-G as a rolling dataset quality report / coverage summary gate:

```text
Input: rolling_event_dataset.csv
Output: rolling_dataset_quality.json / rolling_dataset_quality.md
Coverage: source, timeframe, session, lifecycle, delivery, terminal, dashboard, trader mode
Inference: no lifecycle inference
```

This branch does not implement a daemon loop, notification runtime, default live pipeline wiring, broker actions, Pine import, lifecycle inference, or execution behavior.

---

## 2. Objective lock

Build toward a practical desk-like hybrid stack for XAUUSD behavior monitoring:

```text
TradingView Pine monitor
+ Python data/event engine
+ validation dataset
+ case library
+ evidence packs
+ optional monitor-only notification bridge
```

The system must continue to answer:

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
- No hidden behavior change under quality report implementation.

---

## 4. v9.1 completed gates

```text
v9.1-A — Notification bridge proposal + OHLCV data source decision: COMPLETE / MERGED
v9.1-B — OHLCV adapter implementation: COMPLETE / MERGED
v9.1-C — OHLCV Fetch CLI / Scheduler Boundary: COMPLETE / MERGED
v9.1-D — OHLCV Snapshot Validation / Source Freshness Gate: COMPLETE / MERGED
v9.1-E — OHLCV Snapshot to Event Log Draft Mapper: COMPLETE / MERGED
v9.1-F — Snapshot Event Log Append Boundary / Rolling Dataset: COMPLETE / MERGED
```

---

## 5. Current branch scope

Allowed in this branch:

- add rolling dataset quality report module;
- add quality report CLI;
- validate rolling event dataset before reporting;
- summarize row count;
- summarize source coverage;
- summarize timeframe coverage;
- summarize session / lifecycle / delivery / terminal / dashboard / trader-mode distribution;
- summarize placeholder rows;
- write JSON/Markdown reports;
- add tests and CI quality-report command.

Forbidden in this branch:

- infer lifecycle / route / delivery behavior from OHLCV;
- wire quality reporting into default `run-once` behavior;
- add long-running daemon loop;
- implement notification runtime;
- add broker order actions;
- add MT5 order actions;
- add Pine source;
- add trading signal semantics;
- publish package/release.

---

## 6. Quality report rule

```text
rolling_event_dataset.csv → rolling_dataset_quality.json / .md
validate dataset first
summarize coverage only
no behavior conclusion
```

---

## 7. v9.1 next gates

```text
v9.1-G: IN PROGRESS — Rolling Dataset Quality Report / Coverage Summary
v9.1-H: FUTURE — Rolling Dataset Lifecycle Candidate Proposal
v9.1-I: FUTURE — monitor-only notification bridge implementation requires separate approval
```

---

## 8. Current decision

```text
DECISION: Implement v9.1-G rolling dataset quality report / coverage summary.
PATCH_TYPE: quality module + CLI + tests + docs + CI.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
