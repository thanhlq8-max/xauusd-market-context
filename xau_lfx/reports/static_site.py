from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

from xau_lfx.config import artifact_paths
from xau_lfx.forbidden_language import assert_clean_language
from xau_lfx.utils import read_json, utc_now_iso, write_text

_JSON_ARTIFACT_KEYS = (
    "raw_scan",
    "data_quality",
    "composite_ohlcv",
    "session_context",
    "macro_pressure",
    "event_risk",
    "state",
    "user_insight",
    "artifact_quality",
    "context_summary",
)


def _load_optional_json(paths: dict[str, Path], key: str) -> dict[str, Any]:
    path = paths[key]
    return read_json(path) if path.exists() else {}


def _html_list(items: list[Any]) -> str:
    if not items:
        return "<li>No items emitted.</li>"
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _html_zone_cards(zones: list[dict[str, Any]]) -> str:
    if not zones:
        return "<p>No practical zone deck emitted.</p>"
    cards: list[str] = []
    for zone in zones:
        rank = html.escape(str(zone.get("rank", "n/a")))
        session = html.escape(str(zone.get("session", "unknown")))
        level = html.escape(str(zone.get("level", "unknown")))
        price = html.escape(str(zone.get("price", "n/a")))
        side = html.escape(str(zone.get("side_from_latest", "n/a")))
        distance = html.escape(str(zone.get("distance_points", "n/a")))
        operator_read = html.escape(str(zone.get("operator_read", "Observe this supplied session reference.")))
        cards.append(
            '<div class="card">'
            f'<div class="label">Rank {rank}</div>'
            f'<div class="small-value">{session} {level} @ {price}</div>'
            f'<p>{side}, distance={distance} pts</p>'
            f'<p>{operator_read}</p>'
            "</div>"
        )
    return '<section class="grid" aria-label="practical zone deck">' + "".join(cards) + "</section>"


def _artifact_link_rows(out_dir: Path, source_artifact_dir: Path) -> str:
    exported_artifact_dir = out_dir / "artifacts"
    candidate_dir = exported_artifact_dir if exported_artifact_dir.exists() else source_artifact_dir
    rows = []
    for path in sorted(candidate_dir.glob("*")):
        if path.is_file():
            label = html.escape(path.name)
            rows.append(f'<li><a href="artifacts/{label}">{label}</a></li>')
    return "\n".join(rows) if rows else "<li>No exported artifacts.</li>"


