from __future__ import annotations

import argparse
import json
from typing import Sequence

from xau_lfx.validation.evidence_pack import build_evidence_pack, write_evidence_pack


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an offline monitor-only v9 case review evidence pack.")
    parser.add_argument("--case-index", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    try:
        result = build_evidence_pack(args.case_index)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "status": "ERROR",
            "path": args.case_index,
            "errors": [str(exc)],
            "group_count": 0,
            "case_count": 0,
            "groups": {},
            "review_checklist": [],
            "monitor_only": True,
        }
    report_paths = write_evidence_pack(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
