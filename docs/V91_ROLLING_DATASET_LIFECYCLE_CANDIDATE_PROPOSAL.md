# v9.1-H — Rolling Dataset Lifecycle Candidate Proposal

STATUS: PROPOSAL_ONLY
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY
IMPLEMENTATION: NO

---

## 1. Purpose

This document proposes a future lifecycle-candidate derivation layer for the rolling event dataset.

It does not implement lifecycle derivation. It defines candidate rules, evidence requirements, and approval boundaries for a later scoped implementation.

---

## 2. Required inputs

A future implementation may only consume already validated artifacts:

```text
rolling-dataset/rolling_event_dataset.csv
rolling-quality/rolling_dataset_quality.json
```

Required preconditions:

```text
rolling dataset validates with event-log validator
rolling dataset quality report status is OK or explicitly operator-accepted WARN
source/timeframe coverage is documented
candidate rows retain source identity
```

---

## 3. Candidate-only principle

A lifecycle candidate is not a conclusion.

Candidate states may be proposed as review hints only:

```text
CANDIDATE_RAW_SPIKE
CANDIDATE_RECLAIM
CANDIDATE_ACCEPT
CANDIDATE_REJECT
CANDIDATE_FAIL
NEEDS_MANUAL_REVIEW
```

These labels must not overwrite validated event-log lifecycle fields without a later review/patch workflow.

---

## 4. Proposed evidence inputs per candle sequence

A future candidate derivation may inspect only local rolling dataset values and derived candle context:

```text
ts_utc
symbol
broker_source
timeframe
open
high
low
close
tick_volume
spread
session
source freshness metadata
prior local high/low from same source/timeframe
```

If OHLC fields are not present in the event-log row, a future implementation must either join against a normalized OHLCV snapshot archive or stop with `INSUFFICIENT_CONTEXT`.

---

## 5. Proposed candidate rule families

### 5.1 Raw spike candidate

Possible candidate only when:

```text
price range expands beyond recent local range
close does not confirm stable acceptance beyond the reference
volume/tick activity proxy is elevated relative to local rows
```

This remains a candidate because the current rolling draft rows do not yet contain confirmed liquidity references.

### 5.2 Reclaim candidate

Possible candidate only when:

```text
one row extends through a local reference
later row closes back inside the prior range
source and timeframe match
```

### 5.3 Accept candidate

Possible candidate only when:

```text
row closes beyond a local reference
follow-through rows remain beyond that reference
no immediate reclaim is observed in the local window
```

### 5.4 Reject candidate

Possible candidate only when:

```text
price tests a local reference
close fails to sustain beyond that reference
subsequent local rows move away from the reference
```

### 5.5 Fail candidate

Possible candidate only when:

```text
previous candidate state is invalidated by opposite movement
candidate reference is revisited and not defended
```

---

## 6. Required output contract for future implementation

A future implementation may write a separate candidate artifact only:

```text
lifecycle_candidates.json
lifecycle_candidates.md
```

Candidate rows should include:

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
monitor_only
```

---

## 7. Forbidden behavior

A future implementation must not:

```text
overwrite rolling_event_dataset.csv lifecycle fields automatically
emit direct entry labels
emit BUY or SELL commands
create route or delivery conclusions
create notification bridge messages
call broker or terminal execution APIs
claim statistical edge
claim real MM inventory
claim real retail positioning
```

---

## 8. Approval gate

Implementation requires a separate scoped task:

```text
v9.1-I — Lifecycle Candidate Artifact Implementation
```

That implementation must remain monitor-only and must write candidate artifacts separately from the rolling dataset.
