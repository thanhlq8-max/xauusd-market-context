from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_static_demo_screenshot_asset_is_documented_and_embedded():
    demo = (ROOT / "docs" / "DEMO_WALKTHROUGH.md").read_text(encoding="utf-8")
    asset = ROOT / "docs" / "assets" / "static-demo-screenshot.svg"
    svg = asset.read_text(encoding="utf-8")

    assert "assets/static-demo-screenshot.svg" in demo
    assert "site/index.html" in demo
    assert "python -m xau_lfx.pipeline site --artifact-dir artifacts --out-dir site" in demo
    assert "docs/assets/static-demo-screenshot.svg" in demo

    assert "data:image/png;base64," in svg
    assert "XAUUSD Market Context static demo screenshot" in svg
    assert "width=\"1015\"" in svg
    assert "height=\"858\"" in svg


def test_manifest_includes_docs_assets():
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "recursive-include docs/assets *.svg" in manifest
