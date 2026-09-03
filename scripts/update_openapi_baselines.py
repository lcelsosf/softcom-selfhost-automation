from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from softcom_selfhost_automation.clients import ApiClient, AuthenticationClient
from softcom_selfhost_automation.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atualiza conscientemente os baselines OpenAPI versionados."
    )
    parser.add_argument("--environment", choices=("desktop", "web"), default="desktop")
    parser.add_argument(
        "--output", type=Path, default=Path("schemas"), help="Diretório dos baselines"
    )
    args = parser.parse_args()

    settings = load_settings(args.environment, Path("config"))
    with ApiClient(
        str(settings.base_url),
        timeout=settings.request_timeout,
        verify_ssl=settings.verify_ssl,
    ) as client:
        authentication = AuthenticationClient(client)
        if settings.device_url is not None:
            credentials = authentication.create_authentication_from_device_url(
                str(settings.device_url)
            )
        elif settings.credentials_configured:
            from softcom_selfhost_automation.clients.authentication import DeviceAuthentication

            credentials = DeviceAuthentication(
                token=authentication.create_token(settings.client_id, settings.client_secret)
            )
        else:
            raise SystemExit(
                "Configure SELFHOST_DEVICE_URL ou SELFHOST_CLIENT_ID/SELFHOST_CLIENT_SECRET"
            )

    with ApiClient(
        credentials.api_base_url or str(settings.base_url),
        timeout=settings.request_timeout,
        verify_ssl=settings.verify_ssl,
        token=credentials.token.value,
    ) as client:
        for version in ("v1", "v2"):
            response = client.get(f"/scalar/swagger/{version}/swagger.json")
            response.raise_for_status()
            document = response.json()
            if not isinstance(document, dict):
                raise SystemExit(f"OpenAPI {version} não retornou um objeto JSON")
            sanitized = _sanitize(document)
            target = args.output / f"{version}.openapi.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(sanitized, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(f"Atualizado: {target}")


def _sanitize(document: dict[str, Any]) -> dict[str, Any]:
    """Remove URLs do ambiente; contratos, operações e schemas são preservados."""

    sanitized = dict(document)
    sanitized.pop("servers", None)
    return sanitized


if __name__ == "__main__":
    # Evita que um valor acidentalmente definido pelo runner altere o baseline alvo.
    os.environ.pop("SELFHOST_DESTRUCTIVE_TESTS_ENABLED", None)
    main()
