# v9.0 Final Governance Lock

STATUS: FINAL_GOVERNANCE_LOCK_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This document locks the v9.0 offline validation and review workflow before any future notification-bridge proposal.

The current v9.0 stack is a research and validation workflow. It is not an execution system.

---

## 2. Completed gates

```text
Gate A — Repo foundation
Gate B — Event log validator
Gate C — Compact lifecycle primitives
Gate D — Logged event replay harness
Gate E — Liquidity node graph schema
Gate F — Node graph replay integration
Gate G — Case library seed
Gate H — Case library CLI / artifact boundary
Gate I — Case library index / review workflow
Gate J — Case review batch workflow / evidence pack
Gate K — Reviewer notes patch workflow
```

---

## 3. Locked workflow

The locked offline workflow is:

```text
1. Validate event log.
2. Replay event log through compact lifecycle primitives.
3. Build liquidity node graph report.
4. Build case-library seed.
5. Build case review index.
6. Build evidence pack.
7. Apply controlled reviewer-note/status patch if needed.
8. Review updated case index manually.
```

This workflow stays outside live operation.

---

## 4. Hard boundaries

The following remain locked:

```text
TRADING_MODE: MONITOR_ONLY
AUTO_ENTRY: NO
BUY_SELL_SIGNAL: NO
STRATEGY_MODE: NO
BROKER_EXECUTION: NO
ACCOUNT_RISK_AUTOMATION: NO
REAL_MM_INVENTORY_CLAIM: NO
REAL_RETAIL_POSITIONING_CLAIM: NO
STATISTICAL_EDGE_CLAIM: NO
```

No v9.0 component may turn review labels, node scores, case status, or evidence-pack groups into trade instructions.

---

## 5. Required evidence before notification bridge proposal

Any future notification bridge proposal must provide all of the following:

```text
- At least one validated event-log file.
- Replay report with no mismatch.
- Node graph report built from replay-validated rows.
- Case-library seed.
- Case review index.
- Evidence pack.
- Reviewer-note patch audit trail if manual review modified statuses.
- Explicit list of allowed notification names.
- Explicit statement that notifications are monitor-only.
```

Notification names must be state notifications only. They must not contain execution or account-risk instructions.

---

## 6. Final checklist

```text
[ ] Event log validates.
[ ] Replay passes.
[ ] Node graph report exists.
[ ] Case library exists.
[ ] Case review index exists.
[ ] Evidence pack exists.
[ ] Reviewer notes are applied through the patch workflow only.
[ ] No unsupported patch keys are accepted.
[ ] No trading/execution language is introduced.
[ ] No live bridge is introduced in v9.0 final lock.
```

---

## 7. Next allowed proposal

After this governance lock, the next proposal may be:

```text
v9.1-A — Monitor-only Notification Bridge Proposal
```

That proposal must remain in proposal form first. It must not self-implement notifications until explicitly approved in a separate scoped task.
