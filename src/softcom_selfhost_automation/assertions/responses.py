from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

REQUIRED_ENVELOPE_FIELDS = {"code", "message", "human", "data"}


def assert_json_object(response: httpx.Response) -> Mapping[str, Any]:
    assert response.headers.get("content-type", "").lower().startswith("application/json"), (
        response.text
    )
    payload = response.json()
    assert isinstance(payload, dict), payload
    return payload


def assert_contract_response(response: httpx.Response) -> Mapping[str, Any]:
    """Valida que a rota existe e responde com o contrato JSON padrao."""

    # Um recurso inexistente pode retornar 404 com o envelope correto. O 405
    # continua indicando verbo/rota incompatível com o catálogo.
    assert response.status_code != 405, response.text
    assert response.status_code < 500, response.text
    payload = assert_json_object(response)
    missing = REQUIRED_ENVELOPE_FIELDS.difference(payload)
    assert not missing, f"Campos ausentes no envelope: {sorted(missing)}; payload={payload}"
    assert isinstance(payload["code"], (int, str)), payload
    assert payload["message"] is None or isinstance(payload["message"], str), payload
    assert payload["human"] is None or isinstance(payload["human"], str), payload
    return payload


def assert_content_response(response: httpx.Response) -> None:
    """Valida endpoints de status que retornam HTML ou JSON sem envelope."""

    assert response.status_code not in {404, 405}, response.text
    assert response.status_code < 500, response.text
    assert response.content, "A resposta não possui conteúdo"


def assert_success_envelope(response: httpx.Response) -> Mapping[str, Any]:
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, dict), payload
    assert payload.get("code") in (None, 0, 1), payload
    return payload
