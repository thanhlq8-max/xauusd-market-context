# Context Summary Artifact

`xau_context_summary.json` is a compact monitor-only layer for humans reading generated XAUUSD artifacts.

It does not produce trade calls, execution instructions, position sizing, account-risk logic, or profitability claims.

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
  "spread_state": "STABLE",
  "event_risk_state": "CONTEXT",
  "confidence_explanation": [],
  "monitor_focus": []
}
```

## Interpretation rules

- `latest_close` comes from the local MTF bundle; it is not a centralized XAUUSD price.
- `nearest_session_level` is a reference from supplied CSV data only.
- `spread_state` is broker/feed-specific.
- `event_risk_state` is risk context only and never implies direction.
- `monitor_focus` describes what to observe next, not what to execute.

## Safety contract

The artifact remains aligned with the project monitor-only contract:

- no buy/sell logic;
- no order execution;
- no account-risk logic;
- no actual dealer inventory claim;
- no actual retail positioning claim;
- no statistical edge or profitability claim.
