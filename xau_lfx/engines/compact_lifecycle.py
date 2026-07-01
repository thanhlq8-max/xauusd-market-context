from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from xau_lfx.forbidden_language import assert_clean_language

SIDE_UP = "UP"
SIDE_DN = "DN"
SIDE_NONE = "NONE"

PS_NONE = "NO_SWEEP"
PS_RAW = "RAW_SPIKE"
PS_RECLAIM = "RECLAIM"
PS_ACCEPT = "ACCEPT"
PS_REJECT = "REJECT"
PS_RECLAIM_FAIL = "RECLAIM_FAIL"
PS_ACCEPT_FAIL = "ACCEPT_FAIL"

DS_NONE = "D_NONE"
DS_ACTIVE = "D_ACTIVE"
DS_STALL = "D_STALL"
DS_COUNTERFLOW = "D_COUNTERFLOW"
DS_TARGET_HIT = "D_TARGET_HIT"
DS_FAILED = "D_FAILED"


@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float
    atr: float
    tick_activity: float = 0.0


@dataclass(frozen=True)
class LiquidityLevel:
    source: str
    price: float
    side: str = SIDE_NONE
    freshness_bars: int = 0
    score: float = 1.0


@dataclass(frozen=True)
class SweepLifecycle:
    state: str
    source: str | None
    level: float | None
    sweep_side: str
    route_dir: str
    confidence: float
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class RouteCandidate:
    route_dir: str
    origin_source: str | None
    origin_level: float | None
    target_source: str | None
    target_ref: float | None
    initial_distance_atr: float | None
    confidence: float
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class DeliveryHealth:
    state: str
    route_dir: str
    target_ref: float | None
    current_distance_atr: float | None
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class LifecycleSnapshot:
    monitor_only: bool
    lifecycle: dict[str, Any]
    route: dict[str, Any]
    delivery: dict[str, Any]


def _safe_atr(value: float) -> float:
    return max(float(value), 1e-9)


def _clamp_01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def candle_metrics(candle: Candle) -> dict[str, float]:
    atr = _safe_atr(candle.atr)
    full_range = max(candle.high - candle.low, 0.0)
    body = abs(candle.close - candle.open)
    upper_wick = max(candle.high - max(candle.open, candle.close), 0.0)
    lower_wick = max(min(candle.open, candle.close) - candle.low, 0.0)
    metrics = {
        "range_atr": full_range / atr,
        "body_atr": body / atr,
        "upper_wick_atr": upper_wick / atr,
        "lower_wick_atr": lower_wick / atr,
        "body_ratio": body / full_range if full_range > 0 else 0.0,
        "tick_activity": float(candle.tick_activity),
    }
    assert_clean_language(metrics)
    return metrics


def detect_sweep(candle: Candle, level: LiquidityLevel, near_atr: float = 0.12) -> bool:
    atr = _safe_atr(candle.atr)
    near_band = atr * max(0.0, near_atr)
    if level.side == SIDE_UP:
        return candle.high > level.price and candle.low <= level.price + near_band
    if level.side == SIDE_DN:
        return candle.low < level.price and candle.high >= level.price - near_band
    return (
        (candle.high > level.price and candle.low <= level.price + near_band)
        or (candle.low < level.price and candle.high >= level.price - near_band)
    )


def infer_sweep_side(candle: Candle, level: LiquidityLevel) -> str:
    if level.side in {SIDE_UP, SIDE_DN}:
        return level.side
    up_distance = max(candle.high - level.price, 0.0)
    dn_distance = max(level.price - candle.low, 0.0)
    if up_distance > dn_distance:
        return SIDE_UP
    if dn_distance > up_distance:
        return SIDE_DN
    return SIDE_NONE


def classify_sweep_lifecycle(
    candle: Candle,
    level: LiquidityLevel,
    accept_atr: float = 0.08,
    reclaim_atr: float = 0.02,
) -> SweepLifecycle:
    if not detect_sweep(candle, level):
        result = SweepLifecycle(
            state=PS_NONE,
            source=None,
            level=None,
            sweep_side=SIDE_NONE,
            route_dir=SIDE_NONE,
            confidence=0.0,
            evidence=("no_valid_level_interaction",),
        )
        assert_clean_language(result.__dict__)
        return result

    atr = _safe_atr(candle.atr)
    sweep_side = infer_sweep_side(candle, level)
    accept_band = atr * max(0.0, accept_atr)
    reclaim_band = atr * max(0.0, reclaim_atr)
    metrics = candle_metrics(candle)

    if sweep_side == SIDE_UP:
        if candle.close < level.price - reclaim_band:
            state = PS_RECLAIM
            route_dir = SIDE_DN
            evidence = ("upper_level_swept", "closed_back_below_level")
        elif candle.close > level.price + accept_band:
            state = PS_ACCEPT
            route_dir = SIDE_UP
            evidence = ("upper_level_swept", "closed_beyond_level")
        else:
            state = PS_RAW
            route_dir = SIDE_NONE
            evidence = ("upper_level_swept", "close_near_level")
    elif sweep_side == SIDE_DN:
        if candle.close > level.price + reclaim_band:
            state = PS_RECLAIM
            route_dir = SIDE_UP
            evidence = ("lower_level_swept", "closed_back_above_level")
        elif candle.close < level.price - accept_band:
            state = PS_ACCEPT
            route_dir = SIDE_DN
            evidence = ("lower_level_swept", "closed_beyond_level")
        else:
            state = PS_RAW
            route_dir = SIDE_NONE
            evidence = ("lower_level_swept", "close_near_level")
    else:
        state = PS_RAW
        route_dir = SIDE_NONE
        evidence = ("level_interaction_detected", "side_unclear")

    impulse_score = _clamp_01(metrics["range_atr"] / 1.8)
    source_score = _clamp_01(level.score)
    confidence = round(_clamp_01((impulse_score * 0.55) + (source_score * 0.45)), 4)
    result = SweepLifecycle(
        state=state,
        source=level.source,
        level=level.price,
        sweep_side=sweep_side,
        route_dir=route_dir,
        confidence=confidence,
        evidence=evidence,
    )
    assert_clean_language(result.__dict__)
    return result


