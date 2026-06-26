# Context Summary Artifact

`xau_context_summary.json` is a compact monitor-only layer for humans reading generated XAUUSD artifacts.

It does not produce directional trade calls, execution instructions, position sizing, account-risk logic, or profitability claims.

## Output fields

```json
{
  "latest_close": 2345.67,
  "freshness_age_minutes": 12.0,
  "nearest_session_level": {
    "session": "LONDON",
    "level": "high",
    "price": 2349.2,
    "distance_points": 3.53
  },
  "practical_zone_deck": [
    {
      "rank": 1,
      "role": "LONDON_HIGH_REFERENCE",
      "session": "LONDON",
      "level": "high",
      "price": 2349.2,
      "side_from_latest": "above",
      "distance_points": 3.53,
      "range_points": 8.4,
      "bar_count": 24,
      "why_it_matters": "Ranked session reference from supplied M15 context.",
      "operator_read": "Observe accept or reject behavior around LONDON high reference."
    }
  ],
  "spread_state": "STABLE",
  "event_risk_state": "CONTEXT",
  "confidence_explanation": [],
  "monitor_focus": []
}
```

## Interpretation rules

- `latest_close` comes from the local MTF bundle; it is not a centralized XAUUSD price.
- `nearest_session_level` is a reference from supplied CSV data only.
- `practical_zone_deck` ranks supplied session high/low references by distance from `latest_close`.
- `practical_zone_deck[*].side_from_latest` is a relative position label: `above`, `below`, or `at`.
- `practical_zone_deck[*].distance_points` is a distance measurement, not a directional forecast.
- `spread_state` is broker/feed-specific.
- `event_risk_state` is risk context only and never implies direction.
- `monitor_focus` describes what to observe next, not what to execute.

## Practical zone deck limits

The practical zone deck is an inspection aid. It must remain subordinate to artifact quality, freshness, spread state, and event-risk context.

It does not infer:

- directional bias;
- continuation or reversal;
- timing for execution;
- account-risk sizing;
- statistical edge;
- centralized spot-gold orderflow;
- actual dealer inventory;
- actual retail-side positioning.

Full guide: [`docs/PRACTICAL_ZONE_DECK.md`](PRACTICAL_ZONE_DECK.md).

## Safety contract

The artifact remains aligned with the project monitor-only contract:

- no directional trade-call logic;
- no order execution;
- no account-risk logic;
- no actual dealer inventory claim;
- no actual retail-side positioning claim;
- no statistical edge or profitability claim.
