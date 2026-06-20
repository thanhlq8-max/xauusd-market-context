from xau_lfx.forbidden_language import assert_clean_language
from xau_lfx.reports.live_dashboard import build_live_dashboard_html
from xau_lfx.web import _validate_private_host, create_oanda_live_app


class EmptyService:
    async def run(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def health(self) -> dict:
        return {"status": "STARTING"}

    def snapshot_view(self, _now):
        raise AssertionError("not called")


def test_live_dashboard_contains_fixed_refresh_and_mobile_layout():
    html = build_live_dashboard_html()

    assert "const REFRESH_MS = 5000" in html
    assert "@media (max-width: 560px)" in html
    assert "DID / Past" in html
    assert "DOING / Now" in html
    assert "NEXT / Conditional" in html
    assert "MM Mission" in html
    assert "OANDA v20 Practice" in html
    assert "OANDA_API_TOKEN" not in html
    assert_clean_language(html)


def test_live_app_has_private_dashboard_and_live_api_routes():
    app = create_oanda_live_app(EmptyService())  # type: ignore[arg-type]
    paths = {route.path for route in app.routes}

    assert paths >= {"/", "/api/xau/live", "/api/xau/live/health"}
    assert app.docs_url is None
    assert app.redoc_url is None


def test_private_host_validation_rejects_public_address():
    _validate_private_host("127.0.0.1")
    _validate_private_host("192.168.1.20")

    try:
        _validate_private_host("8.8.8.8")
    except ValueError as exc:
        assert "private" in str(exc)
    else:
        raise AssertionError("public address was accepted")
