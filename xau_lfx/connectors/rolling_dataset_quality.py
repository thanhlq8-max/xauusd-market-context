from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from xau_lfx.validation.event_log import validate_event_log

QUALITY_FIELDS = [
    "broker_source",
    "timeframe",
    "session",
    "lifecycle_state",
    "delivery_state",
    "terminal_state",
    "dashboard_state",
    "trader_mode",
]


class RollingDatasetQualityError(ValueError):
    pass


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _counts(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    values = Counter(str(row.get(field) or "UNKNOWN") for row in rows)
    return dict(sorted(values.items(), key=lambda item: (-item[1], item[0])))


def _placeholder_summary(rows: list[dict[str, str]]) -> dict[str, int]:
    return {
        "no_sweep_rows": sum(1 for row in rows if row.get("lifecycle_state") == "NO_SWEEP"),
        "delivery_none_rows": sum(1 for row in rows if row.get("delivery_state") == "D_NONE"),
        "session_unknown_rows": sum(1 for row in rows if row.get("session") == "UNKNOWN"),
        "snapshot_only_rows": sum(1 for row in rows if row.get("dashboard_state") == "SNAPSHOT_ONLY"),
    }


def build_rolling_dataset_quality_report(path: str | Path, *, allow_warn: bool = True) -> dict[str, Any]:
    """Build a monitor-only coverage summary for a rolling event dataset."""

    validation = validate_event_log(path)
    validation_status = validation.get("status")
    if validation_status == "ERROR" or (validation_status == "WARN" and not allow_warn):
        return {
            "status": "ERROR",
            "path": str(path),
            "row_count": 0,
            "validation": validation,
            "errors": ["rolling dataset validation failed"],
            "warnings": list(validation.get("warnings", [])),
            "monitor_only": True,
        }

    rows = _read_rows(path)
    distributions = {field: _counts(rows, field) for field in QUALITY_FIELDS}
    report_status = "OK" if rows else "WARN"
    warnings = list(validation.get("warnings", []))
    if not rows:
        warnings.append("ROLLING_DATASET_EMPTY")

    return {
        "status": report_status,
        "path": str(path),
        "row_count": len(rows),
        "source_coverage": distributions["broker_source"],
        "timeframe_coverage": distributions["timeframe"],
        "session_distribution": distributions["session"],
        "lifecycle_distribution": distributions["lifecycle_state"],
        "delivery_distribution": distributions["delivery_state"],
        "terminal_distribution": distributions["terminal_state"],
        "dashboard_distribution": distributions["dashboard_state"],
        "trader_mode_distribution": distributions["trader_mode"],
        "placeholder_summary": _placeholder_summary(rows),
        "validation": validation,
        "errors": [],
        "warnings": warnings,
        "monitor_only": True,
        "lifecycle_inference": "NO",
    }


def write_rolling_dataset_quality_report(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "rolling_dataset_quality.json"
    md_path = output_dir / "rolling_dataset_quality.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Rolling Dataset Quality Report",
        "",
        f"STATUS: {result.get('status')}",
        f"ROW_COUNT: {result.get('row_count')}",
        "MONITOR_ONLY: YES",
        f"LIFECYCLE_INFERENCE: {result.get('lifecycle_inference', 'NO')}",
        "",
    ]
    sections = [
        ("Source Coverage", result.get("source_coverage", {})),
        ("Timeframe Coverage", result.get("timeframe_coverage", {})),
        ("Session Distribution", result.get("session_distribution", {})),
        ("Lifecycle Distribution", result.get("lifecycle_distribution", {})),
        ("Delivery Distribution", result.get("delivery_distribution", {})),
        ("Placeholder Summary", result.get("placeholder_summary", {})),
    ]
    for title, values in sections:
        lines.extend([f"## {title}", ""])
        if values:
            lines.extend(f"- {key}: {value}" for key, value in values.items())
        else:
            lines.append("- none: 0")
        lines.append("")
    if result.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result["warnings"])
        lines.append("")
    if result.get("errors"):
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
