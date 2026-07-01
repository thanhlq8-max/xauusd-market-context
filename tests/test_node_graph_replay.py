from pathlib import Path

from xau_lfx.validation.node_graph_replay import build_node_graph_from_replay, write_node_graph_report


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"
EVENT_TEMPLATE = ROOT / "data" / "events" / "event_log_template.csv"


def test_node_graph_report_builds_from_replay_template():
    result = build_node_graph_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)

    assert result["status"] in {"OK", "WARN"}
    assert result["replay_status"] in {"OK", "WARN"}
    assert result["rows_checked"] == 2
    assert result["node_count"] == 1
    assert result["cluster_count"] == 1
    assert result["monitor_only"] is True
    node = result["nodes"][0]
    assert node["source"] == "PDL"
    assert node["reclaim_count"] == 2
    assert node["monitor_only"] is True


def test_node_graph_report_rejects_plain_event_log_without_replay_columns():
    result = build_node_graph_from_replay(EVENT_TEMPLATE, cluster_band=1.0)

    assert result["status"] == "ERROR"
    assert result["replay_status"] == "ERROR"
    assert any("event replay must pass" in error for error in result["errors"])


def test_node_graph_report_rejects_replay_mismatch(tmp_path):
    text = REPLAY_TEMPLATE.read_text(encoding="utf-8")
    mismatch_text = text.replace(",RECLAIM,D_ACTIVE\nreplay-002", ",RECLAIM,D_FAILED\nreplay-002")
    path = tmp_path / "node_graph_mismatch.csv"
    path.write_text(mismatch_text, encoding="utf-8")

    result = build_node_graph_from_replay(path, cluster_band=1.0)

    assert result["status"] == "ERROR"
    assert result["replay_status"] == "MISMATCH"


def test_node_graph_report_writes_json_and_markdown(tmp_path):
    result = build_node_graph_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)
    paths = write_node_graph_report(result, tmp_path)

    json_path = Path(paths["json"])
    md_path = Path(paths["markdown"])
    assert json_path.exists()
    assert md_path.exists()
    text = md_path.read_text(encoding="utf-8")
    assert "MONITOR_ONLY: YES" in text
    assert "PDL:DN:99.500" in text
