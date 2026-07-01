from __future__ import annotations

import argparse
import json
from typing import Sequence

from xau_lfx.validation.case_index import build_case_index, write_case_index


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an offline monitor-only v9 case review index.")
    parser.add_argument("--case-library", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    try:
        result = build_case_index(args.case_library)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "ERROR",
            "path": args.case_library,
            "errors": [str(exc)],
            "cases": [],
            "monitor_only": True,
        }
    report_paths = write_case_index(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
