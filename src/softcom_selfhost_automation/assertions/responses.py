from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


def assert_success_envelope(response: httpx.Response) -> Mapping[str, Any]:
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, dict), payload
    assert payload.get("code") in (None, 0), payload
    return payload
