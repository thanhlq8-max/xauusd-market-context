from __future__ import annotations

import argparse
import json
from typing import Sequence

from xau_lfx.validation.case_library import build_case_library_from_replay, write_case_library


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build an offline monitor-only v9 case-library seed from a replay event log."
    )
    parser.add_argument("--event-log", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--cluster-band", type=float, default=1.0)
    args = parser.parse_args(argv)

    result = build_case_library_from_replay(args.event_log, cluster_band=args.cluster_band)
    report_paths = write_case_library(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
