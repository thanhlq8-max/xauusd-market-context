# v9.1-E — OHLCV Snapshot to Event Log Draft Mapper

STATUS: DRAFT_MAPPER_IMPLEMENTED
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate maps a validated `normalized_ohlcv.json` snapshot into draft v9 event-log rows.

It answers a narrow ingestion-preparation question:

```text
Can validated OHLCV bars be converted into schema-compatible event-log draft rows without lifecycle inference?
```

---

## 2. Implemented modules

```text
xau_lfx/connectors/snapshot_event_mapper.py
xau_lfx/connectors/snapshot_event_mapper_cli.py
```

Implemented helpers:

```text
build_event_log_draft_from_snapshot()
write_event_log_draft()
```

---

## 3. Command

```bash
python -m xau_lfx.connectors.snapshot_event_mapper_cli \
  --snapshot normalized-ohlcv/normalized_ohlcv.json \
  --validation ohlcv-validation/ohlcv_snapshot_validation.json \
  --out-dir snapshot-event-log
```

---

## 4. Outputs

```text
snapshot-event-log/snapshot_event_log_draft.csv
snapshot-event-log/snapshot_event_log_draft.json
snapshot-event-log/snapshot_event_log_validation.json
```

---

## 5. Validation precondition

The mapper requires:

```text
ohlcv_snapshot_validation.status == OK
```

If snapshot validation is not `OK`, mapping fails and no accepted draft rows are produced.

---

## 6. Mapping rule

The mapper creates schema-compatible event-log rows with:

```text
lifecycle_state = NO_SWEEP
delivery_state = D_NONE
session = UNKNOWN
sweep_side = NONE
route_dir = NONE
terminal_state = OPEN
target_hit = false
route_failed = false
```

These values mean:

```text
no lifecycle inference has been performed yet
```

They are placeholders for later reviewed/derived lifecycle workflows, not behavior conclusions.

---

## 7. Source preservation

The mapper preserves source metadata through:

```text
broker_source = source_id
review_notes contains source_id / source_type / monitor_only / no_lifecycle_inference
JSON report preserves source_id / source_type / timeframe / monitor_only
```

---

## 8. Boundary rule

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

## 9. Tests

Implemented tests:

```text
tests/test_snapshot_event_mapper.py
```

Covered cases:

```text
OK validation maps to draft rows
non-OK validation is rejected
written CSV validates with event-log validator
CLI writes CSV/JSON/validation reports
```

---

## 10. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.1-F — Snapshot Event Log Append Boundary / Rolling Dataset
```

That gate may append validated draft rows into a rolling local event dataset with duplicate protection, still monitor-only and without lifecycle inference.
