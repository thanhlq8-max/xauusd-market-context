# Issue Backlog Seed

STATUS: PUBLIC_ADOPTION_DOC  
MODE: CONTROL  
TRADING_MODE: MONITOR_ONLY

These issue seeds are intended to make contribution paths explicit.

Do not create issues that imply trading signals, profitability, execution, or account-risk logic.

## Good first issues

### Add a README screenshot for the static demo

Labels:

```text
good first issue, documentation
```

Body:

```markdown
Add a screenshot of the generated `site/index.html` static demo to the README or docs.

Scope:
- use sample artifacts only;
- do not include broker/vendor data;
- do not change runtime behavior.
```

### Improve MT5 CSV export examples

Labels:

```text
good first issue, documentation
```

Body:

```markdown
Improve `docs/MT5_EXPORT_GUIDE.md` with clearer examples for exporting XAUUSD M5/M15/H1 CSV files.

Scope:
- schema examples only;
- no live account connection;
- no execution or signal language.
```

### Add malformed CSV fixtures

Labels:

```text
good first issue, validation
```

Body:

```markdown
Add small malformed CSV fixtures for duplicate timestamp, non-increasing timestamp, invalid OHLC, and invalid spread.

Scope:
- test fixtures only;
- no production data;
- preserve existing validation semantics.
```

## Enhancement issues

### Add context-summary fixture snapshots

Labels:

```text
enhancement, test
```

Body:

```markdown
Add stable JSON snapshot tests for `xau_context_summary.json`.

Scope:
- sample data only;
- preserve monitor-only wording;
- do not add directional trade language.
```

### Improve static demo artifact table

Labels:

```text
enhancement, frontend
```

Body:

```markdown
Improve the static site artifact list with file descriptions and recommended reading order.

Scope:
- static HTML only;
- no JavaScript framework;
- no backend service.
```

### Add source-quality explanation examples

Labels:

```text
enhancement, documentation
```

Body:

```markdown
Document examples of why confidence may be capped: stale data, missing timeframe, unstable spread, high-impact USD event.

Scope:
- docs/report wording only;
- no scoring formula changes unless separately scoped.
```

## Research issues

### Define non-directional session-distance metrics

Labels:

```text
research, monitor-only
```

Body:

```markdown
Propose non-directional session-distance metrics for context summary.

Must avoid:
- buy/sell language;
- entry logic;
- stop-loss/take-profit logic;
- profitability claims.
```

### Evaluate multi-broker source family design

Labels:

```text
research, architecture
```

Body:

```markdown
Explore a future source-family model for comparing multiple broker CSV exports.

Scope:
- design note only;
- no live broker connection;
- no claim of centralized XAUUSD spot truth.
```
