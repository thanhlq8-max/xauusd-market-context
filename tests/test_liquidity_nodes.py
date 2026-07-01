import pytest

from xau_lfx.engines.liquidity_nodes import (
    REACTION_ACCEPT,
    REACTION_FAIL,
    REACTION_RECLAIM,
    REACTION_SWEEP,
    REACTION_TOUCH,
    LiquidityNode,
    NodeReaction,
    age_node,
    cluster_nodes,
    create_liquidity_node,
    make_node_id,
    score_node,
    serialize_cluster,
    serialize_node,
    update_node_reaction,
)


def test_make_node_id_is_stable_and_normalized():
    assert make_node_id("pdh", 4044.14, "up") == "PDH:UP:4044.140"


def test_create_liquidity_node_preserves_monitor_fields():
    node = create_liquidity_node("pdl", 3998.5, "dn", ts_utc="2026-07-01T08:00:00Z", score=0.3)

    assert node.node_id == "PDL:DN:3998.500"
    assert node.source == "PDL"
    assert node.side == "DN"
    assert node.score == 0.3
    assert node.created_ts_utc == "2026-07-01T08:00:00Z"


def test_update_node_reaction_counts_and_resets_freshness():
    node = create_liquidity_node("round", 4050.0, "up", score=0.2)
    node = age_node(node, 5)
    reaction = NodeReaction(node_id=node.node_id, reaction=REACTION_SWEEP, ts_utc="2026-07-01T09:00:00Z")

    updated = update_node_reaction(node, reaction)

    assert updated.sweep_count == 1
    assert updated.freshness_bars == 0
    assert updated.last_seen_ts_utc == "2026-07-01T09:00:00Z"
    assert updated.score > node.score


def test_reclaim_increases_score_more_than_touch():
    touch_node = create_liquidity_node("pdh", 4044.14, "up")
    reclaim_node = create_liquidity_node("pdh", 4044.14, "up")

    touch_node = update_node_reaction(touch_node, NodeReaction(touch_node.node_id, REACTION_TOUCH))
    reclaim_node = update_node_reaction(reclaim_node, NodeReaction(reclaim_node.node_id, REACTION_RECLAIM))

    assert reclaim_node.score > touch_node.score


def test_fail_reduces_node_score_after_constructive_reactions():
    node = create_liquidity_node("nyh", 4075.0, "up")
    node = update_node_reaction(node, NodeReaction(node.node_id, REACTION_TOUCH))
    node = update_node_reaction(node, NodeReaction(node.node_id, REACTION_SWEEP))
    before_fail = node.score
    node = update_node_reaction(node, NodeReaction(node.node_id, REACTION_FAIL))

    assert node.fail_count == 1
    assert node.score < before_fail


def test_age_node_applies_freshness_penalty():
    node = create_liquidity_node("asiah", 4020.0, "up")
    node = update_node_reaction(node, NodeReaction(node.node_id, REACTION_ACCEPT))
    fresh_score = node.score
    aged = age_node(node, 20)

    assert aged.freshness_bars == 20
    assert score_node(aged) < fresh_score


def test_update_node_reaction_rejects_wrong_node_id():
    node = create_liquidity_node("pdh", 4044.14, "up")

    with pytest.raises(ValueError, match="reaction node_id does not match node"):
        update_node_reaction(node, NodeReaction("OTHER", REACTION_TOUCH))


def test_update_node_reaction_rejects_unknown_reaction():
    node = create_liquidity_node("pdh", 4044.14, "up")

    with pytest.raises(ValueError, match="unsupported node reaction"):
        update_node_reaction(node, NodeReaction(node.node_id, "UNKNOWN"))


def test_serialize_node_is_monitor_only():
    node = create_liquidity_node("round", 4050.0, "up")
    payload = serialize_node(node)

    assert payload["node_id"] == "ROUND:UP:4050.000"
    assert payload["monitor_only"] is True


def test_cluster_nodes_groups_nearby_active_nodes():
    node_a = create_liquidity_node("pdh", 4044.0, "up", score=0.4)
    node_b = create_liquidity_node("round", 4044.5, "up", score=0.6)
    node_c = create_liquidity_node("pdl", 4010.0, "dn", score=0.5)

    clusters = cluster_nodes([node_a, node_b, node_c], band=1.0)

    assert len(clusters) == 2
    assert clusters[0].node_count == 2
    assert clusters[0].lower_price == 4044.0
    assert clusters[0].upper_price == 4044.5
    assert clusters[1].node_count == 1


def test_cluster_nodes_ignores_inactive_nodes():
    active = create_liquidity_node("pdh", 4044.0, "up", score=0.4)
    inactive = LiquidityNode(
        node_id="OLD:UP:4044.200",
        source="OLD",
        price=4044.2,
        side="UP",
        active=False,
    )

    clusters = cluster_nodes([active, inactive], band=1.0)

    assert len(clusters) == 1
    assert clusters[0].node_count == 1


def test_cluster_nodes_requires_positive_band():
    node = create_liquidity_node("pdh", 4044.0, "up")

    with pytest.raises(ValueError, match="band must be positive"):
        cluster_nodes([node], band=0)


def test_serialize_cluster_is_monitor_only():
    node = create_liquidity_node("pdh", 4044.0, "up", score=0.4)
    cluster = cluster_nodes([node], band=1.0)[0]
    payload = serialize_cluster(cluster)

    assert payload["cluster_id"] == "CLUSTER:001"
    assert payload["node_count"] == 1
    assert payload["monitor_only"] is True
