# OHLCV Snapshot Validation Boundary

This gate validates snapshot quality only.

Allowed:

- Read `normalized_ohlcv.json`.
- Validate source status.
- Validate completed candles.
- Validate timestamp uniqueness.
- Validate freshness.
- Write JSON and Markdown validation reports.

Forbidden:

- Runtime order workflow.
- Broker execution.
- Account-risk automation.
- Long-running daemon loop.
- Notification bridge implementation.
- Default artifact pipeline mutation.
