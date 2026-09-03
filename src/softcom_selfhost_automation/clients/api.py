from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


class ApiClient:
    """Cliente base com timeout, URL e validacao do envelope padronizados."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        token: str | None = None,
    ) -> None:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=httpx.Timeout(timeout),
            verify=verify_ssl,
        )

    def close(self) -> None:
        self._client.close()

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        return self._client.request(method, path, **kwargs)

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def post_url(self, url: str, **kwargs: Any) -> httpx.Response:
        """Faz POST em URL absoluta, necessario para a URL gerada do dispositivo."""

        return self._client.post(url, **kwargs)

    @staticmethod
    def parse_envelope(response: httpx.Response) -> Mapping[str, Any]:
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise AssertionError("A resposta não contém o envelope JSON esperado")
        return payload

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
