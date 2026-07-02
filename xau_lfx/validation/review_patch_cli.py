from __future__ import annotations

import argparse
import json
from typing import Sequence

from xau_lfx.validation.review_patch import apply_review_patch, write_updated_case_index


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply an offline monitor-only reviewer notes patch to a v9 case index.")
    parser.add_argument("--case-index", required=True)
    parser.add_argument("--patch-file", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    try:
        result = apply_review_patch(args.case_index, args.patch_file)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "ERROR",
            "case_index_path": args.case_index,
            "patch_path": args.patch_file,
            "errors": [str(exc)],
            "updated_count": 0,
            "cases": [],
            "monitor_only": True,
        }
    report_paths = write_updated_case_index(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
