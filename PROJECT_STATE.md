# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9.1 Foundation

STATUS: V91_LIFECYCLE_CANDIDATE_PROPOSAL_BRANCH
PROJECT: xauusd-market-context
UPSTREAM_SYSTEM: LFX-2 — Liquidity Field Engine
CURRENT_REPO_PACKAGE_VERSION: v2.8.0
TARGET_DEVELOPMENT_TRACK: v9.1 — Rolling Dataset Lifecycle Candidate Proposal
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

This repository has completed the v9.0 offline validation/review governance lock and the v9.1-A through v9.1-G OHLCV ingestion/review dataset scaffolds.

The current branch implements v9.1-H as a proposal-only lifecycle candidate gate:

```text
Input proposal: rolling_event_dataset.csv + rolling_dataset_quality.json
Output proposal: lifecycle_candidates.json / lifecycle_candidates.md
Implementation: NO
Inference: candidate-only proposal, no lifecycle field mutation
```

This branch does not implement a daemon loop, notification runtime, default live pipeline wiring, broker actions, Pine import, lifecycle candidate runtime, lifecycle field mutation, or execution behavior.

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
- No hidden behavior change under proposal documentation.

---

## 4. v9.1 completed gates

```text
v9.1-A — Notification bridge proposal + OHLCV data source decision: COMPLETE / MERGED
v9.1-B — OHLCV adapter implementation: COMPLETE / MERGED
v9.1-C — OHLCV Fetch CLI / Scheduler Boundary: COMPLETE / MERGED
v9.1-D — OHLCV Snapshot Validation / Source Freshness Gate: COMPLETE / MERGED
v9.1-E — OHLCV Snapshot to Event Log Draft Mapper: COMPLETE / MERGED
v9.1-F — Snapshot Event Log Append Boundary / Rolling Dataset: COMPLETE / MERGED
v9.1-G — Rolling Dataset Quality Report / Coverage Summary: COMPLETE / MERGED
```

---

## 5. Current branch scope

Allowed in this branch:

- add lifecycle candidate proposal documentation;
- define candidate-only labels;
- define evidence requirements;
- define forbidden mutation / promotion rules;
- add governance tests for proposal-only and monitor-only boundaries.

Forbidden in this branch:

- implement lifecycle candidate runtime;
- infer lifecycle / route / delivery behavior from OHLCV;
- mutate `rolling_event_dataset.csv`;
- wire proposal into default `run-once` behavior;
- add long-running daemon loop;
- implement notification runtime;
- add broker order actions;
- add MT5 order actions;
- add Pine source;
- add trading signal semantics;
- publish package/release.

---

## 6. Candidate proposal rule

```text
candidate artifact only
candidate labels are review hints only
no automatic lifecycle field overwrite
human review / patch workflow required before promotion
```

---

## 7. v9.1 next gates

```text
v9.1-H: IN PROGRESS — Rolling Dataset Lifecycle Candidate Proposal
v9.1-I: FUTURE — Lifecycle Candidate Artifact Implementation
v9.1-J: FUTURE — monitor-only notification bridge implementation requires separate approval
```

---

## 8. Current decision

```text
DECISION: Add v9.1-H lifecycle candidate proposal.
PATCH_TYPE: docs + governance tests only.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
