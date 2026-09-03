from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import uuid4

import httpx

from .api import ApiClient


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    token_type: str
    expires_in: int


@dataclass(frozen=True, slots=True)
class DeviceAuthentication:
    token: AccessToken
    api_base_url: str | None = None


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
        return self._parse_token(response)

    def _parse_token(self, response: httpx.Response) -> AccessToken:
        envelope = self._api.parse_envelope(response)
        assert envelope.get("code") in (None, 0, 1), envelope

        data: Any = envelope.get("data")
        if not isinstance(data, dict) or not data.get("token"):
            raise AssertionError(f"Token ausente na resposta: {envelope}")

        return AccessToken(
            value=str(data["token"]),
            token_type=str(data.get("type", "Bearer")),
            expires_in=int(data.get("expires_in", 0)),
        )

    def create_token_from_device_url(self, device_url: str) -> AccessToken:
        """Cadastra um device temporario e troca suas credenciais por um token."""

        return self.create_authentication_from_device_url(device_url).token

    def create_authentication_from_device_url(self, device_url: str) -> DeviceAuthentication:
        """Cadastra o device e retorna token e URL da API informada pelo Selfhost."""

        registration_url, token_base_url = self._prepare_device_registration(device_url)
        response = self._api.post_url(
            registration_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            content=b"",
        )
        envelope = self._api.parse_envelope(response)
        assert envelope.get("code") in (None, 0, 1), envelope

        data: Any = envelope.get("data")
        if not isinstance(data, dict):
            raise AssertionError(f"Dados do dispositivo ausentes na resposta: {envelope}")

        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
        if not client_id or not client_secret:
            raise AssertionError(f"Credenciais do dispositivo ausentes na resposta: {envelope}")

        resources = data.get("resources")
        api_base_url = None
        if isinstance(resources, dict):
            resource_url = resources.get("url_base")
            if resource_url:
                api_base_url = str(resource_url).rstrip("/")

        response = self._api.post_url(
            f"{token_base_url}/authentication/token",
            data={
                "grant_type": "client_credentials",
                "client_id": str(client_id),
                "client_secret": str(client_secret),
            },
        )
        return DeviceAuthentication(token=self._parse_token(response), api_base_url=api_base_url)

    @staticmethod
    def _prepare_device_registration(device_url: str) -> tuple[str, str]:
        parsed = urlsplit(device_url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("SELFHOST_DEVICE_URL deve ser uma URL HTTP(S) valida")

        path_parts = [part for part in parsed.path.split("/") if part]
        try:
            device_index = path_parts.index("device")
        except ValueError as error:
            raise ValueError("SELFHOST_DEVICE_URL deve apontar para /device/add") from error

        if path_parts[device_index : device_index + 2] != ["device", "add"]:
            raise ValueError("SELFHOST_DEVICE_URL deve apontar para /device/add")

        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if not query.get("client_id"):
            raise ValueError("SELFHOST_DEVICE_URL nao contem o parametro client_id")

        query["device_id"] = f"PYTEST_AUTOMACAO_{uuid4().hex[:12]}"
        registration_url = urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), "")
        )

        prefix = path_parts[:device_index]
        base_path = f"/{'/'.join(prefix)}" if prefix else ""
        token_base_url = urlunsplit((parsed.scheme, parsed.netloc, base_path, "", "")).rstrip("/")
        return registration_url, token_base_url
