# v9.1-H — Lifecycle Candidate Governance Boundary

STATUS: GOVERNANCE_PROPOSAL
TRADING_MODE: MONITOR_ONLY
IMPLEMENTATION: NO

---

## 1. Boundary decision

Lifecycle candidate work must remain separate from validated event-log fields until a human review workflow accepts the candidate.

The rolling dataset remains the source record. Candidate artifacts are derived review artifacts.

---

## 2. Allowed future artifact

```text
lifecycle_candidates.json
lifecycle_candidates.md
```

---

## 3. Forbidden mutation

A future implementation must not mutate:

```text
rolling_event_dataset.csv
snapshot_event_log_draft.csv
case_index.json
reviewer notes patch files
```

---

## 4. Review requirement

A candidate may become an accepted lifecycle label only through a later explicit review/patch workflow.

---

## 5. Notification bridge rule

Candidate labels must not be sent to any notification bridge until there is a separate monitor-only notification approval task.
