# Repo Cleanup Audit — v9 Foundation

STATUS: NON_DESTRUCTIVE_CLEANUP_PLAN
RUNTIME_CHANGE: NO

---

## 1. Current repo observation

The repository already has a useful foundation:

- Python package metadata and CLI entry points.
- Existing tests and GitHub Actions.
- Existing documentation and adoption resources.
- Existing sample data and generated sample artifacts.
- OANDA Practice dashboard path.
- Artifact contract and schema validation path.

This means the correct cleanup is **not** a destructive rewrite.

---

## 2. Cleanup decision

For this branch:

```text
Do not delete.
Do not move current runtime modules.
Do not rename the package.
Do not import Pine source.
Do not change behavior.
```

Instead:

```text
Add governance + roadmap + schema + directory boundaries.
```

---

## 3. What was cleaned/prepared

| Area | Action | Runtime impact |
|---|---|---:|
| Project state | Added root `PROJECT_STATE.md` | None |
| v9 roadmap | Added `docs/V9_DESK_LIKE_HYBRID_STACK_ROADMAP.md` | None |
| Repo structure | Added `docs/REPO_STRUCTURE_TARGET_v9.md` | None |
| Event schema | Added `docs/EVENT_DATASET_SCHEMA_V9.md` | None |
| Ignore rules | Expanded `.gitignore` for local data/research artifacts | None |
| Placeholder dirs | Added README files for future `data/`, `pine/`, `research/`, `bridges/` | None |
| README | Added v9 transition navigation | None |
| Changelog | Added unreleased cleanup note | None |

---

## 4. Deferred cleanup

The following actions are deferred because they can break behavior or require exact path review:

- moving `xau_lfx/*` modules;
- deleting existing docs;
- deleting examples or sample artifacts;
- changing package name from `xau-lfx-external-data-foundation`;
- changing CLI commands `xau-lfx` / `xau-lfx-api`;
- changing workflow steps;
- adding Pine source;
- adding alert bridges.

---

## 5. Future deletion/move gate

Before any destructive cleanup PR, create a table:

| Old path | Proposed action | Reason | Compatibility impact | Test required |
|---|---|---|---|---|

No path should be deleted or moved unless the table is complete.

---

## 6. Safety checks for future contributors

- Generated artifacts stay out of root.
- Raw/private data stays under ignored `data/raw/`, `data/processed/`, or `data/private/`.
- Credentials stay in environment variables only.
- Public docs must not claim profitability or actual MM inventory.
- Pine source must not be copied into the repo unless license/publication and version-lock policy are explicit.
- Alert bridge must stay monitor-only until a separate execution-spec exists.

---

## 7. Next PR candidates

Recommended next PR order:

1. `v9.0-B`: add event-log template and validator.
2. `v9.0-C`: add compact lifecycle module tests.
3. `v9.0-D`: add liquidity node graph schema.
4. `v9.0-E`: add research dashboard reading event logs.
5. `v9.0-F`: add monitor-only webhook payload schema.
