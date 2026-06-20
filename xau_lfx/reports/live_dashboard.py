from __future__ import annotations

from xau_lfx.forbidden_language import assert_clean_language


def build_live_dashboard_html() -> str:
    document = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>XAUUSD Live Context</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1020; --panel: #121a2d; --panel-2: #17223a; --line: #2a3652;
      --ink: #f4f7fb; --muted: #9aa8bf; --blue: #5d83ff; --gold: #e4a84b;
      --warn: #ffbf69; --bad: #ff8d85; --radius: 16px;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: radial-gradient(circle at 85% 0, #19284b 0, var(--bg) 38%); color: var(--ink); }
    main { width: min(1240px, 100%); margin: 0 auto; padding: 22px; }
    header { display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; margin-bottom: 18px; }
    h1 { margin: 3px 0 6px; font-size: clamp(1.65rem, 4vw, 2.55rem); letter-spacing: -0.035em; }
    h2 { margin: 0 0 12px; font-size: 1rem; letter-spacing: .02em; }
    p { margin: 0; color: var(--muted); }
    .eyebrow, .label { color: var(--muted); font-size: .72rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; }
    .status { display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--line); border-radius: 999px; padding: 8px 12px; background: #0c1428; white-space: nowrap; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--warn); box-shadow: 0 0 0 4px #ffbf6920; }
    .status.ok .dot { background: var(--blue); box-shadow: 0 0 0 4px #5d83ff20; }
    .status.stale .dot { background: var(--bad); box-shadow: 0 0 0 4px #ff8d8520; }
    .metrics { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-bottom: 10px; }
    .card, .panel { border: 1px solid var(--line); background: linear-gradient(145deg, #151e33, #10182a); border-radius: var(--radius); }
    .card { padding: 14px; min-height: 92px; }
    .value { margin-top: 8px; font: 700 clamp(1.05rem, 3vw, 1.45rem)/1.1 ui-monospace, SFMono-Regular, Consolas, monospace; overflow-wrap: anywhere; }
    .sub { margin-top: 7px; color: var(--muted); font-size: .76rem; }
    .layout { display: grid; grid-template-columns: minmax(0, 1.75fr) minmax(290px, .75fr); gap: 10px; }
    .panel { padding: 16px; min-width: 0; }
    .chart-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
    .tabs { display: flex; gap: 5px; }
    button { border: 1px solid var(--line); color: var(--muted); background: #0d1528; border-radius: 9px; padding: 7px 10px; font: inherit; font-size: .78rem; cursor: pointer; }
    button[aria-pressed="true"] { color: var(--ink); border-color: var(--blue); background: #20345f; }
    canvas { display: block; width: 100%; height: 340px; background: #0d1424; border-radius: 12px; }
    .stack { display: grid; gap: 10px; }
    .question { padding: 14px; border: 1px solid var(--line); border-radius: 12px; background: #0e172a; }
    .question strong { display: block; margin: 6px 0; font-size: .96rem; }
    .question p { font-size: .82rem; line-height: 1.45; }
    .zones { display: grid; gap: 7px; }
    .zone { display: grid; grid-template-columns: 72px 1fr 1fr; gap: 8px; align-items: center; padding: 9px 10px; border-radius: 10px; background: #0d1628; font-size: .78rem; }
    .zone span:not(:first-child) { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; text-align: right; }
    .foot { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    details { color: var(--muted); font-size: .8rem; line-height: 1.55; }
    summary { color: var(--ink); cursor: pointer; font-weight: 700; }
    .error { display: none; margin-bottom: 10px; border: 1px solid #ff8d8560; background: #3a1f2a; color: #ffd7d3; padding: 10px 12px; border-radius: 10px; }
    @media (max-width: 920px) { .metrics { grid-template-columns: repeat(3, 1fr); } .layout { grid-template-columns: 1fr; } }
    @media (max-width: 560px) {
      main { padding: 15px 12px 28px; } header { display: block; } .status { margin-top: 13px; }
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } .card:last-child { grid-column: 1 / -1; }
      .chart-head { align-items: flex-start; flex-direction: column; } canvas { height: 280px; }
      .foot { grid-template-columns: 1fr; } .panel { padding: 13px; }
    }
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <div class="eyebrow">OANDA v20 Practice · private-host monitor</div>
      <h1>XAUUSD Live Context</h1>
      <p>Observed OHLC context with explicit source limits. Refreshes every 5 seconds.</p>
    </div>
    <div id="status" class="status" aria-live="polite"><span class="dot"></span><span id="statusText">Connecting</span></div>
  </header>
  <div id="error" class="error" role="alert"></div>

  <section class="metrics" aria-label="Live source summary">
    <article class="card"><div class="label">Latest mid</div><div id="latest" class="value">—</div><div id="latestTs" class="sub">Waiting for source</div></article>
    <article class="card"><div class="label">M5 range</div><div id="range" class="value">—</div><div class="sub">Price units</div></article>
    <article class="card"><div class="label">Close spread proxy</div><div id="spread" class="value">—</div><div class="sub">Latest M5 bid/ask close</div></article>
    <article class="card"><div class="label">Nearest session level</div><div id="nearest" class="value">—</div><div id="nearestMeta" class="sub">Latest market date</div></article>
    <article class="card"><div class="label">Operator mode</div><div id="operator" class="value">—</div><div class="sub">Monitor-only</div></article>
  </section>

  <section class="layout">
    <article class="panel">
      <div class="chart-head">
        <div><h2>OANDA midpoint candles</h2><p id="chartMeta">Last 60 returned candles</p></div>
        <div class="tabs" aria-label="Timeframe">
          <button data-tf="M5" aria-pressed="true">M5</button>
          <button data-tf="M15" aria-pressed="false">M15</button>
          <button data-tf="H1" aria-pressed="false">H1</button>
        </div>
      </div>
      <canvas id="chart" aria-label="XAUUSD candlestick chart"></canvas>
    </article>

    <aside class="panel stack" aria-label="Mission Control questions">
      <div class="question"><div class="label">DID / Past</div><strong id="pastState">—</strong><p id="pastText">Waiting for source</p></div>
      <div class="question"><div class="label">DOING / Now</div><strong id="nowState">—</strong><p id="nowText">Waiting for source</p></div>
      <div class="question"><div class="label">NEXT / Conditional</div><strong id="nextState">—</strong><p id="nextText">Waiting for source</p></div>
      <div class="question"><div class="label">MM Mission</div><strong id="missionState">—</strong><p id="missionText">OHLC evidence check pending</p></div>
      <div class="question"><div class="label">INV / Release</div><strong id="inventoryState">—</strong><p id="inventoryText">OHLC evidence check pending</p></div>
    </aside>
  </section>

  <section class="foot">
    <article class="panel"><h2>KEY Zones · UTC session ranges</h2><div id="zones" class="zones"><p>Waiting for source</p></div></article>
    <article class="panel">
      <h2>Confidence / Risk</h2>
      <div class="stack">
        <div class="question"><div class="label">Source coverage</div><strong>1 broker source family</strong><p>OANDA Practice candles only. Event context is not configured in this mode.</p></div>
        <details><summary>Source and methodology</summary><p id="method">Token stays in the local process. The browser receives OANDA candle fields and derived factual session ranges only. Price count is not centralized traded volume. MM mission and dealer inventory are not inferred from OHLC alone.</p></details>
      </div>
    </article>
  </section>
</main>
<script>
(() => {
  "use strict";
  const REFRESH_MS = 5000;
  const DISPLAY_CANDLES = 60;
  let snapshot = null;
  let selectedTf = "M5";
  const el = id => document.getElementById(id);
  const fmt = value => Number.isFinite(Number(value)) ? Number(value).toFixed(3) : "—";
  const clock = value => value ? new Date(value).toLocaleString([], {hour12: false}) : "—";

  function factText(fact) {
    if (!fact) return "No complete candle available.";
    return `O ${fmt(fact.open)} · H ${fmt(fact.high)} · L ${fmt(fact.low)} · C ${fmt(fact.close)} · change ${Number(fact.change_price_units).toFixed(3)}`;
  }

  function setStatus(state) {
    const node = el("status");
    node.className = `status ${state.toLowerCase()}`;
    el("statusText").textContent = state;
  }

  function renderCards(data) {
    const context = data.context;
    const now = context.now.fact;
    const nearest = context.next.nearest_session_level;
    el("latest").textContent = fmt(now.close);
    el("latestTs").textContent = `${now.complete ? "Complete" : "Forming"} · ${clock(now.ts_utc)}`;
    el("range").textContent = fmt(now.range_price_units);
    el("spread").textContent = Number(context.source_risk.latest_close_spread_proxy).toFixed(3);
    el("nearest").textContent = nearest ? fmt(nearest.price) : "Unavailable";
    el("nearestMeta").textContent = nearest ? `${nearest.session} ${nearest.level} · gap ${fmt(nearest.distance_price_units)}` : context.key_zones.session_date_utc;
    el("operator").textContent = context.operator_mode;

    el("pastState").textContent = context.past.state;
    el("pastText").textContent = `${factText(context.past.fact)} ${context.past.note}`;
    el("nowState").textContent = context.now.state;
    el("nowText").textContent = `${factText(context.now.fact)} ${context.now.note}`;
    el("nextState").textContent = context.next.state;
    el("nextText").textContent = context.next.condition;
    el("missionState").textContent = context.mission.state;
    el("missionText").textContent = context.mission.reason;
    el("inventoryState").textContent = context.inventory_release.state;
    el("inventoryText").textContent = context.inventory_release.reason;

    const zoneRoot = el("zones");
    zoneRoot.replaceChildren();
    if (!context.key_zones.sessions.length) {
      const note = document.createElement("p"); note.textContent = "No named session range is available for the latest market date."; zoneRoot.append(note);
    } else {
      context.key_zones.sessions.forEach(zone => {
        const row = document.createElement("div"); row.className = "zone";
        [zone.session, `H ${fmt(zone.high)}`, `L ${fmt(zone.low)}`].forEach(text => { const span = document.createElement("span"); span.textContent = text; row.append(span); });
        zoneRoot.append(row);
      });
    }
  }

  function drawChart() {
    if (!snapshot) return;
    const canvas = el("chart");
    const rect = canvas.getBoundingClientRect();
    const scale = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.floor(rect.width * scale));
    canvas.height = Math.max(1, Math.floor(rect.height * scale));
    const ctx = canvas.getContext("2d");
    ctx.scale(scale, scale);
    const width = rect.width, height = rect.height;
    ctx.clearRect(0, 0, width, height);
    const candles = snapshot.timeframes[selectedTf].candles.slice(-DISPLAY_CANDLES);
    const highs = candles.map(c => Number(c.mid.high));
    const lows = candles.map(c => Number(c.mid.low));
    const max = Math.max(...highs), min = Math.min(...lows), span = Math.max(max - min, 0.001);
    const pad = {left: 10, right: 62, top: 16, bottom: 28};
    const plotW = width - pad.left - pad.right, plotH = height - pad.top - pad.bottom;
    const y = price => pad.top + (max - price) / span * plotH;
    ctx.font = "11px ui-monospace, Consolas, monospace";
    ctx.strokeStyle = "#28344d"; ctx.fillStyle = "#91a0b8"; ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const price = max - span * i / 4, yy = y(price);
      ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(width - pad.right, yy); ctx.stroke();
      ctx.fillText(price.toFixed(2), width - pad.right + 8, yy + 4);
    }
    const slot = plotW / candles.length, bodyW = Math.max(1.5, Math.min(8, slot * .62));
    candles.forEach((candle, index) => {
      const x = pad.left + slot * index + slot / 2;
      const open = Number(candle.mid.open), close = Number(candle.mid.close), high = Number(candle.mid.high), low = Number(candle.mid.low);
      const color = close >= open ? "#5d83ff" : "#e4a84b";
      ctx.strokeStyle = color; ctx.fillStyle = color;
      ctx.beginPath(); ctx.moveTo(x, y(high)); ctx.lineTo(x, y(low)); ctx.stroke();
      const top = Math.min(y(open), y(close)), bodyH = Math.max(1.5, Math.abs(y(open) - y(close)));
      if (candle.complete) ctx.fillRect(x - bodyW / 2, top, bodyW, bodyH);
      else { ctx.lineWidth = 1.5; ctx.strokeRect(x - bodyW / 2, top, bodyW, bodyH); ctx.lineWidth = 1; }
    });
    const first = candles[0], last = candles[candles.length - 1];
    ctx.fillStyle = "#91a0b8";
    ctx.fillText(new Date(first.ts_utc).toLocaleString([], {month:"short", day:"2-digit", hour:"2-digit", minute:"2-digit"}), pad.left, height - 8);
    const lastLabel = new Date(last.ts_utc).toLocaleString([], {month:"short", day:"2-digit", hour:"2-digit", minute:"2-digit"});
    const labelW = ctx.measureText(lastLabel).width;
    ctx.fillText(lastLabel, Math.max(pad.left, width - pad.right - labelW), height - 8);
    el("chartMeta").textContent = `${selectedTf} · ${candles.length} returned candles · open body marks forming candle`;
  }

  async function refresh() {
    try {
      const response = await fetch("/api/xau/live", {cache: "no-store"});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail?.message || "Live source unavailable");
      snapshot = payload;
      setStatus(payload.status);
      el("error").style.display = "none";
      renderCards(payload); drawChart();
    } catch (error) {
      setStatus(snapshot ? "STALE" : "UNAVAILABLE");
      el("error").textContent = error instanceof Error ? error.message : "Live source unavailable";
      el("error").style.display = "block";
    }
  }

  document.querySelectorAll("button[data-tf]").forEach(button => button.addEventListener("click", () => {
    selectedTf = button.dataset.tf;
    document.querySelectorAll("button[data-tf]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    drawChart();
  }));
  window.addEventListener("resize", drawChart);
  refresh(); setInterval(refresh, REFRESH_MS);
})();
</script>
</body>
</html>
"""
    assert_clean_language(document)
    return document
