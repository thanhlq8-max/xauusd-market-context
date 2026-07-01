from xau_lfx.engines.compact_lifecycle import (
    DS_ACTIVE,
    DS_COUNTERFLOW,
    DS_FAILED,
    DS_NONE,
    DS_STALL,
    DS_TARGET_HIT,
    PS_ACCEPT,
    PS_NONE,
    PS_RECLAIM,
    Candle,
    LiquidityLevel,
    RouteCandidate,
    build_lifecycle_snapshot,
    build_route_candidate,
    classify_sweep_lifecycle,
    evaluate_delivery_health,
)


def test_no_interaction_returns_no_sweep():
    candle = Candle(open=100.0, high=100.4, low=99.8, close=100.1, atr=1.0)
    level = LiquidityLevel(source="PDH", price=101.0, side="UP")

    lifecycle = classify_sweep_lifecycle(candle, level)

    assert lifecycle.state == PS_NONE
    assert lifecycle.route_dir == "NONE"
    assert lifecycle.confidence == 0.0


def test_upper_level_reclaim_routes_down_to_nearest_lower_target():
    candle = Candle(open=100.1, high=101.2, low=99.6, close=99.7, atr=1.0)
    level = LiquidityLevel(source="PDH", price=100.5, side="UP", score=0.8)
    targets = [
        LiquidityLevel(source="PDL", price=97.5, side="DN", score=0.7),
        LiquidityLevel(source="NYL", price=98.8, side="DN", score=0.9),
    ]

    lifecycle = classify_sweep_lifecycle(candle, level)
    route = build_route_candidate(candle, lifecycle, targets)

    assert lifecycle.state == PS_RECLAIM
    assert lifecycle.route_dir == "DN"
    assert route.route_dir == "DN"
    assert route.target_source == "NYL"
    assert route.target_ref == 98.8
    assert route.initial_distance_atr == 0.9


def test_lower_level_reclaim_routes_up_to_nearest_upper_target():
    candle = Candle(open=100.0, high=100.8, low=98.9, close=100.35, atr=1.0)
    level = LiquidityLevel(source="PDL", price=99.5, side="DN", score=0.9)
    targets = [
        LiquidityLevel(source="PDH", price=102.5, side="UP", score=0.7),
        LiquidityLevel(source="ROUND", price=101.0, side="UP", score=0.8),
    ]

    lifecycle = classify_sweep_lifecycle(candle, level)
    route = build_route_candidate(candle, lifecycle, targets)

    assert lifecycle.state == PS_RECLAIM
    assert lifecycle.route_dir == "UP"
    assert route.target_source == "ROUND"
    assert route.target_ref == 101.0


def test_accept_continues_through_level():
    candle = Candle(open=100.0, high=102.0, low=99.7, close=101.2, atr=1.0)
    level = LiquidityLevel(source="ROUND", price=100.5, side="UP", score=0.75)

    lifecycle = classify_sweep_lifecycle(candle, level)

    assert lifecycle.state == PS_ACCEPT
    assert lifecycle.route_dir == "UP"
    assert "closed_beyond_level" in lifecycle.evidence


def test_route_without_target_remains_monitorable_but_low_confidence():
    candle = Candle(open=100.0, high=100.9, low=98.8, close=100.4, atr=1.0)
    level = LiquidityLevel(source="PDL", price=99.5, side="DN", score=0.9)

    lifecycle = classify_sweep_lifecycle(candle, level)
    route = build_route_candidate(candle, lifecycle, [])
    health = evaluate_delivery_health(candle, route)

    assert route.route_dir == "UP"
    assert route.target_ref is None
    assert health.state == DS_NONE


def test_delivery_target_hit_dominates_active_state():
    candle = Candle(open=101.0, high=102.2, low=100.8, close=101.9, atr=1.0)
    route = RouteCandidate(
        route_dir="UP",
        origin_source="PDL",
        origin_level=99.5,
        target_source="PDH",
        target_ref=102.0,
        initial_distance_atr=2.0,
        confidence=0.6,
        evidence=("route_resolved",),
    )

    health = evaluate_delivery_health(candle, route, flow_skew=-0.3, route_age_bars=10)

    assert health.state == DS_TARGET_HIT
    assert health.target_ref == 102.0


def test_delivery_counterflow_before_terminal_fail():
    candle = Candle(open=100.0, high=100.4, low=99.7, close=100.1, atr=1.0)
    route = RouteCandidate(
        route_dir="UP",
        origin_source="PDL",
        origin_level=99.5,
        target_source="PDH",
        target_ref=102.0,
        initial_distance_atr=2.0,
        confidence=0.6,
        evidence=("route_resolved",),
    )

    health = evaluate_delivery_health(candle, route, flow_skew=-0.25, route_age_bars=4)

    assert health.state == DS_COUNTERFLOW


def test_delivery_stall_when_route_is_old_and_not_progressing():
    candle = Candle(open=100.0, high=100.3, low=99.8, close=100.1, atr=1.0)
    route = RouteCandidate(
        route_dir="UP",
        origin_source="PDL",
        origin_level=99.5,
        target_source="PDH",
        target_ref=102.0,
        initial_distance_atr=2.2,
        confidence=0.6,
        evidence=("route_resolved",),
    )

    health = evaluate_delivery_health(candle, route, flow_skew=0.0, route_age_bars=8)

    assert health.state == DS_STALL


def test_delivery_failure_when_route_is_old_and_worse_than_lock():
    candle = Candle(open=100.0, high=100.2, low=99.3, close=99.5, atr=1.0)
    route = RouteCandidate(
        route_dir="UP",
        origin_source="PDL",
        origin_level=99.5,
        target_source="PDH",
        target_ref=102.0,
        initial_distance_atr=2.0,
        confidence=0.6,
        evidence=("route_resolved",),
    )

    health = evaluate_delivery_health(candle, route, flow_skew=0.0, route_age_bars=16)

    assert health.state == DS_FAILED


def test_active_route_without_pressure_stays_active():
    candle = Candle(open=100.0, high=100.8, low=99.8, close=100.7, atr=1.0)
    route = RouteCandidate(
        route_dir="UP",
        origin_source="PDL",
        origin_level=99.5,
        target_source="PDH",
        target_ref=102.0,
        initial_distance_atr=2.0,
        confidence=0.6,
        evidence=("route_resolved",),
    )

    health = evaluate_delivery_health(candle, route, flow_skew=0.1, route_age_bars=3)

    assert health.state == DS_ACTIVE


def test_lifecycle_snapshot_preserves_monitor_only_contract():
    candle = Candle(open=100.0, high=100.8, low=98.9, close=100.4, atr=1.0)
    trigger = LiquidityLevel(source="PDL", price=99.5, side="DN", score=0.9)
    targets = [LiquidityLevel(source="PDH", price=101.0, side="UP", score=0.8)]

    snapshot = build_lifecycle_snapshot(candle, trigger, targets, flow_skew=0.0, route_age_bars=1)

    assert snapshot.monitor_only is True
    assert snapshot.lifecycle["state"] == PS_RECLAIM
    assert snapshot.route["target_ref"] == 101.0
    assert snapshot.delivery["state"] == DS_ACTIVE
