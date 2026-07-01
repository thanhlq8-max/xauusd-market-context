# Case Library CLI / Artifact Boundary — v9.0-H

STATUS: CLI_BOUNDARY_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

This gate exposes case-library seed generation as an explicit offline command while keeping the main market-context artifact pipeline unchanged.

It answers a narrow operator question:

```text
How do I generate JSON/Markdown case-library seed artifacts from a replay event log without connecting live feeds, dashboards, alerts, or execution?
```

---

## 2. Command

```bash
python -m xau_lfx.validation.case_library_cli \
  --event-log data/events/event_replay_template.csv \
  --out-dir case-library-seed
```

Optional:

```bash
python -m xau_lfx.validation.case_library_cli \
  --event-log data/events/event_replay_template.csv \
  --out-dir case-library-seed \
  --cluster-band 1.0
```

---

## 3. Outputs

The command writes:

```text
case-library-seed/case_library_seed.json
case-library-seed/case_library_seed.md
```

The command also prints a JSON payload containing:

```text
status
node_graph_status
case_count
quality_counts
cases
report_paths
monitor_only
```

---

## 4. Exit codes

| Exit code | Meaning |
|---:|---|
| `0` | Case-library seed built successfully or with warnings. |
| `1` | Source replay/node graph validation failed. |

---

## 5. Boundary rule

This CLI deliberately lives under:

```text
xau_lfx.validation.case_library_cli
```

It is not wired into the primary `xau-lfx` pipeline command in this gate. This keeps v9 research artifacts isolated from the existing market-context artifact generator.

---

## 6. Out of scope

- No live dashboard connection.
- No OANDA dashboard connection.
- No alert bridge.
- No broker execution.
- No position sizing.
- No account-risk automation.
- No statistical-edge claim.
- No real MM inventory or real retail-positioning claim.
- No modification to existing market-context artifact generation.

---

## 7. Tests

Implemented tests:

```text
tests/test_case_library_cli.py
```

Covered cases:

- successful CLI execution;
- JSON and Markdown artifact existence;
- monitor-only marker;
- non-zero exit for invalid source.

---

## 8. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-I — Case Library Index / Review Workflow
```

That gate should add a lightweight index over generated case-library artifacts for manual review, still offline and monitor-only.
