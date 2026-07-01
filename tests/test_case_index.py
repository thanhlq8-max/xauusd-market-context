import json
from pathlib import Path

from xau_lfx.validation.case_index import build_case_index, write_case_index
from xau_lfx.validation.case_library import build_case_library_from_replay, write_case_library


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"


def _case_library_json(tmp_path: Path) -> Path:
    result = build_case_library_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)
    paths = write_case_library(result, tmp_path)
    return Path(paths["json"])


def test_case_index_builds_from_case_library_seed(tmp_path):
    case_library_path = _case_library_json(tmp_path)

    result = build_case_index(case_library_path)

    assert result["status"] == "OK"
    assert result["case_count"] == 2
    assert result["monitor_only"] is True
    first = result["cases"][0]
    assert first["case_id"] == "CASE:replay-001"
    assert first["review_status"] == "ACCEPTED"
    assert first["monitor_only"] is True


def test_case_index_supports_explicit_review_status(tmp_path):
    case_library_path = _case_library_json(tmp_path)
    payload = json.loads(case_library_path.read_text(encoding="utf-8"))
    payload["cases"][0]["review_status"] = "NEEDS_DATA"
    payload["cases"][0]["reviewer_notes"] = "needs screenshot confirmation"
    case_library_path.write_text(json.dumps(payload), encoding="utf-8")

    result = build_case_index(case_library_path)

    first = result["cases"][0]
    assert first["review_status"] == "NEEDS_DATA"
    assert first["review_priority"] == "HIGH"
    assert first["reviewer_notes"] == "needs screenshot confirmation"


def test_case_index_rejects_non_monitor_payload(tmp_path):
    path = tmp_path / "bad_case_library.json"
    path.write_text(json.dumps({"monitor_only": False, "cases": []}), encoding="utf-8")

    result = build_case_index(path)

    assert result["status"] == "ERROR"
    assert result["monitor_only"] is True
    assert any("monitor_only=true" in error for error in result["errors"])


def test_case_index_writes_json_and_markdown(tmp_path):
    case_library_path = _case_library_json(tmp_path)
    result = build_case_index(case_library_path)
    paths = write_case_index(result, tmp_path / "index")

    json_path = Path(paths["json"])
    md_path = Path(paths["markdown"])
    assert json_path.exists()
    assert md_path.exists()
    text = md_path.read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in text
    assert "CASE:replay-001" in text
