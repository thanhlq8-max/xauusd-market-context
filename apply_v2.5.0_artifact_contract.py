from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise RuntimeError(f"Expected text not found in {path}: {old[:120]!r}")
    write(path, text.replace(old, new, 1))


def require_missing(path: str) -> None:
    target = ROOT / path
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite existing file: {path}")


ARTIFACT_CONTRACT_PY = r'''from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from xau_lfx.config import artifact_paths
from xau_lfx.forbidden_language import assert_clean_language


ARTIFACT_CONTRACT_VERSION = "1.0.0"

ARTIFACT_REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "raw_scan": ("ts_utc", "symbol", "monitor_only", "source_payloads"),
    "data_quality": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "freshness_score",
        "coverage_score",
        "schema_score",
        "source_count",
        "confidence_cap",
        "present_timeframes",
        "errors",
        "quality_flags",
    ),
    "composite_ohlcv": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "timeframes",
        "primary_timeframe",
        "bars",
    ),
    "session_context": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "session_state",
        "primary_timeframe",
        "session_ranges",
        "confidence_cap",
        "quality_flags",
    ),
    "macro_pressure": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "pressure_state",
        "drivers",
        "confidence_cap",
        "quality_flags",
    ),
    "event_risk": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "risk_state",
        "event_count",
        "high_impact_events",
        "near_high_impact_events",
        "confidence_cap",
        "quality_flags",
    ),
    "state": ("ts_utc", "symbol", "monitor_only", "state", "summary", "evidence", "quality"),
    "user_insight": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "headline",
        "now_read",
        "operator_focus",
        "evidence_map",
        "useful_limits",
        "upgrade_requirements",
        "quality_flags",
    ),
    "artifact_quality": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "status",
        "quality_score",
        "quality_grade",
        "source_count",
        "warnings",
        "errors",
        "confidence_cap",
    ),
    "context_summary": (
        "ts_utc",
        "symbol",
        "monitor_only",
        "latest_close",
        "spread_state",
        "event_risk_state",
        "quality_status",
        "quality_grade",
        "confidence_cap",
        "confidence_explanation",
        "monitor_focus",
        "limitations",
        "quality_flags",
    ),
}


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name}: invalid JSON at line {exc.lineno} column {exc.colno}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name}: top-level JSON value must be an object")
    return payload


def validate_artifact_contract(artifact_dir: str | Path) -> dict[str, Any]:
    paths = artifact_paths(artifact_dir)
    errors: list[str] = []
    checked_artifacts: list[dict[str, Any]] = []

    for artifact_key, required_keys in ARTIFACT_REQUIRED_KEYS.items():
        path = paths[artifact_key]
        checked = {
            "artifact_key": artifact_key,
            "file": path.name,
            "required_keys": list(required_keys),
            "missing_keys": [],
        }
        checked_artifacts.append(checked)

        if not path.exists():
            errors.append(f"{path.name}: missing artifact")
            continue

        try:
            payload = _read_json_object(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        missing_keys = [key for key in required_keys if key not in payload]
        checked["missing_keys"] = missing_keys
        if missing_keys:
            errors.append(f"{path.name}: missing required keys: {', '.join(missing_keys)}")
        if payload.get("monitor_only") is not True:
            errors.append(f"{path.name}: monitor_only must be true")

    result = {
        "schema_contract_version": ARTIFACT_CONTRACT_VERSION,
        "status": "ERROR" if errors else "OK",
        "artifact_dir": str(Path(artifact_dir)),
        "checked_artifact_count": len(checked_artifacts),
        "checked_artifacts": checked_artifacts,
        "errors": errors,
    }
    assert_clean_language(result)
    return result
'''

