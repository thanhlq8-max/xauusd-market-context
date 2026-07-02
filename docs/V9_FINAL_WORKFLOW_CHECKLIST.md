# v9.0 Final Workflow Checklist

STATUS: FINAL_CHECKLIST_DRAFT
MODE: OFFLINE_REVIEW
TRADING_MODE: MONITOR_ONLY

---

## Required artifacts

The v9.0 review cycle is complete only when the following artifacts exist:

```text
replay-report/event_replay_report.json
replay-report/event_replay_report.md
case-library-seed/case_library_seed.json
case-library-seed/case_library_seed.md
case-index/case_index.json
case-index/case_index.md
evidence-pack/evidence_pack.json
evidence-pack/evidence_pack.md
updated-case-index/updated_case_index.json
updated-case-index/updated_case_index.md
```

---

## Required commands

```bash
python -m xau_lfx.pipeline validate-event-log --event-log data/events/event_log_template.csv
python -m xau_lfx.pipeline replay-event-log --event-log data/events/event_replay_template.csv --out-dir replay-report
python -m xau_lfx.validation.case_library_cli --event-log data/events/event_replay_template.csv --out-dir case-library-seed
python -m xau_lfx.validation.case_index_cli --case-library case-library-seed/case_library_seed.json --out-dir case-index
python -m xau_lfx.validation.evidence_pack_cli --case-index case-index/case_index.json --out-dir evidence-pack
python -m xau_lfx.validation.review_patch_cli --case-index case-index/case_index.json --patch-file data/events/reviewer_notes_patch_template.json --out-dir updated-case-index
```

---

## Required review rules

```text
1. Use the case index as the review source.
2. Use the evidence pack as the batch review view.
3. Use patch files for reviewer notes and status changes.
4. Keep all review outputs monitor-only.
5. Do not connect final governance artifacts to live operation.
```
