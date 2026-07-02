from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Sequence

from xau_lfx.connectors.base import SourceRequest
from xau_lfx.connectors.mt5_bridge import MT5BridgeConnector
from xau_lfx.connectors.oanda_rest import OandaRestConnector


def _json_transport_from_fixture(path: str | Path):
    fixture_path = Path(path)

    def transport(url: str, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        return json.loads(fixture_path.read_text(encoding="utf-8"))

    return transport


def _write_output(payload: dict[str, Any], out_dir: str | Path) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "normalized_ohlcv.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"json": str(output_path)}


def _build_oanda(args: argparse.Namespace):
    token = args.oanda_token or os.getenv("OANDA_TOKEN")
    transport = _json_transport_from_fixture(args.fixture_json) if args.fixture_json else None
    return OandaRestConnector(
        token=token,
        api_url=args.oanda_api_url,
        price_component=args.oanda_price,
        transport=transport,
        timeout=args.timeout,
    )


def _build_mt5(args: argparse.Namespace):
    return MT5BridgeConnector(skip_current_bar=not args.include_current_bar)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch one monitor-only normalized OHLCV snapshot.")
    parser.add_argument("--source", choices=("oanda", "mt5"), required=True)
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--timeframe", choices=("M1", "M5", "M15", "H1"), required=True)
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--fixture-json", help="Offline OANDA response fixture for tests or dry runs.")
    parser.add_argument("--oanda-token", help="Runtime token override. Prefer OANDA_TOKEN env var outside shell history.")
    parser.add_argument("--oanda-api-url", default="https://api-fxpractice.oanda.com/v3")
    parser.add_argument("--oanda-price", default="M")
    parser.add_argument("--include-current-bar", action="store_true")
    args = parser.parse_args(argv)

    request = SourceRequest(source_id=args.source.upper(), symbol=args.symbol, timeframe=args.timeframe, limit=args.limit)
    connector = _build_oanda(args) if args.source == "oanda" else _build_mt5(args)
    result = connector.fetch(request)
    report_paths = _write_output(result, args.out_dir)
    payload = {**result, "report_paths": report_paths}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if result.get("status") == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
