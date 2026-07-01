import json
import subprocess
import sys
from pathlib import Path

from xau_lfx.validation.case_index import build_case_index, write_case_index
from xau_lfx.validation.case_library import build_case_library_from_replay, write_case_library


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"


def _case_index_json(tmp_path: Path) -> Path:
    case_library = build_case_library_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)
    library_paths = write_case_library(case_library, tmp_path / "library")
    index = build_case_index(library_paths["json"])
    index_paths = write_case_index(index, tmp_path / "index")
    return Path(index_paths["json"])


def test_evidence_pack_cli_writes_outputs(tmp_path):
    case_index_path = _case_index_json(tmp_path / "source")
    out_dir = tmp_path / "pack"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.validation.evidence_pack_cli",
            "--case-index",
            str(case_index_path),
            "--out-dir",
            str(out_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "OK"
    assert payload["monitor_only"] is True
    assert Path(payload["report_paths"]["json"]).exists()
    assert Path(payload["report_paths"]["markdown"]).exists()


def test_evidence_pack_cli_returns_nonzero_for_invalid_json(tmp_path):
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("not-json", encoding="utf-8")
    out_dir = tmp_path / "pack"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.validation.evidence_pack_cli",
            "--case-index",
            str(bad_path),
            "--out-dir",
            str(out_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "ERROR"
    assert payload["monitor_only"] is True
