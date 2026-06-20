# Real-World Usage Cases

These cases show practical validation and context outcomes without committing broker data or implying predictive performance. All examples are synthetic.

## Case 1: malformed CSV is rejected

**Input condition:** an M15 row has a high below its close, or the file repeats a timestamp.

**Expected result:** source validation fails with the file name, row number, and violated rule. The system does not repair the row or continue with an invented value.

**Practical value:** the operator can correct the exporter before the bad row reaches a dashboard or research notebook.

```powershell
python -m xau_lfx.pipeline validate-sources --input-dir path\to\export --event-file path\to\usd_events.csv
```

## Case 2: spread instability lowers quality

**Input condition:** the supplied spread series varies materially across the local sample.

**Expected result:** `spread_stability` falls, the quality artifact records a warning, and the context summary reports the spread state as a constraint.

**Practical value:** a visually clean price chart cannot hide weak transaction-cost context.

Inspect:

```text
artifacts/xau_data_quality.json
artifacts/xau_artifact_quality.json
artifacts/xau_context_summary.json
```

## Case 3: event proximity caps confidence

**Input condition:** a synthetic high-impact USD event falls inside the configured local risk window.

**Expected result:** the event artifact records the nearby event and confidence remains capped. No price outcome is inferred from the event title.

**Practical value:** the report keeps source confidence separate from a directional narrative during a known event window.

Inspect:

```text
artifacts/xau_event_risk_state.json
artifacts/xau_context_summary.json
```

## Case 4: nearest session level is explicit

**Input condition:** validated M15 bars produce Asia, London, or New York session ranges.

**Expected result:** the context summary identifies the nearest supplied session high or low and its absolute distance from the latest close.

**Practical value:** the user gets a reproducible reference level with source timestamp and session label instead of an opaque chart annotation.

Inspect:

```text
artifacts/xau_session_context.json
artifacts/xau_context_summary.json
```

## Live OANDA Practice case

The private live dashboard adds five-second OANDA Practice refresh without changing the CSV cases above. It displays:

- OANDA M5/M15/H1 candles;
- newest candle timestamp and completion state;
- latest candle-close spread proxy;
- UTC session ranges and nearest level;
- factual DID/NOW context and conditional NEXT reference;
- explicit `NOT_INFERRED` states where OHLC evidence is insufficient.

See [`OANDA_LIVE_DASHBOARD.md`](OANDA_LIVE_DASHBOARD.md).
