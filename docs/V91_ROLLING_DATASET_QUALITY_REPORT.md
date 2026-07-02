# v9.1-G — Rolling Dataset Quality Report / Coverage Summary

STATUS: QUALITY_REPORT_IMPLEMENTED
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate summarizes a rolling event dataset after draft OHLCV rows have been appended.

It answers a narrow dataset-control question:

```text
What source, timeframe, session, lifecycle, and delivery coverage exists in the rolling local event dataset?
```

The report is descriptive only. It does not infer behavior and does not rank future outcomes.

---

## 2. Implemented modules

```text
xau_lfx/connectors/rolling_dataset_quality.py
xau_lfx/connectors/rolling_dataset_quality_cli.py
```

Implemented helpers:

```text
build_rolling_dataset_quality_report()
write_rolling_dataset_quality_report()
```

---

## 3. Command

```bash
python -m xau_lfx.connectors.rolling_dataset_quality_cli \
  --dataset-csv rolling-dataset/rolling_event_dataset.csv \
  --out-dir rolling-quality
```

---

## 4. Outputs

```text
rolling-quality/rolling_dataset_quality.json
rolling-quality/rolling_dataset_quality.md
```

---

## 5. Report sections

The quality report includes:

```text
row_count
source_coverage
timeframe_coverage
session_distribution
lifecycle_distribution
delivery_distribution
terminal_distribution
dashboard_distribution
trader_mode_distribution
placeholder_summary
validation
```

---

## 6. Validation precondition

The rolling CSV must pass the existing event-log validator.

By default:

```text
ERROR dataset validation is rejected
WARN dataset validation is allowed and reported
```

Use `--reject-warn` when warnings should block the report.

---

## 7. Placeholder summary

The report explicitly summarizes placeholder rows:

```text
no_sweep_rows
delivery_none_rows
session_unknown_rows
snapshot_only_rows
```

This keeps draft OHLCV rows separated from later reviewed lifecycle rows.

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
tests/test_rolling_dataset_quality.py
```

Covered cases:

```text
source/timeframe/placeholder counts
invalid dataset rejection
JSON/Markdown report writing
CLI output writing
```

---

## 10. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.1-H — Rolling Dataset Lifecycle Candidate Proposal
```

That gate may propose rules for lifecycle candidate derivation, but must remain proposal-only until explicitly approved.