def build_static_site_html(artifact_dir: str | Path, out_dir: str | Path = "site") -> str:
    paths = artifact_paths(artifact_dir)
    data_quality = _load_optional_json(paths, "data_quality")
    state = _load_optional_json(paths, "state")
    user_insight = _load_optional_json(paths, "user_insight")
    artifact_quality = _load_optional_json(paths, "artifact_quality")
    context_summary = _load_optional_json(paths, "context_summary")
    event = _load_optional_json(paths, "event_risk")

    quality_score = artifact_quality.get("quality_score", "n/a")
    quality_grade = artifact_quality.get("quality_grade", "n/a")
    status = artifact_quality.get("status", "UNKNOWN")
    symbol = data_quality.get("symbol", "XAUUSD")
    present_timeframes = ", ".join(data_quality.get("present_timeframes", [])) or "none"
    state_label = state.get("state", "UNKNOWN")
    headline = user_insight.get("headline", "No insight artifact generated yet.")
    now_read = user_insight.get("now_read", "No current read generated yet.")
    operator_focus = user_insight.get("operator_focus", [])
    warnings = artifact_quality.get("warnings", [])
    errors = artifact_quality.get("errors", [])
    high_impact_count = len(event.get("high_impact_events", []))
    latest_close = context_summary.get("latest_close", "n/a")
    freshness_age = context_summary.get("freshness_age_minutes", "n/a")
    spread_state = context_summary.get("spread_state", "UNKNOWN")
    nearest_level = context_summary.get("nearest_session_level") or {}
    nearest_text = (
        f"{nearest_level.get('session')} {nearest_level.get('level')} @ {nearest_level.get('price')} "
        f"({nearest_level.get('distance_points')} pts)"
        if nearest_level
        else "not available"
    )
    practical_zones = context_summary.get("practical_zone_deck", [])
    confidence_explanation = context_summary.get("confidence_explanation", [])
    monitor_focus = context_summary.get("monitor_focus") or operator_focus
    generated = utc_now_iso()

    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>XAUUSD Market Context Demo</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; padding: 0; line-height: 1.55; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 20px 56px; }}
    header {{ border-bottom: 1px solid #8884; margin-bottom: 24px; padding-bottom: 16px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }}
    .card {{ border: 1px solid #8884; border-radius: 12px; padding: 14px; background: #8881; }}
    .label {{ font-size: 0.82rem; opacity: 0.75; }}
    .value {{ font-size: 1.35rem; font-weight: 700; }}
    .small-value {{ font-size: 1.0rem; font-weight: 700; }}
    code {{ background: #8882; padding: 2px 5px; border-radius: 5px; }}
    pre {{ overflow: auto; padding: 12px; border-radius: 10px; background: #8882; }}
    a {{ font-weight: 600; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>XAUUSD Market Context</h1>
    <p>Static demo generated from local XAUUSD artifacts. Monitor-only research output; no execution or account-risk logic.</p>
  </header>

  <section class="grid" aria-label="quality summary">
    <div class="card"><div class="label">Symbol</div><div class="value">{html.escape(str(symbol))}</div></div>
    <div class="card"><div class="label">Status</div><div class="value">{html.escape(str(status))}</div></div>
    <div class="card"><div class="label">Quality</div><div class="value">{html.escape(str(quality_score))} / 100</div></div>
    <div class="card"><div class="label">Grade</div><div class="value">{html.escape(str(quality_grade))}</div></div>
    <div class="card"><div class="label">State</div><div class="value">{html.escape(str(state_label))}</div></div>
    <div class="card"><div class="label">High-impact USD events</div><div class="value">{high_impact_count}</div></div>
  </section>

  <section>
    <h2>Context Summary</h2>
    <section class="grid" aria-label="context summary">
      <div class="card"><div class="label">Latest close</div><div class="value">{html.escape(str(latest_close))}</div></div>
      <div class="card"><div class="label">Freshness age</div><div class="value">{html.escape(str(freshness_age))} min</div></div>
      <div class="card"><div class="label">Spread state</div><div class="value">{html.escape(str(spread_state))}</div></div>
      <div class="card"><div class="label">Nearest session level</div><div class="small-value">{html.escape(str(nearest_text))}</div></div>
    </section>
  </section>

  <section>
    <h2>Practical Zone Deck</h2>
    {_html_zone_cards(practical_zones)}
  </section>

  <section>
    <h2>Confidence Explanation</h2>
    <ul>{_html_list(confidence_explanation)}</ul>
  </section>

  <section>
    <h2>Current Read</h2>
    <p><strong>{html.escape(str(headline))}</strong></p>
    <p>{html.escape(str(now_read))}</p>
  </section>

  <section>
    <h2>Source Coverage</h2>
    <ul>
      <li>Present timeframes: <code>{html.escape(present_timeframes)}</code></li>
      <li>Source count: <code>{html.escape(str(data_quality.get("source_count", 0)))}</code></li>
      <li>Confidence cap: <code>{html.escape(str(artifact_quality.get("confidence_cap", "n/a")))}</code></li>
    </ul>
  </section>

  <section>
    <h2>What To Monitor</h2>
    <ul>{_html_list(monitor_focus)}</ul>
  </section>

  <section>
    <h2>Warnings</h2>
    <ul>{_html_list(warnings)}</ul>
  </section>

  <section>
    <h2>Errors</h2>
    <ul>{_html_list(errors)}</ul>
  </section>

  <section>
    <h2>Exported Artifacts</h2>
    <ul>{_artifact_link_rows(Path(out_dir), Path(artifact_dir))}</ul>
  </section>

  <section>
    <h2>Reproduce Locally</h2>
    <pre>python -m xau_lfx.pipeline run-once --input-dir examples/sample-data --event-file examples/sample-data/usd_events.csv --out-dir artifacts
python -m xau_lfx.pipeline site --artifact-dir artifacts --out-dir site</pre>
  </section>

  <footer>
    <p>Generated: {html.escape(generated)}</p>
  </footer>
</main>
</body>
</html>
"""
    assert_clean_language(body)
    return body


def write_static_site(artifact_dir: str | Path, out_dir: str | Path = "site") -> Path:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    exported_artifacts = out_path / "artifacts"
    exported_artifacts.mkdir(parents=True, exist_ok=True)

    paths = artifact_paths(artifact_dir)
    for key in _JSON_ARTIFACT_KEYS:
        source = paths[key]
        if source.exists():
            shutil.copy2(source, exported_artifacts / source.name)
    report = paths["market_context_report"]
    if report.exists():
        shutil.copy2(report, exported_artifacts / report.name)

    html_doc = build_static_site_html(artifact_dir=artifact_dir, out_dir=out_path)
    index_path = out_path / "index.html"
    write_text(index_path, html_doc)
    return index_path
