# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9.1 Foundation

STATUS: V91_NOTIFICATION_BRIDGE_PROPOSAL_BRANCH
PROJECT: xauusd-market-context
UPSTREAM_SYSTEM: LFX-2 — Liquidity Field Engine
CURRENT_REPO_PACKAGE_VERSION: v2.8.0
TARGET_DEVELOPMENT_TRACK: v9.1 — Monitor-only Notification Bridge Proposal
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

This repository has completed the v9.0 offline validation/review governance lock. The current branch starts v9.1-A as a proposal-only step for a future monitor-only notification bridge and OHLCV data-source decision.

This branch does not implement notification runtime, live data ingestion, broker actions, Pine import, or execution behavior.

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
- No hidden behavior change under documentation or validation cleanup.

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

## 5. v9.1-A current scope

Allowed in this branch:

- add notification bridge proposal document;
- add OHLCV data source decision document;
- add data input adapter contract proposal;
- add tests that enforce proposal-only and monitor-only boundaries;
- update project state and changelog.

Forbidden in this branch:

- implement notification runtime;
- connect live feeds;
- add broker API actions;
- add MT5 order actions;
- add Pine source;
- add trading signal semantics;
- add broker execution;
- publish package/release.

---

## 6. OHLCV data source decision

Current proposal decision:

```text
Primary candidate: broker REST API source, with OANDA REST candles first.
Secondary candidate: MT5 Python bridge for broker-feed parity.
Fallback candidate: external vendor REST API for independent reference only.
```

Reason:

```text
Broker REST is best for unattended cloud refresh.
MT5 is best for matching the trader's execution broker chart.
Vendor API is useful as backup/reference but not broker-feed-equivalent.
```

Volume rule:

```text
XAUUSD volume must be treated as tick count / quote activity / source-specific proxy, not centralized traded volume.
```

---

## 7. v9.1 development gates

### v9.1-A — Notification bridge proposal + OHLCV data source decision

Status: IN PROGRESS.

- proposal only;
- docs/tests only;
- no runtime implementation.

### v9.1-B — OHLCV adapter implementation

Status: FUTURE / REQUIRES SOURCE SELECTION.

The user must select one primary source before implementation:

```text
A. OANDA REST primary
B. MT5 Python bridge primary
C. vendor REST primary
```

### v9.1-C — Monitor-only notification bridge implementation

Status: FUTURE / REQUIRES SEPARATE APPROVAL.

---

## 8. Current decision

```text
DECISION: Add v9.1-A proposal documents for notification bridge and OHLCV source selection.
PATCH_TYPE: docs + tests only.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