ARTIFACT_CONTRACT_DOC = r'''# Artifact Contract

`xau-lfx validate-artifacts` checks generated JSON files against the current public artifact contract.

The command is intended for shared artifact bundles, GitHub Pages demo outputs, and user-submitted validation reports. It checks structure only. It does not score predictive value, infer direction, or validate any market outcome.

## Command

```bash
xau-lfx validate-artifacts --artifact-dir artifacts
```

The command exits with code `1` when a required artifact file is missing, invalid JSON is found, required top-level keys are missing, or a checked artifact does not keep `monitor_only: true`.

## Contract version

```text
1.0.0
```

This version describes the required top-level keys for the current JSON artifact set. It is not yet a full JSON Schema file set.

## Required artifact files and keys

| Artifact | Required top-level keys |
|---|---|
| `xau_raw_scan.json` | `ts_utc`, `symbol`, `monitor_only`, `source_payloads` |
| `xau_data_quality.json` | `ts_utc`, `symbol`, `monitor_only`, `freshness_score`, `coverage_score`, `schema_score`, `source_count`, `confidence_cap`, `present_timeframes`, `errors`, `quality_flags` |
| `xau_composite_ohlcv.json` | `ts_utc`, `symbol`, `monitor_only`, `timeframes`, `primary_timeframe`, `bars` |
| `xau_session_context.json` | `ts_utc`, `symbol`, `monitor_only`, `session_state`, `primary_timeframe`, `session_ranges`, `confidence_cap`, `quality_flags` |
| `xau_macro_pressure.json` | `ts_utc`, `symbol`, `monitor_only`, `pressure_state`, `drivers`, `confidence_cap`, `quality_flags` |
| `xau_event_risk_state.json` | `ts_utc`, `symbol`, `monitor_only`, `risk_state`, `event_count`, `high_impact_events`, `near_high_impact_events`, `confidence_cap`, `quality_flags` |
| `xau_lfx_external_state.json` | `ts_utc`, `symbol`, `monitor_only`, `state`, `summary`, `evidence`, `quality` |
| `xau_user_insight.json` | `ts_utc`, `symbol`, `monitor_only`, `headline`, `now_read`, `operator_focus`, `evidence_map`, `useful_limits`, `upgrade_requirements`, `quality_flags` |
| `xau_artifact_quality.json` | `ts_utc`, `symbol`, `monitor_only`, `status`, `quality_score`, `quality_grade`, `source_count`, `warnings`, `errors`, `confidence_cap` |
| `xau_context_summary.json` | `ts_utc`, `symbol`, `monitor_only`, `latest_close`, `spread_state`, `event_risk_state`, `quality_status`, `quality_grade`, `confidence_cap`, `confidence_explanation`, `monitor_focus`, `limitations`, `quality_flags` |

## Scope

The validator checks:

- file presence;
- JSON parsing;
- top-level object shape;
- required key presence;
- monitor-only flag preservation.

The validator does not check:

- statistical reliability;
- future market behavior;
- data vendor correctness beyond the emitted artifacts;
- full nested object schemas.

## Compatibility rule

Patch releases may add optional keys.

Removing a required key, changing an artifact file name, or changing the meaning of a required key requires a new contract version and a changelog note.

## Safety boundary

The contract is a data compatibility gate only. It does not convert artifacts into a trading system and does not relax the monitor-only project rules.
'''

TEST_ARTIFACT_CONTRACT = r'''import json

from xau_lfx.artifact_contract import ARTIFACT_CONTRACT_VERSION, validate_artifact_contract
from xau_lfx.config import artifact_paths
from xau_lfx.pipeline import run_once


def test_artifact_contract_accepts_generated_sample_artifacts(tmp_path):
    run_once(input_dir="examples/sample-data", event_file="examples/sample-data/usd_events.csv", out_dir=tmp_path)

    result = validate_artifact_contract(tmp_path)

    assert result["schema_contract_version"] == ARTIFACT_CONTRACT_VERSION
    assert result["status"] == "OK"
    assert result["checked_artifact_count"] == 10
    assert result["errors"] == []


def test_artifact_contract_reports_missing_files(tmp_path):
    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert result["errors"]
    assert any("missing artifact" in error for error in result["errors"])


def test_artifact_contract_rejects_missing_monitor_only_flag(tmp_path):
    paths = artifact_paths(tmp_path)
    paths["artifact_quality"].parent.mkdir(parents=True, exist_ok=True)
    paths["artifact_quality"].write_text(
        json.dumps(
            {
                "ts_utc": "2026-06-19T00:00:00+00:00",
                "symbol": "XAUUSD",
                "status": "OK",
                "quality_score": 90.0,
                "quality_grade": "A",
                "source_count": 1,
                "warnings": [],
                "errors": [],
                "confidence_cap": 0.75,
            }
        ),
        encoding="utf-8",
    )

    result = validate_artifact_contract(tmp_path)

    assert result["status"] == "ERROR"
    assert any("xau_artifact_quality.json: missing required keys: monitor_only" in error for error in result["errors"])
    assert any("xau_artifact_quality.json: monitor_only must be true" in error for error in result["errors"])
'''

# New files.
require_missing("xau_lfx/artifact_contract.py")
require_missing("docs/ARTIFACT_CONTRACT.md")
require_missing("tests/test_artifact_contract.py")
write("xau_lfx/artifact_contract.py", ARTIFACT_CONTRACT_PY)
write("docs/ARTIFACT_CONTRACT.md", ARTIFACT_CONTRACT_DOC)
write("tests/test_artifact_contract.py", TEST_ARTIFACT_CONTRACT)

