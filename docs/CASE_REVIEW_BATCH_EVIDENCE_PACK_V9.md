# Case Review Batch Workflow / Evidence Pack — v9.0-J

STATUS: EVIDENCE_PACK_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate groups case-review index rows into an offline evidence pack for manual review.

It answers a narrow review question:

```text
Which accepted, needs-data, rejected, reviewed, or new cases should be reviewed together, and what checklist should guide that review?
```

The evidence pack is a review artifact. It does not promote cases to trade signals.

---

## 2. Implemented modules

```text
xau_lfx/validation/evidence_pack.py
xau_lfx/validation/evidence_pack_cli.py
```

Implemented helpers:

- `build_evidence_pack()`
- `write_evidence_pack()`

---

## 3. Command

```bash
python -m xau_lfx.validation.evidence_pack_cli \
  --case-index case-index/case_index.json \
  --out-dir evidence-pack
```

---

## 4. Outputs

```text
evidence-pack/evidence_pack.json
evidence-pack/evidence_pack.md
```

---

## 5. Grouping

Cases are grouped by review status:

```text
ACCEPTED
NEEDS_DATA
REJECTED
REVIEWED
NEW
```

Within each group, cases are sorted by:

```text
priority → timestamp → case_id
```

---

## 6. Review checklist

The generated checklist is descriptive. It asks the reviewer to:

- review `NEEDS_DATA` cases first;
- confirm accepted examples have matching lifecycle and delivery evidence;
- keep rejected cases as negative examples;
- leave new cases unchanged until manual review adds status or notes.

---

## 7. Boundary rule

This workflow is offline. It only reads a generated case-index JSON artifact and writes evidence-pack JSON/Markdown files.

It does not connect to:

- live feeds;
- OANDA;
- TradingView;
- MT5;
- alerts;
- broker execution.

---

## 8. Tests

Implemented tests:

```text
tests/test_evidence_pack.py
tests/test_evidence_pack_cli.py
```

Covered cases:

- evidence pack build from generated case index;
- grouping by review statuses;
- monitor-only payload guard;
- JSON/Markdown output writing;
- CLI success path;
- CLI invalid JSON error path.

---

## 9. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-K — Evidence Pack Index / Reviewer Notes Patch Workflow
```

That gate may add a controlled way to apply reviewer-note patches to case-index artifacts, still offline and monitor-only.
