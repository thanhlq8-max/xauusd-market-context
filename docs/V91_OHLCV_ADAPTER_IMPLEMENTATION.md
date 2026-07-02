# v9.1-B — OHLCV Adapter Implementation

STATUS: IMPLEMENTATION_SCAFFOLD
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate implements the first monitor-only OHLCV adapter layer after the v9.1-A source decision.

Implemented primary path:

```text
A — OANDA REST primary
```

Implemented secondary path:

```text
B — MT5 Python bridge
```

The adapters are isolated connectors. They are not wired into the default artifact pipeline in this gate.

---

## 2. Implemented modules

```text
xau_lfx/connectors/ohlcv_adapter.py
xau_lfx/connectors/oanda_rest.py
xau_lfx/connectors/mt5_bridge.py
```

---

## 3. Normalized candle contract

Every adapter row must output:

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
volume_type
monitor_only
```

---

## 4. OANDA REST connector

Implemented connector:

```text
OandaRestConnector
```

Scope:

- maps `XAUUSD` to `XAU_USD`;
- supports `M1`, `M5`, `M15`, `H1`;
- builds OANDA candle request URL;
- accepts an injected transport for actual HTTP access;
- parses completed candles only;
- skips incomplete candles;
- returns monitor-only normalized OHLCV payload.

The connector does not store credentials. The operator must provide the token and transport at runtime.

---

## 5. MT5 bridge connector

Implemented connector:

```text
MT5BridgeConnector
```

Scope:

- uses optional `MetaTrader5` Python module when available;
- supports `M1`, `M5`, `M15`, `H1`;
- selects the symbol in the terminal;
- calls `copy_rates_from_pos`;
- skips the current bar by default to avoid incomplete-candle usage;
- normalizes terminal bars into monitor-only OHLCV rows.

The connector depends on a running/logged MT5 terminal when used live.

---

## 6. Refresh policy

Recommended operator schedule:

```text
M1: run fetch every 60 seconds; accept completed bars only.
M5: run fetch every 60 seconds and process only new completed M5 bars, or run every 300 seconds for lower load.
```

This gate does not add a scheduler. Scheduling should be handled by cron, systemd timer, Docker scheduler, GitHub Actions schedule, or a future scoped service.

---

## 7. Volume rule

For XAUUSD spot/CFD/forex-style feeds:

```text
tick_volume = quote activity / broker-specific activity proxy
```

It must not be described as centralized traded volume.

---

## 8. Tests

Implemented tests:

```text
tests/test_ohlcv_adapter.py
tests/test_oanda_rest_connector.py
tests/test_mt5_bridge_connector.py
```

Covered cases:

- normalized candle contract;
- bad OHLC rejection;
- connector payload status behavior;
- OANDA completed-candle parsing;
- OANDA incomplete-candle skipping;
- OANDA missing-token / missing-transport guard;
- MT5 fake terminal fetch;
- MT5 missing module guard;
- MT5 symbol-select failure guard.

---

## 9. Out of scope

- No default pipeline wiring.
- No long-running scheduler.
- No notification bridge implementation.
- No broker execution.
- No account-risk automation.
- No Pine source import.
- No strategy behavior.

---

## 10. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.1-C — OHLCV Fetch CLI / Scheduler Boundary
```

That gate may expose a fetch-once command and document scheduler usage, still monitor-only and without execution behavior.