# Version and docs.
replace_once("README.md", "# XAUUSD Market Context v2.4.0", "# XAUUSD Market Context v2.5.0")
replace_once(
    "README.md",
    "Generate auditable XAUUSD market-context artifacts from local MT5/broker CSV exports, spread snapshots, manual USD event files, or an optional private OANDA v20 Practice dashboard. v2.4.0 adds five-second live refresh for mobile and desktop while keeping the token in the local server process. The package is a monitor-only sidecar for XAU research workflows; it uses the LFX-2 material as a semantic and safety baseline without modifying or reproducing the Pine source.",
    "Generate auditable XAUUSD market-context artifacts from local MT5/broker CSV exports, spread snapshots, manual USD event files, or an optional private OANDA v20 Practice dashboard. v2.5.0 adds an artifact contract validator so shared JSON bundles can be checked before downstream inspection. The package is a monitor-only sidecar for XAU research workflows; it uses the LFX-2 material as a semantic and safety baseline without modifying or reproducing the Pine source.",
)
replace_once(
    "README.md",
    "Complete CLI reference: [`docs/CLI_USAGE.md`](docs/CLI_USAGE.md).\n\n## OANDA Practice live dashboard",
    "Complete CLI reference: [`docs/CLI_USAGE.md`](docs/CLI_USAGE.md).\n\nValidate generated artifact compatibility:\n\n```bash\nxau-lfx validate-artifacts --artifact-dir artifacts\n```\n\nThis checks required top-level keys, `monitor_only: true`, and JSON readability for the committed artifact contract. It does not validate predictive usefulness and does not infer direction.\n\nArtifact contract reference: [`docs/ARTIFACT_CONTRACT.md`](docs/ARTIFACT_CONTRACT.md).\n\n## OANDA Practice live dashboard",
)
replace_once("README.md", "docs/ISSUE_BACKLOG_SEED.md\ndocs/CONTEXT_SUMMARY.md", "docs/ISSUE_BACKLOG_SEED.md\ndocs/ARTIFACT_CONTRACT.md\ndocs/CONTEXT_SUMMARY.md")

replace_once("pyproject.toml", 'version = "2.4.0"', 'version = "2.5.0"')
replace_once("xau_lfx/__init__.py", '__version__ = "2.4.0"', '__version__ = "2.5.0"')
replace_once("xau_lfx/web.py", 'version="2.4.0"', 'version="2.5.0"')
replace_once("xau_lfx/web.py", 'version="2.4.0"', 'version="2.5.0"')
replace_once("scripts/check_release_readiness.py", 'EXPECTED_VERSION = "2.4.0"', 'EXPECTED_VERSION = "2.5.0"')
replace_once("scripts/check_release_readiness.py", '    "docs/CONTEXT_SUMMARY.md",', '    "docs/CONTEXT_SUMMARY.md",\n    "docs/ARTIFACT_CONTRACT.md",')

replace_once(
    "CHANGELOG.md",
    "# Changelog\n\n## v2.4.0 - OANDA Practice live dashboard and Phase F usage cases",
    "# Changelog\n\n## v2.5.0 - Artifact contract validation\n\n### Added\n\n- `xau-lfx validate-artifacts` command for generated JSON artifact compatibility checks.\n- `xau_lfx.artifact_contract` module with a stable top-level required-key contract.\n- `docs/ARTIFACT_CONTRACT.md` documenting the current artifact contract and validation scope.\n- CI smoke step for the artifact contract validator.\n- Tests for generated sample artifacts, missing artifact handling, and CLI output.\n\n### Preserved\n\n- Existing CSV ingestion, report generation, static site, and OANDA Practice dashboard behavior.\n- Existing artifact payload calculations.\n- Monitor-only safety contract.\n- No Pine source modification, runtime order workflow, account-risk logic, inventory claim, or profitability claim.\n\n## v2.4.0 - OANDA Practice live dashboard and Phase F usage cases",
)
replace_once("ROADMAP.md", "- `v2.4.0`: synthetic real-world usage cases, sanitized report sharing, and an optional private OANDA Practice live dashboard.", "- `v2.4.0`: synthetic real-world usage cases, sanitized report sharing, and an optional private OANDA Practice live dashboard.\n- `v2.5.0`: artifact contract validation for generated JSON bundles.")
replace_once("ROADMAP.md", "- artifact schema stability and compatibility policy;", "- full JSON Schema files and semantic compatibility policy;")

