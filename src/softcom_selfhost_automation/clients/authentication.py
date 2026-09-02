from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .api import ApiClient


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    token_type: str
    expires_in: int


class AuthenticationClient:
    def __init__(self, api: ApiClient) -> None:
        self._api = api

    def create_token(self, client_id: str, client_secret: str) -> AccessToken:
        response = self._api.post(
            "/authentication/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        envelope = self._api.parse_envelope(response)
        assert envelope.get("code") in (None, 0), envelope

        data: Any = envelope.get("data")
        if not isinstance(data, dict) or not data.get("token"):
            raise AssertionError(f"Token ausente na resposta: {envelope}")

        return AccessToken(
            value=str(data["token"]),
            token_type=str(data.get("type", "Bearer")),
            expires_in=int(data.get("expires_in", 0)),
        )
