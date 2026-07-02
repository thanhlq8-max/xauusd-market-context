from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from xau_lfx.validation.event_log import EXPECTED_COLUMNS, validate_event_log


class RollingEventDatasetError(ValueError):
    pass


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return []
        return [{column: (row.get(column) or "") for column in EXPECTED_COLUMNS} for row in reader]


def _write_rows(path: str | Path, rows: list[dict[str, str]]) -> None:
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in EXPECTED_COLUMNS})


def _row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        str(row.get("event_id") or ""),
        str(row.get("ts_utc") or ""),
        str(row.get("broker_source") or ""),
        str(row.get("timeframe") or ""),
    )


def append_event_log_draft(
    *,
    draft_csv: str | Path,
    dataset_csv: str | Path,
    out_dir: str | Path,
    allow_warn: bool = True,
) -> dict[str, Any]:
    """Append draft event-log rows into a rolling local dataset with duplicate protection."""

    draft_validation = validate_event_log(draft_csv)
    if draft_validation.get("status") == "ERROR" or (draft_validation.get("status") == "WARN" and not allow_warn):
        return {
            "status": "ERROR",
            "draft_csv": str(draft_csv),
            "dataset_csv": str(dataset_csv),
            "errors": ["draft event log validation failed"],
            "warnings": list(draft_validation.get("warnings", [])),
            "draft_validation": draft_validation,
            "existing_count": 0,
            "draft_count": 0,
            "appended_count": 0,
            "skipped_duplicate_count": 0,
            "monitor_only": True,
        }

    existing_rows = _read_rows(dataset_csv)
    draft_rows = _read_rows(draft_csv)
    seen = {_row_key(row) for row in existing_rows}
    output_rows = list(existing_rows)
    appended: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    for row in draft_rows:
        key = _row_key(row)
        if key in seen:
            skipped.append(row)
            continue
        seen.add(key)
        output_rows.append(row)
        appended.append(row)

    output_path = Path(out_dir) / "rolling_event_dataset.csv"
    _write_rows(output_path, output_rows)
    dataset_validation = validate_event_log(output_path)
    status = "ERROR" if dataset_validation.get("status") == "ERROR" else "OK"
    return {
        "status": status,
        "draft_csv": str(draft_csv),
        "dataset_csv": str(dataset_csv),
        "output_csv": str(output_path),
        "existing_count": len(existing_rows),
        "draft_count": len(draft_rows),
        "appended_count": len(appended),
        "skipped_duplicate_count": len(skipped),
        "appended_event_ids": [row.get("event_id", "") for row in appended],
        "skipped_duplicate_event_ids": [row.get("event_id", "") for row in skipped],
        "draft_validation": draft_validation,
        "dataset_validation": dataset_validation,
        "errors": list(dataset_validation.get("errors", [])),
        "warnings": list(dataset_validation.get("warnings", [])),
        "monitor_only": True,
    }


def write_append_report(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "rolling_event_append_report.json"
    md_path = output_dir / "rolling_event_append_report.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Rolling Event Dataset Append Report",
        "",
        f"STATUS: {result.get('status')}",
        f"EXISTING_COUNT: {result.get('existing_count')}",
        f"DRAFT_COUNT: {result.get('draft_count')}",
        f"APPENDED_COUNT: {result.get('appended_count')}",
        f"SKIPPED_DUPLICATE_COUNT: {result.get('skipped_duplicate_count')}",
        f"OUTPUT_CSV: {result.get('output_csv')}",
        "MONITOR_ONLY: YES",
        "",
    ]
    if result.get("appended_event_ids"):
        lines.extend(["## Appended Event IDs", ""])
        lines.extend(f"- {event_id}" for event_id in result["appended_event_ids"])
        lines.append("")
    if result.get("skipped_duplicate_event_ids"):
        lines.extend(["## Skipped Duplicate Event IDs", ""])
        lines.extend(f"- {event_id}" for event_id in result["skipped_duplicate_event_ids"])
        lines.append("")
    if result.get("warnings"):
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result["warnings"])
        lines.append("")
    if result.get("errors"):
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "csv": str(result.get("output_csv"))}
