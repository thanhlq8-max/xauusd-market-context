import importlib.util
from pathlib import Path


def _load_release_module():
    path = Path("scripts/check_release_readiness.py")
    spec = importlib.util.spec_from_file_location("check_release_readiness", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_release_readiness_is_ready_after_license_lock():
    module = _load_release_module()
    result = module.check_readiness(".")
    assert result["status"] == "READY"
    assert result["blockers"] == []
    assert result["warnings"] == []
    assert result["license"] == "Apache-2.0"


def test_release_readiness_checks_expected_files():
    module = _load_release_module()
    result = module.check_readiness(".")
    assert result["checked_files"] >= 25
    assert not any("Missing required" in blocker for blocker in result["blockers"])



def _write_minimal_ready_tree(root: Path, module) -> None:
    for rel_path in module.REQUIRED_FILES + module.REQUIRED_SAMPLE_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == "LICENSE":
            path.write_text("Apache License\n", encoding="utf-8")
        elif rel_path == "DATA_LICENSE.md":
            path.write_text("synthetic fixtures\n", encoding="utf-8")
        elif rel_path == "pyproject.toml":
            path.write_text(
                f'version = "{module.EXPECTED_VERSION}"\nlicense = "Apache-2.0"\nlicense-files = ["LICENSE", "NOTICE"]\n',
                encoding="utf-8",
            )
        elif rel_path == "README.md":
            path.write_text(
                "monitor-only local csv artifact quality static demo apache-2.0 use cases\n",
                encoding="utf-8",
            )
        else:
            path.write_text("placeholder\n", encoding="utf-8")

    init_path = root / "xau_lfx" / "__init__.py"
    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text(f'__version__ = "{module.EXPECTED_VERSION}"\n', encoding="utf-8")

    issue_dir = root / ".github" / "ISSUE_TEMPLATE"
    issue_dir.mkdir(parents=True, exist_ok=True)
    for idx in range(3):
        (issue_dir / f"template_{idx}.md").write_text("placeholder\n", encoding="utf-8")


def test_release_readiness_blocks_root_patch_helper_artifacts(tmp_path):
    module = _load_release_module()
    _write_minimal_ready_tree(tmp_path, module)
    (tmp_path / "apply_v2.5.2_repo_hygiene_cleanup.py").write_text("placeholder\n", encoding="utf-8")
    (tmp_path / "xauusd-market-context-v2.5.2-repo-hygiene-cleanup.patch").write_text(
        "placeholder\n", encoding="utf-8"
    )

    result = module.check_readiness(tmp_path)

    assert result["status"] == "BLOCKED"
    assert any("generated patch/apply artifacts" in blocker for blocker in result["blockers"])
