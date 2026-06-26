# Sample Artifacts

This directory contains generated output from the synthetic fixture data in `examples/sample-data`.

The purpose is to let users inspect artifact shape before running the tool on their own local broker/MT5 exports.

## Rebuild

```bash
python -m xau_lfx.pipeline run-once \
  --input-dir examples/sample-data \
  --event-file examples/sample-data/usd_events.csv \
  --out-dir examples/sample-artifacts

python -m xau_lfx.pipeline report \
  --artifact-dir examples/sample-artifacts \
  --write-md
```

## Key files

```text
xau_artifact_quality.json
xau_context_summary.json
xau_market_context_report.md
```

## What to inspect first

1. `xau_artifact_quality.json` - quality score, grade, warnings, and confidence cap.
2. `xau_context_summary.json` - compact operator-facing context summary, including the Practical Zone Deck.
3. `xau_market_context_report.md` - human-readable report, including the Practical Zone Deck section.
4. `xau_data_quality.json` - source coverage, freshness, spread, and confidence details.

## Practical Zone Deck in the sample

The committed sample context summary includes `practical_zone_deck` so users can inspect the current deck shape without generating artifacts first.

The sample deck ranks supplied session high/low references by distance from `latest_close`. It is an inspection aid only and does not infer direction, timing for execution, account risk, or profitability.

## Data policy

These artifacts are generated from synthetic fixture data. They are not live market data and must not be used as trading guidance.

Do not commit broker, vendor, or third-party data unless redistribution rights are verified and documented.
