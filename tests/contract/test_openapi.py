import json
from pathlib import Path
from typing import Any

import pytest

from softcom_selfhost_automation.clients import ApiClient


def _without_environment_data(document: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(document)
    normalized.pop("servers", None)
    return normalized


@pytest.mark.api
@pytest.mark.contract
@pytest.mark.parametrize("version", ["v1", "v2"])
def test_documento_openapi_corresponde_ao_baseline(
    authorized_client: ApiClient,
    pytestconfig: pytest.Config,
    version: str,
) -> None:
    response = authorized_client.get(f"/scalar/swagger/{version}/swagger.json")
    assert response.status_code == 200, response.text
    current = response.json()
    assert isinstance(current, dict)

    baseline_path = Path(str(pytestconfig.rootpath)) / "schemas" / f"{version}.openapi.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert _without_environment_data(current) == baseline, (
        f"O OpenAPI {version} publicado divergiu de {baseline_path}. "
        "Classifique a alteração como bug ou evolução prevista antes de atualizar o baseline."
    )


@pytest.mark.contract
def test_baseline_openapi_documenta_healthcheck(
    openapi_documents: dict[str, dict[str, Any]],
) -> None:
    assert "/api/v2/healthcheck" in openapi_documents["v2"]["paths"]
