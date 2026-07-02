# v9.1-D — OHLCV Snapshot Validation / Source Freshness Gate

STATUS: SNAPSHOT_VALIDATION_IMPLEMENTED
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate validates `normalized_ohlcv.json` before any downstream review tooling uses the snapshot.

It answers a narrow ingestion-control question:

```text
Is this normalized OHLCV snapshot complete, source-labeled, non-duplicated, and fresh enough to be accepted for monitor-only review workflows?
```

---

## 2. Implemented modules

```text
xau_lfx/connectors/candle_snapshot.py
xau_lfx/connectors/candle_snapshot_cli.py
```

Implemented helpers:

```text
validate_ohlcv_snapshot()
write_snapshot_validation()
```

---

## 3. Command

```bash
python -m xau_lfx.connectors.candle_snapshot_cli \
  --snapshot normalized-ohlcv/normalized_ohlcv.json \
  --out-dir ohlcv-validation \
  --max-age-seconds 180
```

Fixture/dry-run mode may bypass freshness only for static samples:

```bash
python -m xau_lfx.connectors.candle_snapshot_cli \
  --snapshot normalized-ohlcv/normalized_ohlcv.json \
  --out-dir ohlcv-validation \
  --skip-freshness-check
```

---

## 4. Outputs

```text
ohlcv-validation/ohlcv_snapshot_validation.json
ohlcv-validation/ohlcv_snapshot_validation.md
```

---

## 5. Validation checks

The validator checks:

```text
source status must be OK or WARN
snapshot monitor_only must be true
rows must exist
row monitor_only must be true
row is_complete must be true
row timeframe must match snapshot timeframe
ts_utc must exist and be timezone-aware
duplicate ts_utc is rejected
freshness is checked unless explicitly skipped
```

---

## 6. Default freshness thresholds

```text
M1: 180 seconds
M5: 600 seconds
M15: 1800 seconds
H1: 7200 seconds
```

Operators may override with `--max-age-seconds`.

---

## 7. Boundary rule

This gate is monitor-only. It does not add:

```text
default run-once pipeline wiring
long-running daemon
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
tests/test_candle_snapshot.py
```

Covered cases:

```text
fresh completed rows accepted
incomplete rows rejected
duplicate timestamps rejected
stale snapshot rejected
source WARN accepted with warning
CLI writes JSON and Markdown reports
```

---

## 9. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.1-E — OHLCV Snapshot to Event Log Draft Mapper
```

That gate may create a draft event-log row source from validated snapshots, still monitor-only and without notification or execution behavior.
