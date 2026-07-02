# PROJECT_STATE — XAUUSD Market Context / LFX-2 v9.1 Foundation

STATUS: V91_ROLLING_EVENT_DATASET_BRANCH
PROJECT: xauusd-market-context
UPSTREAM_SYSTEM: LFX-2 — Liquidity Field Engine
CURRENT_REPO_PACKAGE_VERSION: v2.8.0
TARGET_DEVELOPMENT_TRACK: v9.1 — Monitor-only Rolling Event Dataset
PRIMARY_MODE: CONTROL
TARGET_SYMBOL: XAUUSD
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This branch implements v9.1-F as a snapshot event-log append boundary / rolling dataset gate.

```text
Input: snapshot_event_log_draft.csv
Output: rolling_event_dataset.csv + append report JSON/Markdown
Protection: duplicate event_id / ts_utc / broker_source / timeframe key
Inference: no lifecycle inference
```

The current repository role remains a monitor-only research and validation toolkit. This branch does not add live bridge behavior, order workflow, Pine source, lifecycle inference, or default pipeline wiring.

---

## 2. Completed foundation

```text
v9.0 governance lock: COMPLETE / MERGED
v9.1-A source proposal: COMPLETE / MERGED
v9.1-B OHLCV adapters: COMPLETE / MERGED
v9.1-C fetch-once CLI: COMPLETE / MERGED
v9.1-D snapshot validation: COMPLETE / MERGED
v9.1-E snapshot event-log draft mapper: COMPLETE / MERGED
```

---

## 3. Current branch scope

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
- add broker or terminal order actions;
- add Pine source;
- publish package/release.

---

## 4. Append rule

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

---

## 5. v9.1 gates

```text
v9.1-A: COMPLETE / MERGED
v9.1-B: COMPLETE / MERGED
v9.1-C: COMPLETE / MERGED
v9.1-D: COMPLETE / MERGED
v9.1-E: COMPLETE / MERGED
v9.1-F: IN PROGRESS
v9.1-G: FUTURE — Rolling Dataset Quality Report / Coverage Summary
v9.1-H: FUTURE — monitor-only notification bridge implementation requires separate approval
```

---

## 6. Current decision

```text
DECISION: Implement v9.1-F snapshot event-log append boundary / rolling dataset.
PATCH_TYPE: append module + CLI + tests + docs + CI.
RUNTIME_ARTIFACT_GENERATION_CHANGED: NO.
NEXT_ACTION: run CI, review PR, merge if clean.
```
