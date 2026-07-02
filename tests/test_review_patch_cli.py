import json
import subprocess
import sys
from pathlib import Path

from xau_lfx.validation.case_index import build_case_index, write_case_index
from xau_lfx.validation.case_library import build_case_library_from_replay, write_case_library


ROOT = Path(__file__).resolve().parents[1]
REPLAY_TEMPLATE = ROOT / "data" / "events" / "event_replay_template.csv"
PATCH_TEMPLATE = ROOT / "data" / "events" / "reviewer_notes_patch_template.json"


def _case_index_json(tmp_path: Path) -> Path:
    case_library = build_case_library_from_replay(REPLAY_TEMPLATE, cluster_band=1.0)
    library_paths = write_case_library(case_library, tmp_path / "library")
    index = build_case_index(library_paths["json"])
    index_paths = write_case_index(index, tmp_path / "index")
    return Path(index_paths["json"])


def test_review_patch_cli_writes_updated_index(tmp_path):
    case_index_path = _case_index_json(tmp_path / "source")
    out_dir = tmp_path / "updated"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.validation.review_patch_cli",
            "--case-index",
            str(case_index_path),
            "--patch-file",
            str(PATCH_TEMPLATE),
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
    assert payload["updated_count"] == 1
    assert Path(payload["report_paths"]["json"]).name == "updated_case_index.json"
    assert Path(payload["report_paths"]["markdown"]).exists()


def test_review_patch_cli_returns_nonzero_for_invalid_patch_json(tmp_path):
    case_index_path = _case_index_json(tmp_path / "source")
    bad_patch = tmp_path / "bad_patch.json"
    bad_patch.write_text("not-json", encoding="utf-8")
    out_dir = tmp_path / "updated"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "xau_lfx.validation.review_patch_cli",
            "--case-index",
            str(case_index_path),
            "--patch-file",
            str(bad_patch),
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
