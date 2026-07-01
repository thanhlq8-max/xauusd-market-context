# Event Replay Harness — v9.0-D

STATUS: REPLAY_HARNESS_DRAFT
RUNTIME_PIPELINE_CHANGE: CLI_ONLY
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

The event replay harness compares logged event rows against the compact lifecycle engine.

It answers a narrow validation question:

```text
Did the compact Python engine reproduce the lifecycle and delivery states recorded in the forward-validation event row?
```

It does not measure profitability, does not connect to live feeds, and does not infer trade actions.

---

## 2. Command

```bash
xau-lfx replay-event-log \
  --event-log data/events/event_replay_template.csv \
  --out-dir replay-report
```

Outputs:

```text
replay-report/event_replay_report.json
replay-report/event_replay_report.md
```

If replay output has `MISMATCH`, the CLI exits with code `1` so CI can catch regressions.

---

## 3. Template

Committed synthetic replay template:

```text
data/events/event_replay_template.csv
```

The file extends the v9 event-log schema with replay input columns:

```text
open
high
low
close
atr
tick_activity
trigger_source
trigger_price
trigger_side
trigger_score
target_source
target_price
target_side
target_score
flow_skew
expected_lifecycle_state
expected_delivery_state
```

The event-log validator may warn that replay columns are extra columns. The replay harness accepts those columns as replay inputs.

---

## 4. Replay flow

```text
1. Validate event-log schema.
2. Read replay-specific input columns.
3. Build Candle.
4. Build trigger LiquidityLevel.
5. Build optional target LiquidityLevel.
6. Run build_lifecycle_snapshot().
7. Compare expected lifecycle_state / delivery_state with actual output.
8. Return OK / WARN / MISMATCH / ERROR.
9. Optionally write JSON + Markdown report.
```

---

## 5. Status meanings

| Status | Meaning |
|---|---|
| `OK` | All rows replayed and matched. |
| `WARN` | All rows matched but schema warnings exist. |
| `MISMATCH` | At least one row replayed but lifecycle or delivery output differs. |
| `ERROR` | Schema, parsing, or required replay input failure. |

---

## 6. Out of scope

- No live TradingView connection.
- No OANDA dashboard connection.
- No alert bridge.
- No broker execution.
- No position sizing.
- No account-risk automation.
- No claim of statistical edge.
- No claim of real MM inventory or real retail positioning.

---

## 7. Next gate

After this harness passes CI and merges, the next safe step is:

```text
v9.0-E — Liquidity Node Graph Schema
```

That step should define node objects and historical reaction scoring, but should not yet connect them to live operation.
