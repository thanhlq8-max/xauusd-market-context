# Node Graph Replay Integration — v9.0-F

STATUS: REPLAY_INTEGRATION_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

The node graph replay integration connects logged replay rows to the liquidity node graph schema.

It answers a narrow validation question:

```text
What liquidity nodes and clusters are produced from replay-validated event rows?
```

This is the first step toward restoring node/cụm thanh khoản memory outside Pine. It remains offline, descriptive, and monitor-only.

---

## 2. Implemented module

```text
xau_lfx/validation/node_graph_replay.py
```

Implemented helpers:

- `build_node_graph_from_replay()`
- `write_node_graph_report()`

---

## 3. Flow

```text
1. Run event replay validation first.
2. Reject node graph build if replay status is ERROR or MISMATCH.
3. Read trigger/source/price fields from replay rows.
4. Create or update LiquidityNode objects.
5. Derive NodeReaction from lifecycle_state / delivery_state.
6. Build price-band clusters.
7. Return node/cluster report.
8. Optionally write JSON + Markdown reports.
```

---

## 4. Reaction mapping

| Logged state | Node reaction |
|---|---|
| `D_FAILED` or `*_FAIL` | `FAIL` |
| `RECLAIM` | `RECLAIM` |
| `ACCEPT` | `ACCEPT` |
| `REJECT` | `REJECT` |
| `RAW_SPIKE` | `SWEEP` |
| Other state | `TOUCH` |

This mapping is intentionally conservative and auditable. It does not infer hidden orderflow.

---

## 5. Report outputs

Report keys:

```text
status
replay_status
rows_checked
node_count
cluster_count
updates
nodes
clusters
monitor_only
```

Markdown output includes:

- node table;
- cluster table;
- errors;
- warnings.

---

## 6. Tests

Implemented tests:

```text
tests/test_node_graph_replay.py
```

Covered cases:

- successful node graph from committed replay template;
- rejection of plain event log without replay columns;
- rejection of replay mismatch;
- JSON/Markdown report writing.

---

## 7. Out of scope

- No live dashboard connection.
- No OANDA dashboard connection.
- No alert bridge.
- No broker execution.
- No position sizing.
- No account-risk automation.
- No statistical-edge claim.
- No real MM inventory or real retail-positioning claim.

---

## 8. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-G — Node Graph Quality Report / Case Library Seed
```

That gate should generate curated case summaries from replay/node reports while remaining descriptive and monitor-only.
