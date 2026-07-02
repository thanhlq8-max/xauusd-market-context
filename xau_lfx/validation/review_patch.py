from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from xau_lfx.validation.case_index import VALID_REVIEW_STATUSES, build_case_index, write_case_index

PATCH_REQUIRED_KEYS = {"case_id"}
PATCH_ALLOWED_KEYS = {"case_id", "review_status", "reviewer_notes"}


def _load_json(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    return payload


def _patch_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("patches")
    if not isinstance(rows, list):
        raise ValueError("patch payload must contain a patches list")
    valid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"patch {index}: patch row must be an object")
        valid_rows.append(row)
    return valid_rows


def _validate_patch(row: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    missing = sorted(PATCH_REQUIRED_KEYS - set(row))
    if missing:
        errors.append(f"patch {index}: missing keys: {', '.join(missing)}")
    extra = sorted(set(row) - PATCH_ALLOWED_KEYS)
    if extra:
        errors.append(f"patch {index}: unsupported keys: {', '.join(extra)}")
    if "review_status" in row:
        status = str(row.get("review_status") or "").upper().strip()
        if status not in VALID_REVIEW_STATUSES:
            errors.append(f"patch {index}: unsupported review_status: {row.get('review_status')}")
    if "reviewer_notes" in row and not isinstance(row.get("reviewer_notes"), str):
        errors.append(f"patch {index}: reviewer_notes must be a string")
    return errors


def apply_review_patch(case_index_path: str | Path, patch_path: str | Path) -> dict[str, Any]:
    """Apply controlled review-status/reviewer-note patches to a case index."""

    case_index = build_case_index(case_index_path)
    if case_index.get("status") == "ERROR":
        return {
            "status": "ERROR",
            "case_index_path": str(case_index_path),
            "patch_path": str(patch_path),
            "errors": ["case index must pass validation before patching"],
            "updated_count": 0,
            "cases": [],
            "monitor_only": True,
        }

    patch_payload = _load_json(patch_path)
    patch_rows = _patch_rows(patch_payload)
    errors: list[str] = []
    for index, row in enumerate(patch_rows, start=1):
        errors.extend(_validate_patch(row, index))
    if errors:
        return {
            "status": "ERROR",
            "case_index_path": str(case_index_path),
            "patch_path": str(patch_path),
            "errors": errors,
            "updated_count": 0,
            "cases": list(case_index.get("cases", [])),
            "monitor_only": True,
        }

    patched = copy.deepcopy(case_index)
    cases = patched.get("cases", [])
    by_case_id = {str(case.get("case_id")): case for case in cases if isinstance(case, dict)}
    updated_count = 0
    for row in patch_rows:
        case_id = str(row.get("case_id"))
        case = by_case_id.get(case_id)
        if case is None:
            errors.append(f"case not found: {case_id}")
            continue
        if "review_status" in row:
            case["review_status"] = str(row["review_status"]).upper().strip()
        if "reviewer_notes" in row:
            case["reviewer_notes"] = row["reviewer_notes"]
        case["monitor_only"] = True
        updated_count += 1

    if errors:
        return {
            "status": "ERROR",
            "case_index_path": str(case_index_path),
            "patch_path": str(patch_path),
            "errors": errors,
            "updated_count": 0,
            "cases": list(case_index.get("cases", [])),
            "monitor_only": True,
        }

    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    for case in cases:
        status = str(case.get("review_status") or "UNKNOWN")
        priority = str(case.get("review_priority") or "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    return {
        "status": "OK",
        "case_index_path": str(case_index_path),
        "patch_path": str(patch_path),
        "case_count": len(cases),
        "updated_count": updated_count,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "cases": cases,
        "monitor_only": True,
    }


def write_updated_case_index(result: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    normalized = {
        "status": result.get("status"),
        "path": result.get("case_index_path"),
        "case_count": result.get("case_count", len(result.get("cases", []))),
        "status_counts": result.get("status_counts", {}),
        "priority_counts": result.get("priority_counts", {}),
        "errors": result.get("errors", []),
        "cases": result.get("cases", []),
        "monitor_only": True,
    }
    paths = write_case_index(normalized, out_dir)
    output_dir = Path(out_dir)
    json_path = output_dir / "updated_case_index.json"
    md_path = output_dir / "updated_case_index.md"
    Path(paths["json"]).rename(json_path)
    Path(paths["markdown"]).rename(md_path)
    return {"json": str(json_path), "markdown": str(md_path)}
