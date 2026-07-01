# Case Library Index / Review Workflow — v9.0-I

STATUS: REVIEW_INDEX_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate builds an offline review index over generated case-library seed artifacts.

It answers a narrow review question:

```text
Which cases are new, reviewed, accepted, rejected, or still need more evidence?
```

The index is a review workflow aid. It does not promote cases to trade signals.

---

## 2. Implemented modules

```text
xau_lfx/validation/case_index.py
xau_lfx/validation/case_index_cli.py
```

Implemented helpers:

- `build_case_index()`
- `write_case_index()`

---

## 3. Command

```bash
python -m xau_lfx.validation.case_index_cli \
  --case-library case-library-seed/case_library_seed.json \
  --out-dir case-index
```

---

## 4. Outputs

```text
case-index/case_index.json
case-index/case_index.md
```

---

## 5. Review statuses

```text
NEW
REVIEWED
ACCEPTED
REJECTED
NEEDS_DATA
```

Automatic mapping:

- `manual_review_result = MATCH` and quality `STRONG`/`VALID` → `ACCEPTED`
- `manual_review_result = WRONG` or quality `REJECT` → `REJECTED`
- `manual_review_result = PARTIAL`/`UNCLEAR` or quality `REVIEW` → `NEEDS_DATA`
- explicit `review_status` overrides if valid
- otherwise `NEW`

---

## 6. Review priority

```text
HIGH
MEDIUM
LOW
```

Priority is descriptive and only supports manual review ordering.

---

## 7. Boundary rule

This workflow is offline. It only reads a generated case-library JSON artifact and writes an index JSON/Markdown pair.

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
tests/test_case_index.py
tests/test_case_index_cli.py
```

Covered cases:

- index build from generated case library;
- explicit review status override;
- monitor-only payload guard;
- JSON/Markdown output writing;
- CLI success path;
- CLI invalid JSON error path.

---

## 9. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-J — Case Review Batch Workflow / Evidence Pack
```

That gate may group cases by review status and build an evidence pack for manual review, still offline and monitor-only.
