# GitHub Pages Demo

The project can generate a static demo site from local artifacts.

## Build demo locally

```bash
python -m xau_lfx.pipeline run-once \
  --input-dir examples/sample-data \
  --event-file examples/sample-data/usd_events.csv \
  --out-dir artifacts

python -m xau_lfx.pipeline report --artifact-dir artifacts --write-md
python -m xau_lfx.pipeline site --artifact-dir artifacts --out-dir site
```

Open:

```text
site/index.html
```

## What the site shows

- artifact quality score and grade;
- source coverage;
- confidence cap;
- high-impact USD event count;
- monitor-only current read;
- Practical Zone Deck references ranked by distance from the latest composite close;
- operator focus list;
- exported JSON and Markdown artifacts.

## What the site does not show

- directional trade-call instructions;
- account-risk instructions;
- broker execution;
- actual dealer inventory claims;
- actual retail-side positioning claims;
- profitability claims.

## GitHub workflow

The workflow `.github/workflows/pages.yml` builds the sample artifacts and publishes the generated `site/` directory.

Before enabling GitHub Pages, confirm:

1. `LICENSE`, `NOTICE`, and `DATA_LICENSE.md` are committed.
2. The repo owner/repository URL placeholders in `pyproject.toml` have been replaced.
3. GitHub Pages is enabled for GitHub Actions deployment.
