from __future__ import annotations

import httpx

from .api import ApiClient


class HealthcheckClient:
    def __init__(self, api: ApiClient) -> None:
        self._api = api

    def status(self) -> httpx.Response:
        return self._api.get("/api/v2/healthcheck")

    def info(self) -> httpx.Response:
        return self._api.get("/api/v2/healthcheck/info")
