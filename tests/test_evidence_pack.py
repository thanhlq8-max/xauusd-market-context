import json
from pathlib import Path

from xau_lfx.validation.case_index import build_case_index, write_case_index
from xau_lfx.validation.case_library import build_case_library_from_replay, write_case_library
from xau_lfx.validation.evidence_pack import build_evidence_pack, write_evidence_pack


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"


def _case_index_json(tmp_path: Path) -> Path:
    case_library = build_case_library_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)
    library_paths = write_case_library(case_library, tmp_path / "library")
    index = build_case_index(library_paths["json"])
    index_paths = write_case_index(index, tmp_path / "index")
    return Path(index_paths["json"])


def test_evidence_pack_builds_from_case_index(tmp_path):
    case_index_path = _case_index_json(tmp_path)

    result = build_evidence_pack(case_index_path)

    assert result["status"] == "OK"
    assert result["case_count"] == 2
    assert result["group_count"] >= 1
    assert result["monitor_only"] is True
    assert "ACCEPTED" in result["groups"]
    assert result["groups"]["ACCEPTED"]["case_count"] == 2


def test_evidence_pack_groups_review_statuses(tmp_path):
    case_index_path = _case_index_json(tmp_path)
    payload = json.loads(case_index_path.read_text(encoding="utf-8"))
    payload["cases"][0]["review_status"] = "NEEDS_DATA"
    payload["cases"][0]["review_priority"] = "HIGH"
    payload["cases"][1]["review_status"] = "REJECTED"
    case_index_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_evidence_pack(case_index_path)

    assert result["groups"]["NEEDS_DATA"]["case_count"] == 1
    assert result["groups"]["REJECTED"]["case_count"] == 1
    assert any(item["target_group"] == "NEEDS_DATA" and item["required"] for item in result["review_checklist"])


def test_evidence_pack_rejects_non_monitor_payload(tmp_path):
    path = tmp_path / "bad_index.json"
    path.write_text(json.dumps({"monitor_only": False, "cases": []}), encoding="utf-8")

    result = build_evidence_pack(path)

    assert result["status"] == "ERROR"
    assert result["monitor_only"] is True
    assert any("monitor_only=true" in error for error in result["errors"])


def test_evidence_pack_writes_json_and_markdown(tmp_path):
    case_index_path = _case_index_json(tmp_path)
    result = build_evidence_pack(case_index_path)
    paths = write_evidence_pack(result, tmp_path / "pack")

    json_path = Path(paths["json"])
    md_path = Path(paths["markdown"])
    assert json_path.exists()
    assert md_path.exists()
    text = md_path.read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in text
    assert "## ACCEPTED" in text
