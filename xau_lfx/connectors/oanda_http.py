from __future__ import annotations

import http.client
import json
from typing import Any
from urllib.parse import urlparse


def oanda_http_transport(url: str, headers: dict[str, str], timeout: float) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("OANDA transport requires https URL")
    path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
    connection = http.client.HTTPSConnection(parsed.netloc, timeout=timeout)
    try:
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        if response.status >= 400:
            raise RuntimeError(f"OANDA_HTTP_ERROR_{response.status}: {body[:200]}")
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError("OANDA response must be a JSON object")
        return payload
    finally:
        connection.close()
