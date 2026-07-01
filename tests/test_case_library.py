from pathlib import Path

from xau_lfx.validation.case_library import build_case_library_from_replay, write_case_library


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"
EVENT_TEMPLATE = ROOT / "data" / "events" / "event_log_template.csv"


def test_case_library_builds_from_replay_template():
    result = build_case_library_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)

    assert result["status"] in {"OK", "WARN"}
    assert result["node_graph_status"] in {"OK", "WARN"}
    assert result["case_count"] == 2
    assert result["monitor_only"] is True
    first = result["cases"][0]
    assert first["case_id"] == "CASE:replay-001"
    assert first["source"] == "PDL"
    assert first["node_id"] == "PDL:DN:99.500"
    assert first["node_reaction"] == "RECLAIM"
    assert first["monitor_only"] is True


def test_case_library_rejects_plain_event_log():
    result = build_case_library_from_replay(EVENT_TEMPLATE, cluster_band=1.0)

    assert result["status"] == "ERROR"
    assert result["case_count"] if "case_count" in result else 0 == 0
    assert any("node graph report must pass" in error for error in result["errors"])


def test_case_library_marks_mismatch_source_as_error(tmp_path):
    text = REPLAY_TEMPLATE.read_text(encoding="utf-8")
    mismatch_text = text.replace(",RECLAIM,D_ACTIVE\nreplay-002", ",RECLAIM,D_FAILED\nreplay-002")
    path = tmp_path / "case_library_mismatch.csv"
    path.write_text(mismatch_text, encoding="utf-8")

    result = build_case_library_from_replay(path, cluster_band=1.0)

    assert result["status"] == "ERROR"
    assert result["cases"] == []


def test_case_library_writes_json_and_markdown(tmp_path):
    result = build_case_library_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)
    paths = write_case_library(result, tmp_path)

    json_path = Path(paths["json"])
    md_path = Path(paths["markdown"])
    assert json_path.exists()
    assert md_path.exists()
    text = md_path.read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in text
    assert "CASE:replay-001" in text
