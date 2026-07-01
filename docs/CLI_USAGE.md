# CLI Usage

The `xau-lfx` command validates local XAUUSD CSV files and generates monitor-only context artifacts. It does not require broker credentials for the synthetic demo.

## One-command demo

Run from a source checkout after `pip install -e .`:

```bash
xau-lfx demo
```

The command validates the committed synthetic fixtures, writes JSON and Markdown artifacts under `artifacts/`, and builds `site/index.html`. Its terminal summary prints the absolute path of every generated file.

Custom output directories are supported:

```bash
xau-lfx demo --out-dir demo-artifacts --site-dir demo-site
```

The demo reads only `examples/sample-data`. It does not read broker or vendor data.

## Platform demo examples

The examples below use project-relative placeholders such as `<repo>`. They avoid machine-specific personal directories so the commands can be copied into Windows, Linux, or macOS shells.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
xau-lfx demo
```

Expected output shape:

```text
monitor_state: CONTEXT
artifact.raw_scan: <repo>\artifacts\xau_raw_scan.json
artifact.context_summary: <repo>\artifacts\xau_context_summary.json
artifact.market_context_report: <repo>\artifacts\xau_market_context_report.md
site: <repo>\site\index.html
```

### Linux shell

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
xau-lfx demo
```

Expected output shape:

```text
monitor_state: CONTEXT
artifact.raw_scan: <repo>/artifacts/xau_raw_scan.json
artifact.context_summary: <repo>/artifacts/xau_context_summary.json
artifact.market_context_report: <repo>/artifacts/xau_market_context_report.md
site: <repo>/site/index.html
```

### macOS shell

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
xau-lfx demo
```

Expected output shape:

```text
monitor_state: CONTEXT
artifact.raw_scan: <repo>/artifacts/xau_raw_scan.json
artifact.context_summary: <repo>/artifacts/xau_context_summary.json
artifact.market_context_report: <repo>/artifacts/xau_market_context_report.md
site: <repo>/site/index.html
```

## Validate local sources

```bash
xau-lfx validate-sources \
  --input-dir examples/sample-data \
  --event-file examples/sample-data/usd_events.csv
```

Validation reports source coverage, errors, and quality flags without writing market-context artifacts.

## Generate JSON artifacts

```bash
xau-lfx run-once \
  --input-dir examples/sample-data \
  --event-file examples/sample-data/usd_events.csv \
  --out-dir artifacts
```

The command keeps its existing state output and then prints the absolute path of each generated JSON artifact.

Running `xau-lfx run-once` without local files preserves the existing low-confidence readiness behavior.

## Validate generated artifacts

```bash
xau-lfx validate-artifacts --artifact-dir artifacts
```

The command checks generated JSON artifacts against the package artifact contract:

- required artifact files must exist;
- required top-level keys must be present;
- every checked JSON artifact must keep `monitor_only: true`.

Validation failure exits with code `1`.

## Validate v9 event logs

```bash
xau-lfx validate-event-log --event-log data/events/event_log_template.csv
```

The command checks a forward-validation CSV against the v9 event dataset contract:

- required columns are present;
- timestamps include timezone information;
- state enums are compatible with the monitor-only workflow;
- sensitive columns such as token/account/position-size fields are rejected;
- impossible terminal-state combinations are rejected.

The validator does not score predictive usefulness and does not infer direction.

## Replay v9 event logs

```bash
xau-lfx replay-event-log \
  --event-log data/events/event_replay_template.csv \
  --out-dir replay-report
```

The command validates the event log first, then maps each replay row into compact lifecycle inputs and compares expected lifecycle/delivery states against engine output.

It writes optional JSON and Markdown replay reports when `--out-dir` is supplied. A replay `MISMATCH` exits with code `1` so CI can catch regressions.

The replay harness does not connect to live feeds, dashboards, brokers, or alert bridges.

## Generate the Markdown report

```bash
xau-lfx report --artifact-dir artifacts --write-md
```

## Generate the static site

```bash
xau-lfx site --artifact-dir artifacts --out-dir site
```

Open `site/index.html` locally. The generated outputs remain monitor-only research context and do not contain execution or account-risk logic.

## Run the OANDA Practice live dashboard

`serve-oanda` requires an explicit private host, port, request timeout, and a local `OANDA_API_TOKEN` environment variable. It has no public-feed fallback.

```powershell
.\.venv\Scripts\python.exe -m xau_lfx.web serve-oanda `
  --host 192.168.1.20 `
  --port 8766 `
  --request-timeout-seconds 10
```

The OANDA candle refresh interval is fixed at five seconds. See [`OANDA_LIVE_DASHBOARD.md`](OANDA_LIVE_DASHBOARD.md) for interactive token input, private-network access, and source limitations.

The validator also loads the committed JSON Schema files under `schemas/artifacts/`.
Those schema files must match the required artifact keys and must keep `monitor_only` fixed as a true value.
