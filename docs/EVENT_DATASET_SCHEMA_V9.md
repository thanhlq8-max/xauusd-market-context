# Event Dataset Schema — v9 Draft

STATUS: SCHEMA_DRAFT_WITH_VALIDATOR
RUNTIME_CHANGE: CLI_VALIDATOR_ONLY
PURPOSE: forward-validation dataset for LFX-2 behavior monitoring

---

## 1. Purpose

The v9 event dataset records observable market-context states so the system can be validated without claiming private MM inventory, real retail positioning, or statistical edge prematurely.

The first dataset should answer:

- Did the dashboard state match chart behavior?
- Did a sweep become reclaim, accept, reject, or fail?
- Did an accepted route progress, stall, counterflow, hit target, or fail?
- Which source/session produced the most useful monitor states?

---

## 2. Record grain

One row = one observed event or state transition.

Recommended formats:

```text
CSV for manual logging.
JSONL for programmatic logging.
```

Do not mix manual notes with generated metrics in the same untyped field. Use explicit columns.

---

## 3. Core fields

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `event_id` | string | yes | Unique stable ID |
| `ts_utc` | datetime | yes | UTC timestamp |
| `symbol` | string | yes | Start with `XAUUSD` / `XAU_USD` |
| `broker_source` | string | yes | Example: OANDA, MT5 broker, TradingView source |
| `timeframe` | string | yes | M5, M15, H1, H4, D1 |
| `session` | string | yes | Asia, London, NY, Off |
| `shock_slot` | string | no | Asia/China, US macro, NY open, Normal clock |
| `manual_news_block` | bool | no | Operator flag |
| `spread_state` | string | no | Stable, elevated, unstable, unknown |
| `dashboard_state` | string | yes | High-level dashboard state |
| `trader_mode` | string | yes | TRACK/WAIT/RESET/STRUCTURAL etc. |

---

## 4. Sweep fields

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `sweep_source` | string | no | AsiaH, AsiaL, PDH, PDL, NYH, NYL, WKH, WKL, ROUND, DENSITY |
| `sweep_level` | float | no | Reference price |
| `sweep_side` | string | no | UP, DN, none |
| `sweep_score` | float | no | 0..1 if generated |
| `lifecycle_state` | string | yes | NO_SWEEP, RAW_SPIKE, RECLAIM, ACCEPT, REJECT, RECLAIM_FAIL, ACCEPT_FAIL |
| `absorb_score` | float | no | 0..1 if generated |
| `zone_role` | string | no | SweepRef, Barrier, ReleaseRef, Density, TargetRef, FailedTarget, HitTarget |
| `zone_price` | float | no | Current practical zone reference |

---

## 5. Route/delivery fields

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `route_dir` | string | no | UP, DN, none |
| `route_origin` | float | no | Locked origin/reference if available |
| `target_ref` | float | no | Locked target reference |
| `delivery_state` | string | yes | D_NONE, D_ACTIVE, D_STALL, D_COUNTERFLOW, D_TARGET_HIT, D_FAILED |
| `route_age_bars` | int | no | Bars since route lock |
| `target_dist_at_lock_atr` | float | no | Initial target distance |
| `current_target_dist_atr` | float | no | Current distance |
| `terminal_state` | string | no | HIT, FAILED, RESET, OPEN |

---

## 6. Outcome metrics

Outcome metrics can be filled only after future bars complete.

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `mfe_5` | float | no | Max favorable excursion after 5 bars |
| `mae_5` | float | no | Max adverse excursion after 5 bars |
| `mfe_10` | float | no | Max favorable excursion after 10 bars |
| `mae_10` | float | no | Max adverse excursion after 10 bars |
| `mfe_20` | float | no | Max favorable excursion after 20 bars |
| `mae_20` | float | no | Max adverse excursion after 20 bars |
| `time_to_resolution_bars` | int | no | Bars until HIT/FAILED/RESET |
| `target_hit` | bool | no | True only if target reached |
| `route_failed` | bool | no | True only if failed condition reached |
| `manual_review_result` | string | no | MATCH, PARTIAL, WRONG, UNCLEAR |
| `review_notes` | string | no | Human notes, no hidden instructions |

---

## 7. Minimal CSV header

```csv
event_id,ts_utc,symbol,broker_source,timeframe,session,shock_slot,manual_news_block,spread_state,dashboard_state,trader_mode,sweep_source,sweep_level,sweep_side,sweep_score,lifecycle_state,absorb_score,zone_role,zone_price,route_dir,route_origin,target_ref,delivery_state,route_age_bars,target_dist_at_lock_atr,current_target_dist_atr,terminal_state,mfe_5,mae_5,mfe_10,mae_10,mfe_20,mae_20,time_to_resolution_bars,target_hit,route_failed,manual_review_result,review_notes
```

Committed template:

```text
data/events/event_log_template.csv
```

---

## 8. Validation command

```bash
xau-lfx validate-event-log --event-log data/events/event_log_template.csv
```

The validator checks:

- required columns;
- duplicate `event_id` values;
- timezone-aware `ts_utc` values;
- enum compatibility for timeframe/session/lifecycle/delivery/review states;
- numeric, integer, and boolean fields;
- sensitive columns such as token/account/position-size fields;
- terminal-state conflicts such as `D_TARGET_HIT` with `route_failed=true`.

It does not score predictive usefulness and does not infer trade direction.

---

## 9. Validation rules

- Required fields must not be empty.
- Timestamps must be UTC-compatible.
- `monitor_only` semantics must be preserved in all generated reports.
- `delivery_state = D_TARGET_HIT` cannot also have `route_failed = true`.
- `delivery_state = D_FAILED` cannot also have `target_hit = true` unless manually marked as data error.
- `manual_review_result` must be one of `MATCH`, `PARTIAL`, `WRONG`, `UNCLEAR`, or empty.
- No row should contain account balance, position size, API token, or personal financial data.

---

## 10. First dataset target

Initial validation target:

```text
5–10 London/NY sessions
M5 + M15 + H1 screenshots/logs
20–50 manually reviewed event rows minimum
```

Only after this dataset exists should the project discuss accuracy, reliability, or route-quality statistics.
