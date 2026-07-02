# v9.1-A — Monitor-only Notification Bridge Proposal

STATUS: PROPOSAL_ONLY
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY
IMPLEMENTATION: NO

---

## 1. Purpose

This document proposes a future monitor-only notification bridge after the v9.0 offline validation/review workflow has been locked.

It does not implement notifications. It defines the minimum scope and approval boundary for a later implementation task.

---

## 2. Required preconditions

A notification bridge may only be implemented after the operator can produce:

```text
validated event log
replay report with no mismatch
node graph report
case-library seed
case review index
evidence pack
reviewer-note patch audit trail if statuses were changed
```

---

## 3. Proposed allowed notification states

Future notifications may use state names only:

```text
TRACK_RECLAIM
TRACK_ACCEPT
D_ACTIVE
D_STALL
D_FAILED
TARGET_HIT
NEEDS_REVIEW
```

These are monitoring states. They are not entries, exits, orders, or strategy signals.

---

## 4. Payload boundary

A future payload may include:

```text
ts_utc
symbol
timeframe
state
source
node_id
cluster_id
case_id
review_status
priority
evidence_pack_ref
monitor_only
```

A future payload must not include:

```text
BUY
SELL
entry_price
stop_loss
take_profit
lot_size
position_size
leverage
account_balance
risk_percent
order_id
broker_order_request
```

---

## 5. Proposed delivery channels

Allowed future channels may include:

```text
local JSONL append
local webhook receiver
Telegram message
Slack message
email digest
```

Every channel must preserve monitor-only wording.

---

## 6. Out of scope for v9.1-A

```text
No code implementation.
No live feed connection.
No broker API action.
No MT5 order action.
No Pine source import.
No TradingView automation.
No account-risk logic.
No execution bridge.
```

---

## 7. Approval gate

Implementation requires a separate scoped task:

```text
v9.1-B — Monitor-only Notification Bridge Implementation
```

That task must select one channel, one data source, and one payload contract. It must not implement execution behavior.
