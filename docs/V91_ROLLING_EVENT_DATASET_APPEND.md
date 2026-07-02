# v9.1-F — Snapshot Event Log Append Boundary / Rolling Dataset

STATUS: APPEND_BOUNDARY_IMPLEMENTED
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate appends `snapshot_event_log_draft.csv` rows into a rolling local event dataset with duplicate protection.

It answers a narrow persistence question:

```text
Can validated draft event-log rows be accumulated into a local rolling dataset without duplicating events or changing trading behavior?
```

---

## 2. Implemented modules

```text
xau_lfx/connectors/rolling_event_dataset.py
xau_lfx/connectors/rolling_event_dataset_cli.py
```

Implemented helpers:

```text
append_event_log_draft()
write_append_report()
```

---

## 3. Command

```bash
python -m xau_lfx.connectors.rolling_event_dataset_cli \
  --draft-csv snapshot-event-log/snapshot_event_log_draft.csv \
  --dataset-csv rolling-dataset/rolling_event_dataset.csv \
  --out-dir rolling-dataset
```

---

## 4. Outputs

```text
rolling-dataset/rolling_event_dataset.csv
rolling-dataset/rolling_event_append_report.json
rolling-dataset/rolling_event_append_report.md
```

---

## 5. Validation precondition

The draft CSV must pass the existing event-log validator.

By default:

```text
ERROR draft validation is rejected
WARN draft validation is allowed
```

Use `--reject-warn` when the operator wants warning states to block append.

---

## 6. Duplicate protection

Duplicate protection uses this key:

```text
event_id + ts_utc + broker_source + timeframe
```

If the key already exists in the rolling dataset, the row is skipped and counted as duplicate.

---

## 7. Boundary rule

This gate is monitor-only. It does not add:

```text
lifecycle inference
route inference
notification bridge
broker execution
MT5 order action
position sizing
account-risk automation
Pine source import
strategy behavior
```

---

## 8. Tests

Implemented tests:

```text
tests/test_rolling_event_dataset.py
```

Covered cases:

```text
new dataset creation
append to existing dataset
duplicate skip
invalid draft rejection
report writing
CLI output writing
```

---

## 9. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.1-G — Rolling Dataset Quality Report / Coverage Summary
```

That gate may summarize dataset row counts, source coverage, timeframe coverage, and validation status, still monitor-only and without lifecycle inference.
