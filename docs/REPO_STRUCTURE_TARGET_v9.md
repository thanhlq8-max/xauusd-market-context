# Target Repository Structure — v9

STATUS: STRUCTURE_TARGET_DRAFT
RUNTIME_CHANGE: NO

---

## 1. Current principle

Do not move existing package files in the cleanup branch. The current repository already has working Python package, docs, examples, tests, and GitHub Actions.

This document defines the target layout for future PRs.

---

## 2. Target tree

```text
xauusd-market-context/
  README.md
  PROJECT_STATE.md
  CHANGELOG.md
  LICENSE
  SECURITY.md
  CONTRIBUTING.md
  pyproject.toml
  requirements.txt

  xau_lfx/
    connectors/
    engines/
    reports/
    schemas/
    validation/              # future
    bridges/                 # future, monitor-only

  pine/                       # future optional; no source in cleanup branch
    README.md

  data/
    README.md
    raw/                      # ignored
    processed/                # ignored
    private/                  # ignored
    events/                   # templates allowed; generated logs ignored by default

  docs/
    V9_DESK_LIKE_HYBRID_STACK_ROADMAP.md
    REPO_STRUCTURE_TARGET_v9.md
    EVENT_DATASET_SCHEMA_V9.md
    REPO_CLEANUP_V9.md
    ...existing docs...

  research/
    README.md
    notebooks/                # future notebooks
    reports/                  # generated reports ignored unless explicitly curated

  bridges/
    README.md
    tradingview_webhook/      # future
    mt5_bridge/               # future
    telegram_alert/           # future

  examples/
    sample-data/
    sample-artifacts/

  tests/
    ...existing tests...
    validation/               # future
    engines/                  # future

  scripts/
    ...existing scripts...

  .github/
    workflows/
```

---

## 3. Path ownership

| Path | Owner role | Current rule |
|---|---|---|
| `xau_lfx/` | Python package runtime | Do not refactor in cleanup branch |
| `docs/` | documentation and governance | Safe to add v9 docs |
| `examples/` | committed synthetic fixtures | Preserve |
| `data/` | local research data boundary | Raw/private/generated data ignored |
| `pine/` | optional future Pine mirror | Placeholder only in cleanup branch |
| `research/` | future notebooks/reports | Placeholder only |
| `bridges/` | future alerts/integrations | Placeholder only; no execution |
| `.github/workflows/` | CI and Pages | Preserve unless CI issue is proven |

---

## 4. Migration rules

- No destructive moves until the PR lists exact old path, new path, and compatibility impact.
- No package rename until package publication decision is locked.
- No Pine source import until the source license/publication boundary is explicitly approved.
- No generated data under repository root.
- No secrets or broker credentials in examples.
- No notebook outputs unless specifically curated.

---

## 5. Cleanup sequencing

### Stage 1 — Non-destructive setup

- add v9 docs;
- add target directories with README files;
- expand `.gitignore` for generated research data;
- update README navigation.

### Stage 2 — Validation scaffolding

- add event schema code/tests;
- add validation-log templates;
- add sample event cases.

### Stage 3 — Engine extraction

- add compact lifecycle modules;
- compare against Pine screenshots/logs;
- keep existing artifact pipeline stable.

### Stage 4 — Research dashboard

- add dashboards only after logged dataset exists;
- keep reports descriptive and monitor-only.

---

## 6. Rejected cleanup actions for this branch

- deleting current docs;
- moving current Python modules;
- changing package name;
- changing CLI names;
- importing Pine source;
- adding execution bridge;
- adding profit/edge claims.
