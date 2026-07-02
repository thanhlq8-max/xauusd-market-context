from __future__ import annotations

import argparse
import json
from typing import Sequence

from xau_lfx.connectors.snapshot_event_mapper import build_event_log_draft_from_snapshot, write_event_log_draft


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Map a validated OHLCV snapshot into draft monitor-only event-log rows.")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    try:
        result = build_event_log_draft_from_snapshot(args.snapshot, args.validation)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "ERROR",
            "snapshot_path": args.snapshot,
            "validation_path": args.validation,
            "errors": [str(exc)],
            "warnings": [],
            "rows": [],
            "monitor_only": True,
        }
    report_paths = write_event_log_draft(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
