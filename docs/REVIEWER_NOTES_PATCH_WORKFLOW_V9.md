# Evidence Pack Index / Reviewer Notes Patch Workflow — v9.0-K

STATUS: REVIEW_PATCH_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate adds a controlled offline patch workflow for reviewer notes and review statuses.

It answers a narrow workflow question:

```text
How can a reviewer apply review_status and reviewer_notes updates to a case_index artifact without mutating live systems or adding trade logic?
```

The patch workflow is a review-data operation. It does not promote cases to trade signals.

---

## 2. Implemented modules

```text
xau_lfx/validation/review_patch.py
xau_lfx/validation/review_patch_cli.py
```

Implemented helpers:

- `apply_review_patch()`
- `write_updated_case_index()`

---

## 3. Command

```bash
python -m xau_lfx.validation.review_patch_cli \
  --case-index case-index/case_index.json \
  --patch-file data/events/reviewer_notes_patch_template.json \
  --out-dir updated-case-index
```

---

## 4. Outputs

```text
updated-case-index/updated_case_index.json
updated-case-index/updated_case_index.md
```

---

## 5. Patch file schema

```json
{
  "patches": [
    {
      "case_id": "CASE:replay-001",
      "review_status": "NEEDS_DATA",
      "reviewer_notes": "Request screenshot/session confirmation before acceptance."
    }
  ]
}
```

Allowed patch keys:

```text
case_id
review_status
reviewer_notes
```

Allowed `review_status` values:

```text
NEW
REVIEWED
ACCEPTED
REJECTED
NEEDS_DATA
```

Unsupported keys are rejected.

---

## 6. Boundary rule

This workflow is offline. It only reads:

```text
case_index.json
reviewer patch JSON
```

and writes:

```text
updated_case_index.json
updated_case_index.md
```

It does not connect to:

- live feeds;
- OANDA;
- TradingView;
- MT5;
- alerts;
- broker execution.

---

## 7. Tests

Implemented tests:

```text
tests/test_review_patch.py
tests/test_review_patch_cli.py
```

Covered cases:

- applying review status and notes;
- invalid status rejection;
- unknown case rejection;
- unsupported key rejection;
- JSON/Markdown updated index output;
- CLI success path;
- CLI invalid patch JSON error path.

---

## 8. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-L — Evidence Pack Review Cycle Lock / v9.0 Final Governance
```

That gate should lock the offline validation/review workflow and document what is required before any alert bridge proposal.
