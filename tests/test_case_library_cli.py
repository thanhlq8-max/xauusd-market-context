import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"
EVENT_TEMPLATE = ROOT / "data" / "events" / "event_log_template.csv"


def test_case_library_cli_writes_seed_outputs(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.validation.case_library_cli",
            "--event-log",
            str(REPLAY_TEMPLATE),
            "--out-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] in {"OK", "WARN"}
    assert payload["monitor_only"] is True
    assert Path(payload["report_paths"]["json"]).exists()
    assert Path(payload["report_paths"]["markdown"]).exists()
    assert "MONITOR_ONLY: YES" in Path(payload["report_paths"]["markdown"]).read_text(encoding="utf-8")


def test_case_library_cli_returns_nonzero_for_invalid_source(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.validation.case_library_cli",
            "--event-log",
            str(EVENT_TEMPLATE),
            "--out-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "ERROR"
    assert payload["monitor_only"] is True