def select_route_target(
    current_price: float,
    route_dir: str,
    levels: list[LiquidityLevel],
) -> LiquidityLevel | None:
    if route_dir == SIDE_UP:
        candidates = [level for level in levels if level.price > current_price]
        return min(candidates, key=lambda level: level.price - current_price) if candidates else None
    if route_dir == SIDE_DN:
        candidates = [level for level in levels if level.price < current_price]
        return min(candidates, key=lambda level: current_price - level.price) if candidates else None
    return None


def build_route_candidate(
    candle: Candle,
    lifecycle: SweepLifecycle,
    target_levels: list[LiquidityLevel],
) -> RouteCandidate:
    if lifecycle.state not in {PS_RECLAIM, PS_ACCEPT} or lifecycle.route_dir == SIDE_NONE:
        result = RouteCandidate(
            route_dir=SIDE_NONE,
            origin_source=lifecycle.source,
            origin_level=lifecycle.level,
            target_source=None,
            target_ref=None,
            initial_distance_atr=None,
            confidence=0.0,
            evidence=("route_not_resolved",),
        )
        assert_clean_language(result.__dict__)
        return result

    target = select_route_target(candle.close, lifecycle.route_dir, target_levels)
    if target is None:
        result = RouteCandidate(
            route_dir=lifecycle.route_dir,
            origin_source=lifecycle.source,
            origin_level=lifecycle.level,
            target_source=None,
            target_ref=None,
            initial_distance_atr=None,
            confidence=round(lifecycle.confidence * 0.55, 4),
            evidence=("route_resolved", "target_missing"),
        )
        assert_clean_language(result.__dict__)
        return result

    atr = _safe_atr(candle.atr)
    distance_atr = abs(target.price - candle.close) / atr
    distance_quality = _clamp_01(1.0 - max(0.0, distance_atr - 3.0) / 6.0)
    confidence = round(_clamp_01((lifecycle.confidence * 0.7) + (target.score * 0.2) + (distance_quality * 0.1)), 4)
    result = RouteCandidate(
        route_dir=lifecycle.route_dir,
        origin_source=lifecycle.source,
        origin_level=lifecycle.level,
        target_source=target.source,
        target_ref=target.price,
        initial_distance_atr=round(distance_atr, 4),
        confidence=confidence,
        evidence=("route_resolved", "target_locked"),
    )
    assert_clean_language(result.__dict__)
    return result


def evaluate_delivery_health(
    candle: Candle,
    route: RouteCandidate,
    flow_skew: float = 0.0,
    route_age_bars: int = 0,
    stall_bars: int = 8,
    fail_bars: int = 16,
) -> DeliveryHealth:
    if route.route_dir == SIDE_NONE or route.target_ref is None:
        result = DeliveryHealth(
            state=DS_NONE,
            route_dir=SIDE_NONE,
            target_ref=None,
            current_distance_atr=None,
            evidence=("no_locked_route",),
        )
        assert_clean_language(result.__dict__)
        return result

    atr = _safe_atr(candle.atr)
    current_distance_atr = abs(route.target_ref - candle.close) / atr
    route_sign = 1 if route.route_dir == SIDE_UP else -1
    counterflow = route_sign * float(flow_skew) < -0.20
    initial_distance = route.initial_distance_atr if route.initial_distance_atr is not None else current_distance_atr
    stale_distance = current_distance_atr > initial_distance * 0.72

    target_hit = (
        (route.route_dir == SIDE_UP and candle.high >= route.target_ref)
        or (route.route_dir == SIDE_DN and candle.low <= route.target_ref)
    )
    if target_hit:
        state = DS_TARGET_HIT
        evidence = ("target_reached",)
    elif route_age_bars >= fail_bars and (counterflow or current_distance_atr > initial_distance):
        state = DS_FAILED
        evidence = ("route_failed", "age_or_distance_guard")
    elif counterflow:
        state = DS_COUNTERFLOW
        evidence = ("route_under_counterflow",)
    elif route_age_bars >= stall_bars and stale_distance:
        state = DS_STALL
        evidence = ("route_stalled",)
    else:
        state = DS_ACTIVE
        evidence = ("route_active",)

    result = DeliveryHealth(
        state=state,
        route_dir=route.route_dir,
        target_ref=route.target_ref,
        current_distance_atr=round(current_distance_atr, 4),
        evidence=evidence,
    )
    assert_clean_language(result.__dict__)
    return result


def build_lifecycle_snapshot(
    candle: Candle,
    trigger_level: LiquidityLevel,
    target_levels: list[LiquidityLevel],
    flow_skew: float = 0.0,
    route_age_bars: int = 0,
) -> LifecycleSnapshot:
    lifecycle = classify_sweep_lifecycle(candle, trigger_level)
    route = build_route_candidate(candle, lifecycle, target_levels)
    delivery = evaluate_delivery_health(
        candle=candle,
        route=route,
        flow_skew=flow_skew,
        route_age_bars=route_age_bars,
    )
    snapshot = LifecycleSnapshot(
        monitor_only=True,
        lifecycle=lifecycle.__dict__,
        route=route.__dict__,
        delivery=delivery.__dict__,
    )
    assert_clean_language(snapshot.__dict__)
    return snapshot
