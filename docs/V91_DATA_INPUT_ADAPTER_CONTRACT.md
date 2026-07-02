# v9.1-A — Data Input Adapter Contract

STATUS: CONTRACT_PROPOSAL
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This document defines the proposed contract for future OHLCV data adapters.

It is a proposal only. It does not implement any adapter.

---

## 2. Required normalized candle fields

```text
source_id
source_type
symbol
timeframe
ts_utc
open
high
low
close
tick_volume
spread
is_complete
source_latency_ms
received_at_utc
monitor_only
```

---

## 3. Source type enum proposal

```text
BROKER_REST
MT5_TERMINAL
VENDOR_REST
LOCAL_FILE
```

---

## 4. Completion rule

Only completed candles may enter replay, node graph, case library, or evidence pack workflows.

Incomplete candles may be logged for diagnostics, but must not update review artifacts.

---

## 5. Timeframe rule

The first implementation should support only:

```text
M1
M5
M15
H1
```

No additional timeframe should be added without a separate scoped task.

---

## 6. Source labeling rule

Every generated event row must retain its source label.

The system must not merge OANDA, MT5, and vendor data without preserving source identity.

---

## 7. Forbidden fields

```text
BUY
SELL
entry
exit
stop_loss
take_profit
lot_size
position_size
leverage
account_balance
risk_percent
order_id
```

---

## 8. Future implementation gate

Implementation requires source selection first:

```text
A. OANDA REST primary
B. MT5 Python bridge primary
C. vendor REST primary
```
