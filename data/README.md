# data/

Local research data boundary for the v9 validation stack.

Rules:

- Do not commit raw broker exports, private logs, account data, or personal financial data.
- Use `examples/sample-data/` for committed synthetic fixtures.
- Use `data/raw/`, `data/processed/`, and `data/private/` locally; these paths are ignored.
- Curated public templates may be committed only after review.
- Generated event logs should follow `docs/EVENT_DATASET_SCHEMA_V9.md`.
