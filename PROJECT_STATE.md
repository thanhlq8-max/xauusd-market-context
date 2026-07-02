# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9.1 Foundation

STATUS: V91_OHLCV_SNAPSHOT_VALIDATION_BRANCH
PROJECT: xauusd-market-context
UPSTREAM_SYSTEM: LFX-2 — Liquidity Field Engine
CURRENT_REPO_PACKAGE_VERSION: v2.8.0
TARGET_DEVELOPMENT_TRACK: v9.1 — Monitor-only OHLCV Snapshot Validation
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

This repository has completed the v9.0 offline validation/review governance lock, v9.1-A source proposal, v9.1-B OHLCV adapter implementation, and v9.1-C fetch-once CLI boundary.

The current branch implements v9.1-D as a snapshot validation and source freshness gate:

```text
Input: normalized_ohlcv.json
Output: ohlcv_snapshot_validation.json / ohlcv_snapshot_validation.md
Checks: source status, complete rows, duplicate timestamps, freshness threshold
```

This branch does not implement a daemon loop, notification runtime, default live pipeline wiring, broker actions, Pine import, or execution behavior.

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
- No hidden behavior change under snapshot validation implementation.

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

- add snapshot validation module;
- add snapshot validation CLI;
- write `ohlcv_snapshot_validation.json` and `.md`;
- validate source status `OK` / `WARN`;
- validate `is_complete=true` rows;
- detect duplicate `ts_utc` values;
- validate freshness with timeframe defaults or explicit `--max-age-seconds`;
- document fixture-only freshness skip;
- add tests and CI fixture validation command.

Forbidden in this branch:

- wire snapshot validation into default `run-once` behavior;
- add long-running daemon loop;
- implement notification runtime;
- add broker order actions;
- add MT5 order actions;
- add Pine source;
- add trading signal semantics;
- publish package/release.

---

## 7. Freshness thresholds

```text
M1: 180 seconds
M5: 600 seconds
M15: 1800 seconds
H1: 7200 seconds
```

Operators may override with `--max-age-seconds`.

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

Status: IN PROGRESS.

- validate snapshot freshness;
- detect duplicate timestamps;
- require source status OK/WARN before downstream use.

### v9.1-E — OHLCV Snapshot to Event Log Draft Mapper

Status: FUTURE.

- create draft event-log rows from validated snapshots;
- no notification or execution behavior.

### v9.1-F — Monitor-only notification bridge implementation

Status: FUTURE / REQUIRES SEPARATE APPROVAL.

---

## 10. Current decision

```text
DECISION: Implement v9.1-D OHLCV snapshot validation / source freshness gate.
PATCH_TYPE: validation module + CLI + tests + docs + CI.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
