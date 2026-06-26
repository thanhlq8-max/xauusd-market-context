# Demo Walkthrough

This walkthrough shows the shortest path from a fresh clone to inspectable XAUUSD market-context artifacts.

The demo uses only synthetic fixture data under `examples/sample-data`. It does not require broker credentials, MT5, vendor data, TradingView, or a live account.

## 1. Install locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e .
```

## Recommended artifact reading order

When inspecting generated outputs or reviewing the static demo, use this order so source quality is checked before interpretation:

1. **Artifact quality** — inspect source coverage, freshness, structural errors, warnings, and confidence caps first.
2. **Context summary** — read the compact monitor-only summary, practical zone deck, spread state, event-risk state, and monitor-focus bullets.
3. **Markdown report** — review the human-readable report for expanded context and artifact links.
4. **Source policy** — cross-check source limits, synthetic fixture policy, and redistribution boundaries.

This order is for inspection only. It does not turn artifacts into execution instructions, position sizing, or profitability evidence.

## One-command path

```bash
xau-lfx demo
```

This validates the synthetic source set, generates the JSON and Markdown artifacts, builds `site/index.html`, and prints the absolute path of each output. The remaining sections show the equivalent commands separately for inspection and troubleshooting.

## 2. Validate sample sources

```bash
python -m xau_lfx.pipeline validate-sources \
  --input-dir examples/sample-data \
  --event-file examples/sample-data/usd_events.csv
```

Expected result: the command should report a valid local source set. If validation fails, the failure should identify the CSV file and row-level issue.

## 3. Generate sample artifacts

```bash
python -m xau_lfx.pipeline run-once \
  --input-dir examples/sample-data \
  --event-file examples/sample-data/usd_events.csv \
  --out-dir artifacts
```

Important outputs:

```text
artifacts/xau_artifact_quality.json
artifacts/xau_context_summary.json
artifacts/xau_market_context_report.md
```

## 4. Inspect the context summary

Open:

```text
artifacts/xau_context_summary.json
```

This file is the compact operator-facing summary. It can include latest close, source freshness age, nearest session level context, a practical zone deck, spread state, event-risk state, confidence explanation, and monitor-focus bullets.

The practical zone deck ranks supplied session high/low references by distance from the latest composite close. It is designed for inspecting accept, reject, or rotation behavior around known references. It does not infer direction, execution, account risk, or profitability.

It is monitor-only. It must not be interpreted as directional trade-call guidance, execution instruction, position sizing, or profitability evidence.

## 5. Build the Markdown report

```bash
python -m xau_lfx.pipeline report --artifact-dir artifacts --write-md
```

Open:

```text
artifacts/xau_market_context_report.md
```

The report is the most readable artifact for human review.

## 6. Build the static demo site

```bash
python -m xau_lfx.pipeline site --artifact-dir artifacts --out-dir site
```

Open:

```text
site/index.html
```

The static site is backend-free and suitable for GitHub Pages. It summarizes artifact quality, context summary, practical zone deck, source coverage, warnings, errors, and exported artifact links.

### Static demo screenshot

![Static demo screenshot](assets/static-demo-screenshot.svg)

The screenshot above was captured from the generated local file:

```text
site/index.html
```

To refresh it, rebuild the demo from the committed synthetic fixtures, open the generated page, capture the visible static report, and replace `docs/assets/static-demo-screenshot.svg` only after visually checking that the image still shows the current static demo:

```powershell
Set-Location E:\xauusd-market-context
python -m xau_lfx.pipeline run-once --input-dir examples/sample-data --event-file examples/sample-data/usd_events.csv --out-dir artifacts
python -m xau_lfx.pipeline report --artifact-dir artifacts --write-md
python -m xau_lfx.pipeline site --artifact-dir artifacts --out-dir site
Start-Process .\site\index.html
```

Do not replace this screenshot with broker, vendor, or third-party market data unless redistribution rights are verified and documented.

## 7. Rebuild committed sample artifacts

Maintainers can refresh the committed sample artifacts with:

```bash
python -m xau_lfx.pipeline run-once \
  --input-dir examples/sample-data \
  --event-file examples/sample-data/usd_events.csv \
  --out-dir examples/sample-artifacts

python -m xau_lfx.pipeline report \
  --artifact-dir examples/sample-artifacts \
  --write-md
```

Do not replace synthetic fixture artifacts with broker, vendor, or third-party market data unless redistribution rights are verified and documented.

## Safety contract

This project is a monitor-only market-context artifact generator.

It does not provide:

- trade execution;
- directional trade-call calls;
- account-risk logic;
- position sizing;
- profitability claims;
- centralized spot-gold orderbook claims;
- real dealer inventory or retail positioning claims.
