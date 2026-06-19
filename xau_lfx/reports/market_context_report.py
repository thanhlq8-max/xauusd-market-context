from __future__ import annotations

from pathlib import Path
from typing import Any

from xau_lfx.config import artifact_paths
from xau_lfx.forbidden_language import assert_clean_language
from xau_lfx.utils import read_json, utc_now_iso, write_text


def _lines_for_sessions(session_ranges: dict[str, Any]) -> list[str]:
    if not session_ranges:
        return ["- No session range could be built from the current source set."]
    lines: list[str] = []
    for name, block in session_ranges.items():
        lines.append(
            f"- {name}: bars={block.get('bar_count', 0)}, high={block.get('high')}, "
            f"low={block.get('low')}, range={block.get('range_points')}"
        )
    return lines


def _bullet_lines(items: list[Any], fallback: str) -> str:
    if not items:
        return f"- {fallback}\n"
    return "".join(f"- {item}\n" for item in items)


def _format_nearest_session_level(context_summary: dict[str, Any]) -> str:
    nearest = context_summary.get("nearest_session_level") or {}
    if not nearest:
        return "not available"
    session = nearest.get("session", "unknown")
    level = nearest.get("level", "unknown")
    price = nearest.get("price")
    distance = nearest.get("distance_points")
    return f"{session} {level} at {price}, distance={distance}"


def build_market_context_markdown(
    data_quality: dict[str, Any],
    composite: dict[str, Any],
    session: dict[str, Any],
    event: dict[str, Any],
    user_insight: dict[str, Any],
    artifact_quality: dict[str, Any],
    context_summary: dict[str, Any] | None = None,
) -> str:
    context_summary = context_summary or {}
    session_lines = _lines_for_sessions(session.get("session_ranges", {}))
    latest_close = context_summary.get("latest_close", composite.get("median_latest_close"))
    warnings = artifact_quality.get("warnings", [])
    errors = artifact_quality.get("errors", [])

    report = f"""# XAUUSD Market Context Report

Generated: {utc_now_iso()}  
Mode: monitor-only research artifact  
Symbol: {data_quality.get('symbol', 'XAUUSD')}

## Artifact Quality

- Status: {artifact_quality.get('status')}
- Quality score: {artifact_quality.get('quality_score')} / 100
- Quality grade: {artifact_quality.get('quality_grade')}
- Confidence cap: {artifact_quality.get('confidence_cap')}
- Source count: {artifact_quality.get('source_count')}

## Source Coverage

- Present timeframes: {', '.join(data_quality.get('present_timeframes', [])) or 'none'}
- Freshness score: {artifact_quality.get('freshness_score')} / 100
- Coverage score: {artifact_quality.get('coverage_score')} / 100
- Schema score: {artifact_quality.get('schema_score')} / 100
- Spread score: {artifact_quality.get('spread_score')} / 100
- Event score: {artifact_quality.get('event_score')} / 100

## Context Summary

- Latest close: {latest_close if latest_close is not None else 'not available'}
- Freshness age minutes: {context_summary.get('freshness_age_minutes', 'not available')}
- Nearest session level: {_format_nearest_session_level(context_summary)}
- Spread state: {context_summary.get('spread_state', 'not available')}
- Event risk state: {context_summary.get('event_risk_state', event.get('risk_state'))}
- Quality status: {context_summary.get('quality_status', artifact_quality.get('status'))}
- Quality grade: {context_summary.get('quality_grade', artifact_quality.get('quality_grade'))}

## Confidence Explanation

{_bullet_lines(context_summary.get('confidence_explanation', []), 'No additional confidence explanation was generated.')}

## Monitor Focus

{_bullet_lines(context_summary.get('monitor_focus', user_insight.get('operator_focus', [])), 'No monitor focus was generated.')}

## M15 Session Map

{chr(10).join(session_lines)}

## Event Risk Context

- Risk state: {event.get('risk_state')}
- Event count: {event.get('event_count', 0)}
- High-impact USD events: {len(event.get('high_impact_events', []))}
- Note: {event.get('note')}

## Current Read

- Latest cross-timeframe median close: {composite.get('median_latest_close') if composite.get('median_latest_close') is not None else 'not available'}
- Headline: {user_insight.get('headline')}
- Now: {user_insight.get('now_read')}

## What This Artifact Cannot Claim

"""

    cannot_claim = [
        "It cannot infer centralized spot-gold orderflow from broker CSV files.",
        "It cannot infer actual dealer inventory or actual retail-side positioning.",
        "It cannot provide execution instructions or profitability claims.",
        "It cannot treat broker tick activity as centralized traded volume.",
    ]
    for item in cannot_claim:
        report += f"- {item}\n"

    report += "\n## Limitations\n\n"
    report += _bullet_lines(
        context_summary.get("limitations", []),
        "No additional context-summary limitations were generated.",
    )

    report += "\n## Warnings\n\n"
    if warnings:
        for item in warnings[:30]:
            report += f"- {item}\n"
    else:
        report += "- No warnings emitted by the artifact-quality gate.\n"

    report += "\n## Errors\n\n"
    if errors:
        for item in errors[:30]:
            report += f"- {item}\n"
    else:
        report += "- No schema or source errors were emitted.\n"

    assert_clean_language(report)
    return report


def write_market_context_report(artifact_dir: str | Path, write_md: bool = True) -> str:
    paths = artifact_paths(artifact_dir)
    context_summary_path = paths.get("context_summary")
    context_summary = {}
    if context_summary_path is not None and context_summary_path.exists():
        context_summary = read_json(context_summary_path)

    report = build_market_context_markdown(
        data_quality=read_json(paths["data_quality"]),
        composite=read_json(paths["composite_ohlcv"]),
        session=read_json(paths["session_context"]),
        event=read_json(paths["event_risk"]),
        user_insight=read_json(paths["user_insight"]),
        artifact_quality=read_json(paths["artifact_quality"]),
        context_summary=context_summary,
    )
    if write_md:
        write_text(paths["market_context_report"], report)
    return report
