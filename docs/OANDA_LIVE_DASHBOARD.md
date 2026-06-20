# OANDA Practice Live Dashboard

This optional local service reads `XAU_USD` candles from OANDA v20 Practice and renders a mobile-first monitor on the same private host. It does not change the CSV pipeline or the static GitHub Pages demo.

## Locked runtime contract

| Setting | Locked value |
|---|---|
| OANDA environment | Practice |
| REST host | `https://api-fxpractice.oanda.com` |
| Instrument | `XAU_USD` |
| Candle price components | midpoint, bid, ask |
| Timeframes | M5, M15, H1 |
| Requested candles | 300 per timeframe |
| Refresh interval | 5 seconds |
| Credential location | local process environment only |
| Browser access | same host or private LAN |

The connector requests OANDA-generated candles. It does not resample, fill missing candles, or replace a failed response with fabricated values. A failed refresh leaves the last successful snapshot visible with `STALE` status.

## Credential setup on Windows

Create a Practice token through OANDA's API access workflow. Do not paste it into source files, issue forms, screenshots, command arguments, or browser storage.

Use an interactive PowerShell prompt so the token is not written literally into command history:

```powershell
$secure = Read-Host "OANDA Practice token" -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:OANDA_API_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
}
```

The environment variable exists only in that PowerShell process and child processes. Remove it when the dashboard stops:

```powershell
Remove-Item Env:OANDA_API_TOKEN
```

## Start on a private LAN address

Find the PC's private IPv4 address with `ipconfig`, then pass that address explicitly. The example timeout and port are operator-selected launch values; the CLI does not silently choose them for `serve-oanda`.

```powershell
.\.venv\Scripts\python.exe -m xau_lfx.web serve-oanda `
  --host 192.168.1.20 `
  --port 8766 `
  --request-timeout-seconds 10
```

Open the following address on a phone connected to the same private network:

```text
http://192.168.1.20:8766/
```

Use a Windows Firewall private-network rule only. Do not expose this service through public port forwarding. The server rejects an explicit public bind address; a local wildcard address still depends on host firewall policy, so a concrete private address is preferred.

## Endpoints

| Route | Purpose |
|---|---|
| `/` | responsive dashboard |
| `/api/xau/live` | current source snapshot and bounded context |
| `/api/xau/live/health` | refresh state without candle data |

The browser receives no authorization header, environment variable, or token field. The page uses same-origin requests and does not load third-party scripts.

## Dashboard reading order

1. Check `OK`, `STALE`, or `UNAVAILABLE` source status.
2. Check the newest M5 timestamp and whether the candle is complete.
3. Inspect M5/M15/H1 price shape in the candle chart.
4. Read DID, DOING, and NEXT as observed facts and a conditional reference only.
5. Inspect UTC session highs/lows under KEY Zones.
6. Keep MM Mission and INV/Release at `NOT_INFERRED` unless a separately specified evidence engine exists.

`price_count` is the number of OANDA prices inside a candle. It is not centralized traded volume. The latest close spread is a candle-close proxy, not a streaming spread measurement.

## Chart contract

- Question: what price shape is visible in the most recent returned OANDA candles?
- Form: interactive candlestick chart with M5/M15/H1 selector.
- Data: the last 60 of 300 returned candles for the selected timeframe.
- Encoding: blue and gold bodies, outline body for an incomplete candle, price on a common linear scale.
- Mobile behavior: single-column layout below 920 px; compact two-column summary below 560 px.
- Source note: OANDA v20 Practice, `XAU_USD`, midpoint candles; bid/ask retained for the close-spread proxy.

## Status semantics

- `STARTING`: no refresh has completed yet.
- `UNAVAILABLE`: no refresh has succeeded and the latest attempt failed.
- `OK`: the latest refresh succeeded.
- `STALE`: a prior snapshot exists but the latest refresh failed.

An `OK` transport state does not mean the market is active. The newest candle timestamp and completion flag remain visible so weekends or market pauses are not hidden.

## Source limits

- OANDA Practice is the closest supported source to an OANDA-branded chart feed, but it may differ from a TradingView chart.
- Candle timing, account availability, environment, and provider-side aggregation can produce differences.
- The OANDA-only mode has one broker source family and no event calendar context.
- OHLC candles alone do not establish an MM mission, dealer inventory, or retail positioning.
- Do not commit or redistribute downloaded candle snapshots unless the applicable data terms permit it.

References:

- [OANDA v20 REST API](https://developer.oanda.com/rest-live-v20/introduction/)
- [OANDA v20 OpenAPI instrument specification](https://github.com/oanda/v20-openapi/blob/master/yaml/separate/v20_instrument.yaml)
- [OANDA legal and regulatory documents](https://www.oanda.com/us-en/legal/)

## Local verification

Automated tests use a fake transport and contain no live credential or downloaded market snapshot:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_oanda_v20_connector.py tests/test_oanda_live.py tests/test_live_dashboard.py -q
```

A real-account smoke test requires the operator's local Practice token and is intentionally not part of public CI.