# Pipeline CLI.
replace_once(
    "xau_lfx/pipeline.py",
    "from xau_lfx.config import ARTIFACTS, DEFAULT_SYMBOL, PACKAGE_ROOT, artifact_paths\n",
    "from xau_lfx.config import ARTIFACTS, DEFAULT_SYMBOL, PACKAGE_ROOT, artifact_paths\nfrom xau_lfx.artifact_contract import validate_artifact_contract\n",
)
replace_once(
    "xau_lfx/pipeline.py",
    "    report_parser = sub.add_parser(\"report\")\n    report_parser.add_argument(\"--artifact-dir\", default=\"artifacts\")\n    report_parser.add_argument(\"--write-md\", action=\"store_true\")\n\n    site_parser = sub.add_parser(\"site\")",
    "    report_parser = sub.add_parser(\"report\")\n    report_parser.add_argument(\"--artifact-dir\", default=\"artifacts\")\n    report_parser.add_argument(\"--write-md\", action=\"store_true\")\n\n    validate_artifacts_parser = sub.add_parser(\"validate-artifacts\")\n    validate_artifacts_parser.add_argument(\"--artifact-dir\", default=\"artifacts\")\n\n    site_parser = sub.add_parser(\"site\")",
)
replace_once(
    "xau_lfx/pipeline.py",
    "    elif args.command == \"report\":\n        report = write_market_context_report(args.artifact_dir, write_md=args.write_md)\n        print(report if not args.write_md else str(artifact_paths(args.artifact_dir)[\"market_context_report\"]))\n    elif args.command == \"site\":",
    "    elif args.command == \"report\":\n        report = write_market_context_report(args.artifact_dir, write_md=args.write_md)\n        print(report if not args.write_md else str(artifact_paths(args.artifact_dir)[\"market_context_report\"]))\n    elif args.command == \"validate-artifacts\":\n        result = validate_artifact_contract(args.artifact_dir)\n        print(json.dumps(result, indent=2, ensure_ascii=False))\n        if result[\"status\"] == \"ERROR\":\n            raise SystemExit(1)\n    elif args.command == \"site\":",
)

# CI and CLI docs/tests.
replace_once(
    ".github/workflows/tests.yml",
    "      - run: python -m xau_lfx.pipeline run-once --input-dir examples/sample-data --event-file examples/sample-data/usd_events.csv --out-dir artifacts\n      - run: python -m xau_lfx.pipeline report --artifact-dir artifacts --write-md",
    "      - run: python -m xau_lfx.pipeline run-once --input-dir examples/sample-data --event-file examples/sample-data/usd_events.csv --out-dir artifacts\n      - run: python -m xau_lfx.pipeline validate-artifacts --artifact-dir artifacts\n      - run: python -m xau_lfx.pipeline report --artifact-dir artifacts --write-md",
)
replace_once(
    "docs/CLI_USAGE.md",
    "Running `xau-lfx run-once` without local files preserves the existing low-confidence readiness behavior.\n\n## Generate the Markdown report",
    "Running `xau-lfx run-once` without local files preserves the existing low-confidence readiness behavior.\n\n## Validate generated artifacts\n\n```bash\nxau-lfx validate-artifacts --artifact-dir artifacts\n```\n\nThe command checks generated JSON artifacts against the package artifact contract:\n\n- required artifact files must exist;\n- required top-level keys must be present;\n- every checked JSON artifact must keep `monitor_only: true`.\n\nValidation failure exits with code `1`.\n\n## Generate the Markdown report",
)
replace_once("tests/test_cli.py", "from xau_lfx.pipeline import main", "from xau_lfx.pipeline import main, run_once")
replace_once(
    "tests/test_cli.py",
    "\ndef test_cli_usage_documents_demo_and_existing_commands():",
    "\n\ndef test_validate_artifacts_command_checks_generated_files(tmp_path, monkeypatch, capsys):\n    artifact_dir = tmp_path / \"artifacts\"\n    sample_dir = ROOT / \"examples\" / \"sample-data\"\n    run_once(input_dir=sample_dir, event_file=sample_dir / \"usd_events.csv\", out_dir=artifact_dir)\n    monkeypatch.setattr(\n        sys,\n        \"argv\",\n        [\n            \"xau-lfx\",\n            \"validate-artifacts\",\n            \"--artifact-dir\",\n            str(artifact_dir),\n        ],\n    )\n\n    main()\n\n    output = capsys.readouterr().out\n    assert '\"status\": \"OK\"' in output\n    assert '\"schema_contract_version\": \"1.0.0\"' in output\n\n\ndef test_validate_artifacts_command_exits_on_missing_artifacts(tmp_path, monkeypatch):\n    monkeypatch.setattr(sys, \"argv\", [\"xau-lfx\", \"validate-artifacts\", \"--artifact-dir\", str(tmp_path)])\n\n    try:\n        main()\n    except SystemExit as exc:\n        assert exc.code == 1\n    else:\n        raise AssertionError(\"validate-artifacts should fail when artifacts are missing\")\n\n\ndef test_cli_usage_documents_demo_and_existing_commands():",
)
replace_once("tests/test_cli.py", '["demo", "validate-sources", "run-once", "report", "site"]', '["demo", "validate-sources", "run-once", "validate-artifacts", "report", "site"]')

print("Applied v2.5.0 artifact contract validation patch.")
print("Run: python -m compileall xau_lfx scripts && python -m pytest -q && python -m build")
