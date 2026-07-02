import json
from pathlib import Path

from xau_lfx.validation.case_index import build_case_index, write_case_index
from xau_lfx.validation.case_library import build_case_library_from_replay, write_case_library
from xau_lfx.validation.review_patch import apply_review_patch, write_updated_case_index


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"
PATCH_TEMPLATE = ROOT / "data" / "events" / "reviewer_notes_patch_template.json"


def _case_index_json(tmp_path: Path) -> Path:
    case_library = build_case_library_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)
    library_paths = write_case_library(case_library, tmp_path / "library")
    index = build_case_index(library_paths["json"])
    index_paths = write_case_index(index, tmp_path / "index")
    return Path(index_paths["json"])


def test_apply_review_patch_updates_status_and_notes(tmp_path):
    case_index_path = _case_index_json(tmp_path)

    result = apply_review_patch(case_index_path, PATCH_TEMPLATE)

    assert result["status"] == "OK"
    assert result["updated_count"] == 1
    first = result["cases"][0]
    assert first["case_id"] == "CASE:replay-001"
    assert first["review_status"] == "NEEDS_DATA"
    assert "screenshot" in first["reviewer_notes"]
    assert first["monitor_only"] is True


def test_apply_review_patch_rejects_invalid_status(tmp_path):
    case_index_path = _case_index_json(tmp_path)
    patch_path = tmp_path / "bad_patch.json"
    patch_path.write_text(
        json.dumps({"patches": [{"case_id": "CASE:replay-001", "review_status": "DONE"}]}),
        encoding="utf-8",
    )

    result = apply_review_patch(case_index_path, patch_path)

    assert result["status"] == "ERROR"
    assert any("unsupported review_status" in error for error in result["errors"])
    assert result["updated_count"] == 0


def test_apply_review_patch_rejects_unknown_case(tmp_path):
    case_index_path = _case_index_json(tmp_path)
    patch_path = tmp_path / "unknown_case_patch.json"
    patch_path.write_text(
        json.dumps({"patches": [{"case_id": "CASE:missing", "review_status": "REJECTED"}]}),
        encoding="utf-8",
    )

    result = apply_review_patch(case_index_path, patch_path)

    assert result["status"] == "ERROR"
    assert any("case not found" in error for error in result["errors"])


def test_apply_review_patch_rejects_unsupported_key(tmp_path):
    case_index_path = _case_index_json(tmp_path)
    patch_path = tmp_path / "bad_key_patch.json"
    patch_path.write_text(
        json.dumps({"patches": [{"case_id": "CASE:replay-001", "trade_signal": "BUY"}]}),
        encoding="utf-8",
    )

    result = apply_review_patch(case_index_path, patch_path)

    assert result["status"] == "ERROR"
    assert any("unsupported keys" in error for error in result["errors"])


def test_write_updated_case_index_outputs_expected_names(tmp_path):
    case_index_path = _case_index_json(tmp_path)
    result = apply_review_patch(case_index_path, PATCH_TEMPLATE)
    paths = write_updated_case_index(result, tmp_path / "updated")

    json_path = Path(paths["json"])
    md_path = Path(paths["markdown"])
    assert json_path.name == "updated_case_index.json"
    assert md_path.name == "updated_case_index.md"
    assert json_path.exists()
    assert md_path.exists()
    assert "MONITOR_ONLY: YES" in md_path.read_text(encoding="utf-8")
