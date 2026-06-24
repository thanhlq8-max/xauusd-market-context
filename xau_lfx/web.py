from __future__ import annotations

import argparse
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from ipaddress import ip_address
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from xau_lfx.config import ARTIFACTS
from xau_lfx.connectors.oanda_v20 import OandaPracticeConfig, OandaPracticeConnector, UrllibJsonTransport
from xau_lfx.live import LiveSnapshotUnavailable, OandaLiveService
from xau_lfx.pipeline import run_once
from xau_lfx.reports.live_dashboard import build_live_dashboard_html
from xau_lfx.utils import read_json

app = FastAPI(title="XAU-LFX External Data Foundation", version="2.5.0")


@app.get("/api/xau/state")
def get_state() -> dict:
    return read_json(ARTIFACTS["state"])


@app.get("/api/xau/data-quality")
def get_data_quality() -> dict:
    return read_json(ARTIFACTS["data_quality"])


@app.get("/api/xau/session-context")
def get_session_context() -> dict:
    return read_json(ARTIFACTS["session_context"])


@app.get("/api/xau/macro-pressure")
def get_macro_pressure() -> dict:
    return read_json(ARTIFACTS["macro_pressure"])


@app.get("/api/xau/event-risk")
def get_event_risk() -> dict:
    return read_json(ARTIFACTS["event_risk"])


@app.get("/api/xau/composite-ohlcv")
def get_composite_ohlcv() -> dict:
    return read_json(ARTIFACTS["composite_ohlcv"])


@app.get("/api/xau/user-insight")
def get_user_insight() -> dict:
    return read_json(ARTIFACTS["user_insight"])


@app.get("/api/xau/artifact-quality")
def get_artifact_quality() -> dict:
    return read_json(ARTIFACTS["artifact_quality"])


def serve(host: str, port: int) -> None:
    run_once()
    uvicorn.run("xau_lfx.web:app", host=host, port=port, reload=False)


def create_oanda_live_app(service: OandaLiveService) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task = asyncio.create_task(service.run())
        try:
            yield
        finally:
            service.stop()
            await task

    live_app = FastAPI(
        title="XAUUSD OANDA Practice Live Context",
        version="2.5.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )

    @live_app.get("/", response_class=HTMLResponse)
    def dashboard() -> HTMLResponse:
        return HTMLResponse(
            build_live_dashboard_html(),
            headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": (
                    "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                    "connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
                ),
                "Referrer-Policy": "no-referrer",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @live_app.get("/api/xau/live")
    def live_snapshot() -> dict:
        try:
            return service.snapshot_view(datetime.now(timezone.utc))
        except LiveSnapshotUnavailable as exc:
            raise HTTPException(
                status_code=503,
                detail={"message": str(exc), "health": service.health()},
            ) from exc

    @live_app.get("/api/xau/live/health")
    def live_health() -> dict:
        return service.health()

    return live_app


def _validate_private_host(host: str) -> None:
    if host == "localhost":
        return
    try:
        address = ip_address(host)
    except ValueError as exc:
        raise ValueError("--host must be localhost or an IP address") from exc
    if not (address.is_loopback or address.is_private or address.is_link_local or address.is_unspecified):
        raise ValueError("--host must bind to a loopback, private, link-local, or local wildcard address")


def serve_oanda(host: str, port: int, request_timeout_seconds: float, token: str) -> None:
    _validate_private_host(host)
    if not 1 <= port <= 65535:
        raise ValueError("--port must be between 1 and 65535")
    config = OandaPracticeConfig(token=token, timeout_seconds=request_timeout_seconds)
    connector = OandaPracticeConnector(config=config, transport=UrllibJsonTransport())
    live_app = create_oanda_live_app(OandaLiveService(connector))
    uvicorn.run(live_app, host=host, port=port, reload=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="XAU-LFX External Data API")
    sub = parser.add_subparsers(dest="command", required=True)
    serve_parser = sub.add_parser("serve")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8766)
    oanda_parser = sub.add_parser("serve-oanda", help="Run the private OANDA Practice live dashboard.")
    oanda_parser.add_argument("--host", required=True)
    oanda_parser.add_argument("--port", required=True, type=int)
    oanda_parser.add_argument("--request-timeout-seconds", required=True, type=float)
    args = parser.parse_args()
    if args.command == "serve":
        serve(args.host, args.port)
    elif args.command == "serve-oanda":
        token = os.environ.get("OANDA_API_TOKEN")
        if token is None:
            parser.exit(2, "serve-oanda failed: OANDA_API_TOKEN is not set in the local process\n")
        try:
            serve_oanda(args.host, args.port, args.request_timeout_seconds, token)
        except ValueError as exc:
            parser.exit(2, f"serve-oanda failed: {exc}\n")


if __name__ == "__main__":
    main()
