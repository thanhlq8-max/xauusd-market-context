# v9.1-A — OHLCV Data Source Decision

STATUS: DATA_SOURCE_DECISION_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Decision

Recommended primary source for fully automatic M1/M5 XAUUSD OHLCV refresh:

```text
Primary: broker REST API source, with OANDA REST candles as first implementation candidate.
Secondary: MT5 Python bridge when broker-feed parity is more important than cloud-native operation.
Fallback: external market-data vendor for reference/backup only.
```

---

## 2. Why broker REST API first

A broker REST API is the cleanest unattended server-side input because it can run without a desktop terminal.

For OANDA-style candle polling, the adapter can request completed candles by instrument, price component, granularity, count/from/to, and use the completed-candle flag before accepting a bar into the validation pipeline.

Recommended refresh policy:

```text
M1 source: poll every 60 seconds, accept only completed M1 bars.
M5 source: poll every 60 seconds but process only when a new completed M5 bar appears, or poll every 300 seconds for lower load.
```

---

## 3. When MT5 is better

Use MT5 Python bridge when the objective is to match the exact broker feed seen on the trader's MT5 chart.

MT5 is suitable for:

```text
ICMarkets / broker-feed parity
local/VPS terminal workflows
spread and tick-volume fields from the terminal
chart-to-tool comparison
```

MT5 is less suitable for:

```text
headless cloud deployment
no-terminal operation
multi-source normalization
high-availability unattended services
```

Reason: MT5 Python data depends on a running terminal, logged account/session, selected symbol, and available chart history.

---

## 4. Vendor API fallback

A vendor API can be used for independent reference or backup, but it should not be treated as the same feed as the execution broker.

For XAUUSD/forex-style data, vendor aggregates may be built from quoted bid/ask prices rather than executed trades. This is acceptable for monitoring reference, but must be labeled by source.

---

## 5. Volume rule

For XAUUSD spot/CFD/forex-style feeds, `volume` must be treated as:

```text
tick count / quote activity / source-specific activity proxy
```

It must not be described as centralized traded volume.

---

## 6. Adapter contract proposal

Every OHLCV adapter must output:

```text
source_id
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
monitor_only
```

Forbidden adapter fields:

```text
account_balance
risk_percent
position_size
order_request
broker_order_id
trade_signal
```

---

## 7. Implementation gate

The v9.1-A scope is decision/proposal only.

Implementation requires a future scoped task:

```text
v9.1-B — OHLCV Adapter Implementation
```

The user must select the primary source before implementation:

```text
A. OANDA REST primary
B. MT5 Python bridge primary
C. vendor API primary
```
