# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9.1 Foundation

STATUS: V91_ROLLING_EVENT_DATASET_BRANCH
PROJECT: xauusd-market-context
UPSTREAM_SYSTEM: LFX-2 — Liquidity Field Engine
CURRENT_REPO_PACKAGE_VERSION: v2.8.0
TARGET_DEVELOPMENT_TRACK: v9.1 — Monitor-only Rolling Event Dataset
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

This repository has completed the v9.0 offline validation/review governance lock, v9.1-A source proposal, v9.1-B OHLCV adapter implementation, v9.1-C fetch-once CLI boundary, v9.1-D snapshot validation gate, and v9.1-E snapshot event-log draft mapper.

The current branch implements v9.1-F as a snapshot event-log append boundary / rolling dataset gate:

```text
Input: snapshot_event_log_draft.csv
Output: rolling_event_dataset.csv + append report JSON/Markdown
Protection: duplicate event_id / ts_utc / broker_source / timeframe key
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
- No hidden behavior change under rolling dataset implementation.

---

## 4. v9.0 locked foundation

Completed and merged gates:

```text
Gate A — Repo foundation
Gate B — Event log validator
Gate C — Compact lifecycle primitives
Gate D — Event replay harness
Gate E — Liquidity node graph schema
Gate F — Node graph replay integration
Gate G — Case library seed
Gate H — Case library CLI / artifact boundary
Gate I — Case library index / review workflow
Gate J — Evidence pack workflow
Gate K — Reviewer notes patch workflow
Gate L — v9.0 final governance lock
```

---

## 5. v9.1 source path

Selected implementation path:

```text
A. OANDA REST primary
B. MT5 Python bridge secondary
```

Not selected as primary:

```text
C. vendor REST primary
```

---

## 6. Current branch scope

Allowed in this branch:

- add rolling event dataset append module;
- add append CLI;
- validate draft event-log CSV before append;
- append valid draft rows into `rolling_event_dataset.csv`;
- skip duplicate rows by `event_id + ts_utc + broker_source + timeframe`;
- write append report JSON/Markdown;
- add tests and CI fixture append command.

Forbidden in this branch:

- infer lifecycle / route / delivery behavior from OHLCV;
- wire rolling dataset into default `run-once` behavior;
- add long-running daemon loop;
- implement notification runtime;
- add broker order actions;
- add MT5 order actions;
- add Pine source;
- add trading signal semantics;
- publish package/release.

---

## 7. Append rule

```text
snapshot_event_log_draft.csv → rolling_event_dataset.csv
validate draft first
append only non-duplicate rows
validate output dataset after append
write report
```

Duplicate key:

```text
event_id + ts_utc + broker_source + timeframe
```

The append workflow creates a local rolling research dataset. It does not infer behavior conclusions.

---

## 8. Volume rule

```text
XAUUSD tick_volume = quote activity / source-specific activity proxy.
It is not centralized traded volume.
```

---

## 9. v9.1 development gates

### v9.1-A — Notification bridge proposal + OHLCV data source decision

Status: COMPLETE / MERGED.

### v9.1-B — OHLCV adapter implementation

Status: COMPLETE / MERGED.

### v9.1-C — OHLCV Fetch CLI / Scheduler Boundary

Status: COMPLETE / MERGED.

### v9.1-D — OHLCV Snapshot Validation / Source Freshness Gate

Status: COMPLETE / MERGED.

### v9.1-E — OHLCV Snapshot to Event Log Draft Mapper

Status: COMPLETE / MERGED.

### v9.1-F — Snapshot Event Log Append Boundary / Rolling Dataset

Status: IN PROGRESS.

- append validated draft rows into a rolling local event dataset;
- duplicate protection;
- no lifecycle inference.

### v9.1-G — Rolling Dataset Quality Report / Coverage Summary

Status: FUTURE.

- summarize dataset row counts;
- summarize source and timeframe coverage;
- no lifecycle inference.

### v9.1-H — Monitor-only notification bridge implementation

Status: FUTURE / REQUIRES SEPARATE APPROVAL.

---

## 10. Current decision

```text
DECISION: Implement v9.1-F snapshot event-log append boundary / rolling dataset.
PATCH_TYPE: append module + CLI + tests + docs + CI.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
