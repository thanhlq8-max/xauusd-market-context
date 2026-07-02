# v9 Notification Bridge Preconditions

STATUS: PRECONDITION_DRAFT
MODE: PROPOSAL_ONLY
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This document defines what must exist before any v9.1 notification bridge proposal can be considered.

The bridge is not implemented in v9.0-L.

---

## 2. Required proof set

A future notification bridge proposal must reference:

```text
- validated event log;
- replay report;
- node graph report;
- case-library seed;
- case review index;
- evidence pack;
- optional updated case index if reviewer-note patches were applied.
```

---

## 3. Allowed notification categories

Allowed future categories may include monitor states such as:

```text
TRACK_RECLAIM
TRACK_ACCEPT
D_ACTIVE
D_STALL
D_FAILED
TARGET_HIT
NEEDS_REVIEW
```

These are review or monitoring states only.

---

## 4. Forbidden promotion

The bridge proposal must not convert review cases, node scores, cluster scores, or quality labels into execution instructions.

---

## 5. Approval rule

A future notification bridge requires a separate scoped task after this final governance lock.
