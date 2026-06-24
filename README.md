# XAUUSD Market Context v2.8.0

[![tests](https://github.com/thanhlq8-max/xauusd-market-context/actions/workflows/tests.yml/badge.svg)](https://github.com/thanhlq8-max/xauusd-market-context/actions/workflows/tests.yml)
[![pages-demo](https://github.com/thanhlq8-max/xauusd-market-context/actions/workflows/pages.yml/badge.svg)](https://github.com/thanhlq8-max/xauusd-market-context/actions/workflows/pages.yml)
[![Release](https://img.shields.io/github/v/release/thanhlq8-max/xauusd-market-context)](https://github.com/thanhlq8-max/xauusd-market-context/releases)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

STATUS: OANDA_PRACTICE_LIVE_DASHBOARD
MODE: CONTROL  
TRADING_MODE: MONITOR_ONLY  
AUTO_EXECUTION: NO  
DIRECTIONAL_TRADE_CALLS: NO

Generate auditable XAUUSD market-context artifacts from local MT5/broker CSV exports, spread snapshots, manual USD event files, or an optional private OANDA v20 Practice dashboard. v2.5.0 adds an artifact contract validator so shared JSON bundles can be checked before downstream inspection. v2.5.1 adds deterministic context-summary snapshot coverage so operator-facing wording changes are intentional. v2.5.2 removes committed patch helper artifacts and blocks generated patch/apply files from release readiness. v2.6.0 adds committed JSON Schema files and validates generated artifacts against them. v2.6.1 adds a packaged built-in schema fallback so wheel installs can validate artifacts without relying on repository-root schema files. v2.7.0 deepens nested schema coverage for existing object and array structures while preserving artifact generation behavior. v2.8.0 adds a package publication readiness gate for package-name and TestPyPI/PyPI decisions without publishing or changing runtime behavior. The package is a monitor-only sidecar for XAU research workflows; it uses the LFX-2 material as a semantic and safety baseline without modifying or reproducing the Pine source.

## Why this exists

Most retail XAUUSD workflows depend on one broker feed and opaque indicator output. This repo takes a stricter route:

- ingest local CSV files that the user controls;
- validate schema, freshness, spread stability, and MTF coverage;
- preserve broker tick activity as `tick_volume`, not centralized volume;
- generate JSON and Markdown artifacts that can be audited or used by another dashboard;
- cap confidence when source quality, spread, or event risk is weak.

## Use cases

- Validate local XAUUSD CSV exports before using them in research dashboards.
- Generate auditable market-context artifacts from broker-controlled source files.
- Inspect MTF coverage, source freshness, spread state, event-risk state, and context summary.
- Produce static HTML/Markdown outputs that can be shared without a backend service.
- Run a private-host OANDA Practice candle dashboard on a PC and view it from a phone on the same LAN.
- Maintain a monitor-only workflow that avoids trading-signal, execution, and profitability claims.

## Who this is for

- XAUUSD researchers who want reproducible local artifacts.
- Systematic traders who need source-quality gates before downstream analysis.
- Tool builders who need a small, static, auditable market-context sidecar.
- Contributors looking for focused OSS issues around validation, docs, and report quality.

## Hard rules

- Does not modify or reproduce the LFX-2 v7.1-F/v7.2-A-R5 Pine source.
- Does not create order execution, position sizing, or account-risk logic.
- Does not claim centralized XAUUSD spot orderbook.
- Does not treat CFD tick activity as centralized traded volume.
- Does not claim actual dealer inventory or actual retail-side positioning.
- Does not claim statistical edge or profitability.

## Install

For local development:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e .
```

CLI commands after editable install:

```bash
xau-lfx --help
xau-lfx-api --help
```

Package publication preflight is documented in [`docs/PACKAGE_PUBLICATION_READINESS.md`](docs/PACKAGE_PUBLICATION_READINESS.md). It requires an explicit package-name decision before TestPyPI or PyPI upload.

## Quickstart with sample data

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e .
xau-lfx demo
```

The command validates the committed synthetic fixtures, generates JSON and Markdown artifacts, prints their absolute paths, and builds `site/index.html`. Open that file for the static demo used by GitHub Pages.


Demo walkthrough:

```text
docs/DEMO_WALKTHROUGH.md
```

The walkthrough explains how to rebuild sample artifacts, inspect `xau_context_summary.json`, open the generated Markdown report, and generate the static demo site without broker credentials.

Complete CLI reference: [`docs/CLI_USAGE.md`](docs/CLI_USAGE.md).

Validate generated artifact compatibility:

```bash
xau-lfx validate-artifacts --artifact-dir artifacts
```

This checks required top-level keys, `monitor_only: true`, JSON readability, and the committed JSON Schema files under `schemas/artifacts/`. It does not validate predictive usefulness and does not infer direction.

Artifact contract reference: [`docs/ARTIFACT_CONTRACT.md`](docs/ARTIFACT_CONTRACT.md). JSON Schema reference: [`docs/ARTIFACT_JSON_SCHEMAS.md`](docs/ARTIFACT_JSON_SCHEMAS.md).

## OANDA Practice live dashboard

The optional live path is separate from the CSV pipeline and public GitHub Pages demo. It requests OANDA-generated `XAU_USD` M5/M15/H1 midpoint, bid, and ask candles every five seconds. Failed refreshes are visible as `STALE`; missing fields are not filled.

Set `OANDA_API_TOKEN` only in the local process, then bind the service to an explicit private address:

```powershell
.\.venv\Scripts\python.exe -m xau_lfx.web serve-oanda `
  --host 192.168.1.20 `
  --port 8766 `
  --request-timeout-seconds 10
```

Open `http://192.168.1.20:8766/` from a device on the same private network. The browser never receives the token. Full credential setup, firewall boundaries, status semantics, and source limits: [`docs/OANDA_LIVE_DASHBOARD.md`](docs/OANDA_LIVE_DASHBOARD.md).

OANDA Practice may differ from a TradingView OANDA chart candle-for-candle. This mode uses one broker source family, no event feed, and does not infer an MM mission or dealer inventory from OHLC alone.

No-argument compatibility mode still works:

```bash
python -m xau_lfx.pipeline run-once
```

That mode intentionally returns a low-confidence readiness state until local sources are provided.

## Local CSV schemas

### OHLCV files

Expected files:

```text
XAUUSD_M5.csv
XAUUSD_M15.csv
XAUUSD_H1.csv
```

Required columns:

```text
ts_utc,open,high,low,close,tick_volume
```

Rules:

- `ts_utc` must include a timezone and parse as UTC-compatible ISO-8601.
- OHLC values must be numeric.
- `tick_volume` is preserved as broker tick activity.
- Missing columns fail validation; missing OHLC values are not filled.

### Spread file

Expected file:

```text
XAUUSD_spread.csv
```

Required columns:

```text
ts_utc,bid,ask,spread_points
```

Spread is broker-specific. Instability reduces artifact quality.

### Event file

Required columns:

```text
ts_utc,currency,impact,title
```

Allowed impact values:

```text
LOW,MEDIUM,HIGH
```

Only high-impact USD events may cap confidence for XAUUSD, and only as risk context. The system does not infer direction from events.

## GitHub adoption resources

- Demo walkthrough: [`docs/DEMO_WALKTHROUGH.md`](docs/DEMO_WALKTHROUGH.md)
- Adoption guide: [`docs/ADOPTION_GUIDE.md`](docs/ADOPTION_GUIDE.md)
- Backlog seed: [`docs/ISSUE_BACKLOG_SEED.md`](docs/ISSUE_BACKLOG_SEED.md)
- Release readiness: [`docs/GITHUB_RELEASE_READINESS.md`](docs/GITHUB_RELEASE_READINESS.md)
- Package publication readiness: [`docs/PACKAGE_PUBLICATION_READINESS.md`](docs/PACKAGE_PUBLICATION_READINESS.md)
