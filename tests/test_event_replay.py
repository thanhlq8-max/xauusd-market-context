from pathlib import Path

from xau_lfx.validation.event_replay import replay_event_log, write_replay_report


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"


def test_committed_replay_template_matches_compact_lifecycle():
    result = replay_event_log(TEMPLATE)

    assert result["status"] in {"OK", "WARN"}
    assert result["rows_checked"] == 2
    assert result["matches"] == 2
    assert result["mismatches"] == 0
    assert result["monitor_only"] is True


def test_replay_harness_rejects_plain_event_log_without_replay_columns():
    result = replay_event_log(ROOT / "data" / "events" / "event_log_template.csv")

    assert result["status"] == "ERROR"
    assert any("missing replay columns" in error for error in result["errors"])


def test_replay_harness_reports_mismatch(tmp_path):
    text = TEMPLATE.read_text(encoding="utf-8")
    mismatch_text = text.replace(",RECLAIM,D_ACTIVE\nreplay-002", ",RECLAIM,D_FAILED\nreplay-002")
    path = tmp_path / "event_replay_mismatch.csv"
    path.write_text(mismatch_text, encoding="utf-8")

    result = replay_event_log(path)

    assert result["status"] == "MISMATCH"
    assert result["matches"] == 1
    assert result["mismatches"] == 1
    first_row = result["results"][0]
    assert first_row["expected_delivery_state"] == "D_FAILED"
    assert first_row["actual_delivery_state"] == "D_ACTIVE"


def test_replay_harness_writes_json_and_markdown_reports(tmp_path):
    result = replay_event_log(TEMPLATE)
    paths = write_replay_report(result, tmp_path)

    json_path = Path(paths["json"])
    md_path = Path(paths["markdown"])
    assert json_path.exists()
    assert md_path.exists()
    assert "MONITOR_ONLY: YES" in md_path.read_text(encoding="utf-8")
