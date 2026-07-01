from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

SIDE_UP = "UP"
SIDE_DN = "DN"
SIDE_NONE = "NONE"

REACTION_TOUCH = "TOUCH"
REACTION_SWEEP = "SWEEP"
REACTION_RECLAIM = "RECLAIM"
REACTION_ACCEPT = "ACCEPT"
REACTION_REJECT = "REJECT"
REACTION_FAIL = "FAIL"

VALID_SIDES = {SIDE_UP, SIDE_DN, SIDE_NONE}
VALID_REACTIONS = {
    REACTION_TOUCH,
    REACTION_SWEEP,
    REACTION_RECLAIM,
    REACTION_ACCEPT,
    REACTION_REJECT,
    REACTION_FAIL,
}


@dataclass(frozen=True)
class LiquidityNode:
    node_id: str
    source: str
    price: float
    side: str = SIDE_NONE
    created_ts_utc: str | None = None
    last_seen_ts_utc: str | None = None
    freshness_bars: int = 0
    touch_count: int = 0
    sweep_count: int = 0
    reclaim_count: int = 0
    accept_count: int = 0
    reject_count: int = 0
    fail_count: int = 0
    score: float = 0.0
    active: bool = True


@dataclass(frozen=True)
class NodeReaction:
    node_id: str
    reaction: str
    ts_utc: str | None = None
    price: float | None = None
    timeframe: str | None = None
    session: str | None = None
    notes: str = ""


@dataclass(frozen=True)
class NodeCluster:
    cluster_id: str
    nodes: tuple[LiquidityNode, ...]
    center_price: float
    lower_price: float
    upper_price: float
    score: float

    @property
    def node_count(self) -> int:
        return len(self.nodes)


def _clamp_01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _normalize_side(value: str) -> str:
    side = (value or SIDE_NONE).upper()
    if side not in VALID_SIDES:
        return SIDE_NONE
    return side


def make_node_id(source: str, price: float, side: str = SIDE_NONE) -> str:
    normalized_source = source.strip().upper().replace(" ", "_") or "UNKNOWN"
    normalized_side = _normalize_side(side)
    return f"{normalized_source}:{normalized_side}:{price:.3f}"


def create_liquidity_node(
    source: str,
    price: float,
    side: str = SIDE_NONE,
    ts_utc: str | None = None,
    score: float = 0.0,
) -> LiquidityNode:
    normalized_side = _normalize_side(side)
    return LiquidityNode(
        node_id=make_node_id(source, price, normalized_side),
        source=source.strip().upper() or "UNKNOWN",
        price=float(price),
        side=normalized_side,
        created_ts_utc=ts_utc,
        last_seen_ts_utc=ts_utc,
        score=_clamp_01(score),
    )


def age_node(node: LiquidityNode, bars: int = 1) -> LiquidityNode:
    bars = max(0, int(bars))
    return replace(node, freshness_bars=node.freshness_bars + bars)


def update_node_reaction(node: LiquidityNode, reaction: NodeReaction) -> LiquidityNode:
    if reaction.node_id != node.node_id:
        raise ValueError("reaction node_id does not match node")
    reaction_type = reaction.reaction.upper()
    if reaction_type not in VALID_REACTIONS:
        raise ValueError(f"unsupported node reaction: {reaction.reaction}")

    touch_count = node.touch_count + (1 if reaction_type == REACTION_TOUCH else 0)
    sweep_count = node.sweep_count + (1 if reaction_type == REACTION_SWEEP else 0)
    reclaim_count = node.reclaim_count + (1 if reaction_type == REACTION_RECLAIM else 0)
    accept_count = node.accept_count + (1 if reaction_type == REACTION_ACCEPT else 0)
    reject_count = node.reject_count + (1 if reaction_type == REACTION_REJECT else 0)
    fail_count = node.fail_count + (1 if reaction_type == REACTION_FAIL else 0)

    updated = replace(
        node,
        last_seen_ts_utc=reaction.ts_utc or node.last_seen_ts_utc,
        touch_count=touch_count,
        sweep_count=sweep_count,
        reclaim_count=reclaim_count,
        accept_count=accept_count,
        reject_count=reject_count,
        fail_count=fail_count,
        freshness_bars=0,
    )
    return replace(updated, score=score_node(updated))


def score_node(node: LiquidityNode) -> float:
    constructive = (node.touch_count * 0.07) + (node.sweep_count * 0.16) + (node.reclaim_count * 0.24) + (node.accept_count * 0.18)
    caution = (node.reject_count * 0.10) + (node.fail_count * 0.20)
    freshness_penalty = min(0.35, node.freshness_bars * 0.015)
    activity_score = constructive - caution - freshness_penalty
    base = 0.25 if node.active else 0.0
    return round(_clamp_01(base + activity_score), 4)


def serialize_node(node: LiquidityNode) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "source": node.source,
        "price": node.price,
        "side": node.side,
        "created_ts_utc": node.created_ts_utc,
        "last_seen_ts_utc": node.last_seen_ts_utc,
        "freshness_bars": node.freshness_bars,
        "touch_count": node.touch_count,
        "sweep_count": node.sweep_count,
        "reclaim_count": node.reclaim_count,
        "accept_count": node.accept_count,
        "reject_count": node.reject_count,
        "fail_count": node.fail_count,
        "score": node.score,
        "active": node.active,
        "monitor_only": True,
    }


def cluster_nodes(nodes: list[LiquidityNode], band: float) -> list[NodeCluster]:
    if band <= 0:
        raise ValueError("band must be positive")
    active_nodes = sorted((node for node in nodes if node.active), key=lambda node: node.price)
    clusters: list[NodeCluster] = []
    current: list[LiquidityNode] = []

    for node in active_nodes:
        if not current:
            current = [node]
            continue
        current_center = sum(item.price for item in current) / len(current)
        if abs(node.price - current_center) <= band:
            current.append(node)
        else:
            clusters.append(_build_cluster(current, len(clusters) + 1))
            current = [node]
    if current:
        clusters.append(_build_cluster(current, len(clusters) + 1))
    return clusters


def _build_cluster(nodes: list[LiquidityNode], index: int) -> NodeCluster:
    prices = [node.price for node in nodes]
    total_score = sum(node.score for node in nodes)
    center = sum(prices) / len(prices)
    return NodeCluster(
        cluster_id=f"CLUSTER:{index:03d}",
        nodes=tuple(nodes),
        center_price=round(center, 4),
        lower_price=min(prices),
        upper_price=max(prices),
        score=round(_clamp_01(total_score / max(1, len(nodes)) + min(0.2, len(nodes) * 0.03)), 4),
    )


def serialize_cluster(cluster: NodeCluster) -> dict[str, Any]:
    return {
        "cluster_id": cluster.cluster_id,
        "center_price": cluster.center_price,
        "lower_price": cluster.lower_price,
        "upper_price": cluster.upper_price,
        "score": cluster.score,
        "node_ids": [node.node_id for node in cluster.nodes],
        "node_count": cluster.node_count,
        "monitor_only": True,
    }
