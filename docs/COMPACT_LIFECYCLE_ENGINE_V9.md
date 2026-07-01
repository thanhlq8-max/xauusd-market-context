# Compact Lifecycle Engine — v9.0-C

STATUS: ENGINE_PRIMITIVE_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

The compact lifecycle engine ports the minimum LFX-2 behavior primitives into Python so future validation can compare logged Pine dashboard states with deterministic Python outputs.

This module is not connected to the artifact-generation pipeline in this branch.

---

## 2. Scope

Implemented module:

```text
xau_lfx/engines/compact_lifecycle.py
```

Covered primitives:

- candle metrics;
- level interaction guard;
- sweep side inference;
- lifecycle classification:
  - `NO_SWEEP`;
  - `RAW_SPIKE`;
  - `RECLAIM`;
  - `ACCEPT`;
- route candidate construction;
- target reference selection;
- delivery health:
  - `D_NONE`;
  - `D_ACTIVE`;
  - `D_STALL`;
  - `D_COUNTERFLOW`;
  - `D_TARGET_HIT`;
  - `D_FAILED`;
- monitor-only lifecycle snapshot.

---

## 3. Out of scope

- No TradingView Pine source import.
- No live dashboard connection.
- No OANDA dashboard behavior change.
- No artifact generation behavior change.
- No broker execution.
- No account-risk logic.
- No profitability or statistical-edge claim.
- No real MM inventory or real retail-positioning claim.

---

## 4. Input objects

### Candle

```text
open
high
low
close
atr
tick_activity
```

### LiquidityLevel

```text
source
price
side
freshness_bars
score
```

The engine uses `UP`, `DN`, and `NONE` as route/side vocabulary. It does not emit directional trade instructions.

---

## 5. Lifecycle logic

A level interaction must pass the bar-range/proximity guard before a sweep lifecycle can be classified.

Simplified lifecycle behavior:

| Condition | State | Route context |
|---|---|---|
| No valid interaction | `NO_SWEEP` | `NONE` |
| Interaction but close near level | `RAW_SPIKE` | `NONE` |
| Upper level swept then closed back below | `RECLAIM` | `DN` |
| Lower level swept then closed back above | `RECLAIM` | `UP` |
| Upper level swept then closed beyond | `ACCEPT` | `UP` |
| Lower level swept then closed beyond | `ACCEPT` | `DN` |

---

## 6. Route target logic

When lifecycle resolves as `RECLAIM` or `ACCEPT`, the engine selects the nearest available target reference in the route direction.

If no target exists, the route remains monitorable but lower-confidence and delivery health returns `D_NONE`.

---

## 7. Delivery health logic

Delivery state is evaluated from:

- locked route direction;
- target reference;
- current candle;
- route age;
- flow skew;
- current distance from target vs. initial distance.

Terminal precedence:

```text
D_TARGET_HIT
D_FAILED
D_COUNTERFLOW
D_STALL
D_ACTIVE
D_NONE
```

---

## 8. Tests

Implemented tests:

```text
tests/test_compact_lifecycle.py
```

Covered cases:

- no interaction;
- upper-level reclaim route;
- lower-level reclaim route;
- accept continuation;
- route without target;
- target hit;
- counterflow;
- stall;
- fail;
- active route;
- monitor-only snapshot.

---

## 9. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-D — Logged Event Replay Harness
```

That gate should compare event-log rows with compact lifecycle outputs before connecting this module to any dashboard or live adapter.
