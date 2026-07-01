# v9.0 Roadmap — Desk-like Hybrid Research Stack

STATUS: ROADMAP_DRAFT
SCOPE: planning and repository preparation
RUNTIME_CHANGE: NO

---

## 1. Positioning

The v9 track should be developed as a **hybrid MM-behavior research and validation stack**, not as a direct trading-signal or auto-execution system.

Correct framing:

```text
Behavior monitoring + event dataset + validation + research dashboard.
```

Incorrect framing:

```text
Guaranteed MM detector, real dealer inventory model, retail positioning source, auto-profitable trading system.
```

---

## 2. Stack layers

| Layer | Component | Purpose | Current action |
|---|---|---|---|
| L1 | TradingView Pine monitor | Chart-side Mission Control | Keep external locked reference for now |
| L2 | Python data engine | Deterministic event extraction and validation | Build after schema lock |
| L3 | Event dataset | Forward-validation ground truth | Define schema first |
| L4 | Research reports | Event study, source quality, session quality | Add notebooks/reports later |
| L5 | Case library | Screenshots + event notes | Add after first validation batch |
| L6 | Alert bridge | Monitor-only operational alerts | Later, no execution |

---

## 3. Version plan

### v9.0-A — Repository foundation

Goal:

- clean repo positioning;
- add `PROJECT_STATE.md`;
- add v9 roadmap;
- add target repo structure;
- add event schema draft;
- preserve existing package behavior.

Acceptance:

- CI passes;
- no runtime package behavior change;
- no Pine source added;
- docs state limitations clearly.

---

### v9.0-B — Event schema and validation log

Goal:

- formalize event records for sweep/reclaim/accept/reject/fail/delivery states;
- add CSV/JSONL templates;
- create manual validation workflow.

Acceptance:

- sample event log validates;
- MFE/MAE/time-to-resolution fields defined;
- source quality and session tags included;
- no edge/profit claim.

---

### v9.0-C — Compact lifecycle engine port

Goal:

- port only the compact v8.1-D lifecycle primitives into Python:
  - normalizer;
  - multi-source sweep detection;
  - sweep lifecycle;
  - absorption confirmation;
  - route lock;
  - delivery health;
  - terminal outcome.

Acceptance:

- unit tests cover each primitive;
- outputs are comparable with logged Pine dashboard states;
- no auto-entry semantics.

---

### v9.0-D — Liquidity node graph outside Pine

Goal:

- rebuild liquidity nodes/cụm thanh khoản outside Pine where memory and compute constraints are lower;
- track node freshness, touches, reactions, failure, and historical outcome quality.

Acceptance:

- node schema defined;
- node scoring is auditable;
- node graph does not claim real orderbook or private flow.

---

### v9.0-E — Research dashboard

Goal:

- show event timeline;
- show source quality by PDH/PDL/NYH/NYL/Asia/round/density;
- show session performance and failure patterns;
- show route health statistics.

Acceptance:

- dashboard reads logged dataset;
- no trading recommendation language;
- all charts are descriptive, not predictive claims.

---

### v9.0-F — Monitor-only alert bridge

Goal:

- emit operational states:
  - `TRACK_RECLAIM`;
  - `TRACK_ACCEPT`;
  - `D_ACTIVE`;
  - `D_STALL`;
  - `D_COUNTERFLOW`;
  - `D_FAILED`;
  - `TARGET_HIT`.

Acceptance:

- no order placement;
- no position sizing;
- no SL/TP logic;
- alert payload has schema tests.

---

## 4. Module boundaries

Future Python modules should be added only after tests and schema contracts exist.

Target package path can remain `xau_lfx` unless a separate package rename decision is made.

Proposed future modules:

```text
xau_lfx/engines/sweep_detector.py
xau_lfx/engines/sweep_lifecycle.py
xau_lfx/engines/absorption.py
xau_lfx/engines/route_lock.py
xau_lfx/engines/delivery_health.py
xau_lfx/engines/liquidity_nodes.py
xau_lfx/validation/event_schema.py
xau_lfx/validation/event_metrics.py
```

---

## 5. Validation priority

Validation should measure dashboard-state correctness, not trading profit first.

Primary metrics:

- event classification accuracy by manual review;
- time-to-resolution;
- target-hit vs route-failed count;
- MFE/MAE after event;
- session/source reliability;
- false-positive and stale-route frequency.

Forbidden metrics until dataset maturity:

- profitability claim;
- win-rate claim as public marketing;
- broker-independent edge claim;
- universal XAUUSD signal claim.

---

## 6. Release rule

Do not release v9 as production until:

- CI passes;
- event schema is stable;
- at least 5–10 forward sessions are logged;
- limitations are documented;
- no secrets or private data are committed;
- README avoids overclaiming.
