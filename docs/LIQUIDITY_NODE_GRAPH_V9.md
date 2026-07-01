# Liquidity Node Graph Schema — v9.0-E

STATUS: SCHEMA_PRIMITIVE_DRAFT
RUNTIME_PIPELINE_CHANGE: NO
TRADING_MODE: MONITOR_ONLY

---

## 1. Purpose

The liquidity node graph schema starts restoring the deeper node/cụm thanh khoản layer outside Pine, where state memory and validation can be handled without TradingView compiler constraints.

This branch only defines primitive objects, scoring, reactions, clustering, and tests. It does not connect the node graph to live operation.

---

## 2. Implemented module

```text
xau_lfx/engines/liquidity_nodes.py
```

Implemented objects:

- `LiquidityNode`
- `NodeReaction`
- `NodeCluster`

Implemented primitives:

- `make_node_id()`
- `create_liquidity_node()`
- `age_node()`
- `update_node_reaction()`
- `score_node()`
- `serialize_node()`
- `cluster_nodes()`
- `serialize_cluster()`

---

## 3. Node fields

```text
node_id
source
price
side
created_ts_utc
last_seen_ts_utc
freshness_bars
touch_count
sweep_count
reclaim_count
accept_count
reject_count
fail_count
score
active
```

The score is a monitor-quality score. It is not a trade edge or profitability score.

---

## 4. Reaction types

```text
TOUCH
SWEEP
RECLAIM
ACCEPT
REJECT
FAIL
```

Reaction update behavior:

- increments the matching counter;
- resets `freshness_bars` to zero;
- updates `last_seen_ts_utc` if provided;
- recalculates node score.

---

## 5. Scoring principle

The score is intentionally simple and auditable:

```text
constructive activity
- caution activity
- freshness penalty
+ active node base
```

Constructive activity:

- touch;
- sweep;
- reclaim;
- accept.

Caution activity:

- reject;
- fail.

This score is designed to rank practical references for research review. It does not claim hidden orderflow or true dealer inventory.

---

## 6. Clustering principle

`cluster_nodes(nodes, band)` groups nearby active nodes by price distance.

Cluster output:

```text
cluster_id
nodes
center_price
lower_price
upper_price
score
```

The cluster score is an average node score with a small density bonus. It is only a practical grouping score.

---

## 7. Out of scope

- No TradingView Pine source import.
- No live dashboard connection.
- No replay harness connection yet.
- No OANDA dashboard behavior change.
- No artifact generation behavior change.
- No broker execution.
- No account-risk logic.
- No statistical-edge claim.
- No real MM inventory or real retail-positioning claim.

---

## 8. Tests

Implemented tests:

```text
tests/test_liquidity_nodes.py
```

Covered cases:

- stable node IDs;
- node creation;
- reaction update;
- score increase on constructive reaction;
- score decrease on failure;
- freshness penalty;
- invalid reaction guards;
- monitor-only serialization;
- clustering;
- inactive-node exclusion;
- positive-band validation.

---

## 9. Next gate

After this PR passes CI and merges, the next safe step is:

```text
v9.0-F — Node Graph Replay Integration
```

That gate should update nodes from replay rows and produce node/cluster reports, still without live dashboard or alert integration.
