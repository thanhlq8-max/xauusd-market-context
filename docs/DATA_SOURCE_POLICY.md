# Data Source Policy

This project accepts local, user-controlled data first.

## Supported source paths

- MT5 or broker OHLCV CSV files for `XAUUSD_M5`, `XAUUSD_M15`, and `XAUUSD_H1`.
- Broker spread CSV file.
- Manual USD event CSV file.
- Optional OANDA v20 Practice `XAU_USD` candles on a local private host.

## Source limits

- Broker OHLCV is broker-specific.
- `tick_volume` is broker tick activity, not centralized traded volume.
- Broker spread is not institutional consensus.
- Event data is risk context only.
- No centralized XAUUSD spot orderbook is claimed.
- OANDA `price_count` is provider price activity, not centralized traded volume.
- Live OANDA snapshots are not committed or redistributed by this repository.
- A local OANDA Practice token is required only for the optional live dashboard.

## Deferred source families

- Live MT5 bridge.
- Paid futures or macro vendors.
- Licensed open interest datasets.
- Telegram or desktop alerting.
- Pine bridge.
