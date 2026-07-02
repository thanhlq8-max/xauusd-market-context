from __future__ import annotations

import argparse
import json
from typing import Sequence

from xau_lfx.connectors.lifecycle_candidates import build_lifecycle_candidates, write_lifecycle_candidates


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build monitor-only lifecycle candidate artifacts from a rolling dataset.")
    parser.add_argument("--dataset-csv", required=True)
    parser.add_argument("--quality-json", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    try:
        result = build_lifecycle_candidates(dataset_csv=args.dataset_csv, quality_json=args.quality_json)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "ERROR",
            "dataset_csv": args.dataset_csv,
            "quality_json": args.quality_json,
            "errors": [str(exc)],
            "warnings": [],
            "candidate_count": 0,
            "candidates": [],
            "monitor_only": True,
            "dataset_mutated": False,
            "lifecycle_field_overwrite": "NO",
        }
    report_paths = write_lifecycle_candidates(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
