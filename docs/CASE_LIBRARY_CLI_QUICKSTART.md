# Case Library CLI Quickstart

STATUS: QUICKSTART
MODE: OFFLINE
TRADING_MODE: MONITOR_ONLY

Run from the repository root after editable install:

```bash
python -m xau_lfx.validation.case_library_cli \
  --event-log data/events/event_replay_template.csv \
  --out-dir case-library-seed
```

Expected outputs:

```text
case-library-seed/case_library_seed.json
case-library-seed/case_library_seed.md
```

This command reads a replay event log, builds the offline node graph report internally, then writes case-library seed artifacts.

It does not connect to live feeds, OANDA, TradingView, MT5, alerts, or broker execution. It does not produce BUY/SELL, position sizing, SL/TP, profit, real MM inventory, or real retail positioning claims.
