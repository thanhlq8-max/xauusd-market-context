from __future__ import annotations

import argparse
import json
from typing import Sequence

from xau_lfx.connectors.rolling_event_dataset import append_event_log_draft, write_append_report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append draft event-log rows into a rolling monitor-only dataset.")
    parser.add_argument("--draft-csv", required=True)
    parser.add_argument("--dataset-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--reject-warn", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = append_event_log_draft(
            draft_csv=args.draft_csv,
            dataset_csv=args.dataset_csv,
            out_dir=args.out_dir,
            allow_warn=not args.reject_warn,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "ERROR",
            "draft_csv": args.draft_csv,
            "dataset_csv": args.dataset_csv,
            "errors": [str(exc)],
            "warnings": [],
            "existing_count": 0,
            "draft_count": 0,
            "appended_count": 0,
            "skipped_duplicate_count": 0,
            "monitor_only": True,
        }
    report_paths = write_append_report(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
