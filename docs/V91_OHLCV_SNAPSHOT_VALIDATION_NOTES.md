# OHLCV Snapshot Validation Notes

The snapshot validator is an acceptance gate for `normalized_ohlcv.json`.

It should be placed after fetch-once output and before any future event-log draft mapper.

Boundary decisions:

- `OK` source status is accepted.
- `WARN` source status is accepted with a warning.
- `ERROR` source status is rejected.
- Incomplete candles are rejected.
- Duplicate timestamps are rejected.
- Freshness is checked by timeframe defaults unless an operator override is supplied.
- Static fixtures may skip freshness for CI and dry-run only.

This gate remains offline and monitor-only.
