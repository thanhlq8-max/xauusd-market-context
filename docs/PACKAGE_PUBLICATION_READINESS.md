# Package Publication Readiness

This document is the decision gate before any TestPyPI or PyPI publication.

## Current metadata

The current Python package metadata declares:

```text
project.name = xau-lfx-external-data-foundation
console script = xau-lfx
api script = xau-lfx-api
repository = https://github.com/thanhlq8-max/xauusd-market-context
```

This document does not change those values. A maintainer must confirm the final package name before any upload.

## Decision required before upload

Before publishing to TestPyPI or PyPI, record one explicit decision in release notes or an issue:

```text
PACKAGE_NAME_DECISION: keep xau-lfx-external-data-foundation
```

or:

```text
PACKAGE_NAME_DECISION: rename to <chosen-package-name>
```

Do not publish under a name that has not been explicitly confirmed by the maintainer.

## Preflight checklist

Run these checks from a clean checkout:

```bash
git status --short
python -m compileall xau_lfx scripts
python -m pytest -q
python scripts/check_release_readiness.py --strict
python -m build
```

Then inspect the generated package metadata locally before upload:

```bash
python -m pip install --force-reinstall dist/*.whl
xau-lfx --help
xau-lfx validate-artifacts --artifact-dir examples/sample-artifacts
```

The wheel must preserve the packaged schema fallback, and the source distribution must include `schemas/artifacts/`.

## TestPyPI boundary

TestPyPI is for publication rehearsal only. A TestPyPI upload is not production distribution and must not be described as public adoption proof.

Use TestPyPI only after the package-name decision is recorded and local gates pass. Upload credentials must remain outside the repository.

## PyPI boundary

PyPI publication requires a separate maintainer confirmation after TestPyPI validation. Do not add automatic publishing without a separate scope decision.

## Monitor-only boundary

Package publication does not change the project contract:

```text
MONITOR_ONLY
NO_EXECUTION
NO_BUY_SELL_SIGNAL
NO_FINANCIAL_ADVICE
NO_STATISTICAL_EDGE_CLAIM
```

The package remains an artifact generator and validator for auditable market-context research. It does not create orders, size positions, infer profitability, or convert artifacts into directional calls.
