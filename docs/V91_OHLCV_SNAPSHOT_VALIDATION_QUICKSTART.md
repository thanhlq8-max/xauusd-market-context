# OHLCV Snapshot Validation Quickstart

STATUS: QUICKSTART
TRADING_MODE: MONITOR_ONLY

---

## Fetch then validate

```bash
export OANDA_TOKEN="<runtime-token>"

python -m xau_lfx.connectors.candle_cli \
  --source oanda \
  --symbol XAUUSD \
  --timeframe M1 \
  --limit 300 \
  --out-dir normalized-ohlcv

python -m xau_lfx.connectors.candle_snapshot_cli \
  --snapshot normalized-ohlcv/normalized_ohlcv.json \
  --out-dir ohlcv-validation \
  --max-age-seconds 180
```

Expected outputs:

```text
ohlcv-validation/ohlcv_snapshot_validation.json
ohlcv-validation/ohlcv_snapshot_validation.md
```

---

## Static fixture mode

Use this only for tests or dry runs:

```bash
python -m xau_lfx.connectors.candle_snapshot_cli \
  --snapshot normalized-ohlcv/normalized_ohlcv.json \
  --out-dir ohlcv-validation \
  --skip-freshness-check
```

Do not use `--skip-freshness-check` for live operator workflow.
