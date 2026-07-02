# v9.1-I — Lifecycle Candidate Artifact Implementation

STATUS: CANDIDATE_ARTIFACT_IMPLEMENTED
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate writes separate lifecycle candidate artifacts from a validated rolling event dataset and its quality report.

It answers a narrow review-preparation question:

```text
Which rolling dataset rows should be queued for manual lifecycle review without mutating the source dataset?
```

---

## 2. Implemented modules

```text
xau_lfx/connectors/lifecycle_candidates.py
xau_lfx/connectors/lifecycle_candidates_cli.py
```

Implemented helpers:

```text
build_lifecycle_candidates()
write_lifecycle_candidates()
```

---

## 3. Command

```bash
python -m xau_lfx.connectors.lifecycle_candidates_cli \
  --dataset-csv rolling-dataset/rolling_event_dataset.csv \
  --quality-json rolling-quality/rolling_dataset_quality.json \
  --out-dir lifecycle-candidates
```

---

## 4. Outputs

```text
lifecycle-candidates/lifecycle_candidates.json
lifecycle-candidates/lifecycle_candidates.md
```

---

## 5. Preconditions

The builder requires:

```text
validate_event_log(rolling_event_dataset.csv).status == OK
rolling_dataset_quality.status == OK
```

If either precondition fails, the builder returns `ERROR` and writes no accepted candidate rows.

---

## 6. Current candidate state

The current implementation emits only:

```text
NEEDS_MANUAL_REVIEW
```

Reason:

```text
rolling draft rows currently preserve OHLCV-derived event-log shape, but do not yet contain confirmed liquidity references or reviewed lifecycle evidence.
```

This prevents premature lifecycle conclusions.

---

## 7. Candidate row contract

Each candidate contains:

```text
candidate_id
event_id
ts_utc
symbol
broker_source
timeframe
candidate_state
candidate_reference
candidate_evidence
required_review
source_lifecycle_state
source_delivery_state
monitor_only
```

---

## 8. Boundary rule

This gate is monitor-only. It does not add:

```text
mutation of rolling_event_dataset.csv
lifecycle field overwrite
route conclusion
delivery conclusion
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
tests/test_lifecycle_candidates.py
```

Covered cases:

```text
candidate artifact creation
bad dataset rejection
non-OK quality report rejection
JSON/Markdown report writing
CLI output writing
```

---

## 10. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.1-J — Lifecycle Candidate Review Patch Workflow
```

That gate may define a controlled review patch for candidate acceptance/rejection, still without mutating the rolling dataset directly.
