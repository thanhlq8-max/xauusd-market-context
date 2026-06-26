# Practical Zone Deck

The Practical Zone Deck is a monitor-only section in `xau_context_summary.json`, the Markdown market-context report, and the static demo site.

It converts supplied session high/low references into a compact inspection deck so a human reviewer can quickly see which known references are closest to the latest composite close.

## Purpose

The deck is designed to improve readability of existing context artifacts. It helps reviewers inspect:

- which supplied session references are nearest to the latest composite close;
- whether each reference is above or below the latest composite close;
- which session and level produced the reference;
- what the operator should observe around that reference.

It is not a predictive model, trading system, order instruction, account-risk module, or profitability claim.

## Source inputs

The deck is derived from data already present in the context summary build path:

- `composite.median_latest_close`
- `session.session_ranges[*].high`
- `session.session_ranges[*].low`

The deck does not fetch broker-only positioning, dealer inventory, centralized spot-gold orderbook data, or third-party market data.

## Ranking rule

Each candidate reference is ranked by absolute distance from `median_latest_close`.

For every supplied session high/low reference:

1. compute `abs(reference_price - median_latest_close)`;
2. keep numeric references only;
3. sort by smallest distance first;
4. assign a one-based `rank`.

The ranking is distance-only. It does not infer directional bias, continuation, reversal, execution timing, account risk, or statistical edge.

## Field contract

Each deck item may include:

| Field | Meaning |
| --- | --- |
| `rank` | One-based distance rank. |
| `role` | Stable text role based on session and level, such as `ASIA_HIGH_REFERENCE`. |
| `session` | Session name from the supplied session range object. |
| `level` | Source level, usually `high` or `low`. |
| `price` | Reference price from the supplied session context. |
| `side_from_latest` | `above`, `below`, or `at` relative to the latest composite close. |
| `distance_points` | Absolute distance from latest composite close. |
| `range_points` | Optional supplied session range size when available. |
| `bar_count` | Optional supplied session bar count when available. |
| `why_it_matters` | Monitor-only explanation of why this reference is visible. |
| `operator_read` | Monitor-only observation prompt for reviewing behavior around the reference. |

Downstream tools should treat unknown fields as non-critical metadata unless a future artifact contract explicitly states otherwise.

## How to read it

Recommended inspection order:

1. Confirm artifact quality status and confidence cap first.
2. Check `latest_close` and `nearest_session_level`.
3. Read `practical_zone_deck[0]` as the nearest supplied session reference.
4. Compare nearby deck items with the Markdown report and static site.
5. Use lower-timeframe views only as confirmation context, not as an execution command.

The static site and Markdown report intentionally use observation language. They should not be rewritten into order language.

## Safety boundaries

The Practical Zone Deck must remain inside the project monitor-only contract.

Allowed wording:

- observe accept or reject behavior;
- inspect rotation behavior;
- compare M5, M15, and H1 context;
- keep spread and event risk visible;
- rank supplied references by distance.

Forbidden behavior:

- direct trade-call output;
- order execution;
- account-risk sizing;
- profit projection;
- claims about actual dealer inventory;
- claims about actual retail-side positioning;
- claims about centralized spot XAUUSD orderbook data.

## Maintainer checklist

When changing this feature:

1. Preserve `monitor_only: true` in generated artifacts.
2. Keep ranking deterministic.
3. Do not add predictive wording.
4. Do not introduce execution or account-risk logic.
5. Update `tests/fixtures/context_summary_snapshot.json` when operator-facing summary output intentionally changes.
6. Run the full local validation set before pushing a release tag.

```bash
py -m compileall xau_lfx tests
py -m pytest -q
py -m build
python -m xau_lfx.pipeline demo --out-dir artifacts --site-dir site
python -m xau_lfx.pipeline validate-artifacts --artifact-dir artifacts
```
