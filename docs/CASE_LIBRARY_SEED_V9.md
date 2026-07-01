# Case Library Seed — v9.0-G

STATUS: CASE_LIBRARY_SEED_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

The case library seed converts replay/node graph outputs into compact evidence cases.

It answers a narrow review question:

```text
Which replay-validated events should be reviewed as behavior cases, and what node/cluster evidence supports each case?
```

This remains offline, descriptive, and monitor-only.

---

## 2. Implemented module

```text
xau_lfx/validation/case_library.py
```

Implemented helpers:

- `build_case_library_from_replay()`
- `write_case_library()`

---

## 3. Flow

```text
1. Run node graph replay build first.
2. Reject case-library build if node graph build fails.
3. Read replay rows.
4. Join each event row with node update output.
5. Join node with cluster if available.
6. Create one case per event row.
7. Assign descriptive quality label.
8. Optionally write JSON + Markdown seed files.
```

---

## 4. Case fields

```text
case_id
event_id
ts_utc
symbol
timeframe
session
source
side
lifecycle_state
delivery_state
terminal_state
node_id
node_reaction
node_score_after
cluster_id
cluster_score
manual_review_result
quality_label
review_notes
monitor_only
```

---

## 5. Quality labels

| Label | Meaning |
|---|---|
| `STRONG` | Node or cluster score is high enough to prioritize review. |
| `VALID` | Node or cluster score is usable for review. |
| `WEAK` | Evidence exists but score is low. |
| `REVIEW` | Manual review is partial or unclear. |
| `REJECT` | Manual review marks the case wrong. |

These labels are descriptive review labels, not trade ratings.

---

## 6. Report outputs

Output files:

```text
case_library_seed.json
case_library_seed.md
```

Markdown output includes:

- status;
- node graph status;
- case count;
- monitor-only flag;
- case table.

---

## 7. Tests

Implemented tests:

```text
tests/test_case_library.py
```

Covered cases:

- successful case seed from committed replay template;
- rejection of plain event log;
- rejection of replay mismatch source;
- JSON/Markdown report writing.

---

## 8. Out of scope

- No live dashboard connection.
- No OANDA dashboard connection.
- No alert bridge.
- No broker execution.
- No position sizing.
- No account-risk automation.
- No statistical-edge claim.
- No real MM inventory or real retail-positioning claim.

---

## 9. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-H — Case Library CLI / Artifact Boundary
```

That gate may expose case-library generation as a CLI command or curated artifact writer, but it should remain offline and monitor-only.
