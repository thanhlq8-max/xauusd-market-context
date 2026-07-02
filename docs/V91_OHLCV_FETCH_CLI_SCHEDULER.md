# v9.1-C — OHLCV Fetch CLI / Scheduler Boundary

STATUS: FETCH_ONCE_CLI_IMPLEMENTED
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate exposes a fetch-once CLI for normalized OHLCV snapshots while keeping scheduling outside the Python runtime.

The CLI writes:

```text
normalized_ohlcv.json
```

It does not run a daemon loop and does not connect to any execution workflow.

---

## 2. Command — OANDA primary

Use environment variable for the runtime token:

```bash
export OANDA_TOKEN="<runtime-token>"
python -m xau_lfx.connectors.candle_cli \
  --source oanda \
  --symbol XAUUSD \
  --timeframe M1 \
  --limit 300 \
  --out-dir normalized-ohlcv
```

Optional OANDA parameters:

```bash
python -m xau_lfx.connectors.candle_cli \
  --source oanda \
  --symbol XAUUSD \
  --timeframe M5 \
  --limit 300 \
  --oanda-api-url https://api-fxpractice.oanda.com/v3 \
  --oanda-price M \
  --out-dir normalized-ohlcv
```

---

## 3. Command — MT5 secondary

```bash
python -m xau_lfx.connectors.candle_cli \
  --source mt5 \
  --symbol XAUUSD \
  --timeframe M5 \
  --limit 300 \
  --out-dir normalized-ohlcv
```

MT5 requirements:

```text
MetaTrader5 Python package installed
MT5 terminal running
Account/session logged in
Symbol available and selectable
Terminal history loaded
```

The MT5 connector skips the current bar by default.

---

## 4. Offline fixture mode

For tests or dry runs:

```bash
python -m xau_lfx.connectors.candle_cli \
  --source oanda \
  --symbol XAUUSD \
  --timeframe M1 \
  --limit 1 \
  --fixture-json data/events/oanda_candles_fixture.json \
  --oanda-token test-token \
  --out-dir normalized-ohlcv
```

---

## 5. Scheduler boundary

This gate does not add a loop daemon. Use an external scheduler.

Recommended refresh policy:

```text
M1: run every 60 seconds; accept completed candles only.
M5: run every 60 seconds and process only new completed M5 bars, or run every 300 seconds for lower load.
```

Examples:

```text
cron
systemd timer
Docker scheduler
cloud scheduler
Windows Task Scheduler
```

---

## 6. Output contract

```text
normalized-ohlcv/normalized_ohlcv.json
```

The output is the connector payload containing:

```text
ts_utc
source_id
source_type
symbol
timeframe
status
payload.ohlcv
row_counts
errors
quality_flags
monitor_only
```

---

## 7. Boundary rule

This CLI is monitor-only.

It does not add:

```text
default pipeline wiring
notification bridge
broker execution
MT5 order action
position sizing
account-risk automation
Pine source import
strategy behavior
```

---

## 8. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.1-D — OHLCV Snapshot Validation / Source Freshness Gate
```

That gate should validate freshness, duplicate timestamps, and source status before any snapshot is accepted by downstream review tooling.
