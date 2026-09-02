import pytest

from softcom_selfhost_automation.clients import ApiClient
from softcom_selfhost_automation.config import Settings


@pytest.mark.api
@pytest.mark.contract
def test_documento_openapi_esta_disponivel(api_client: ApiClient, settings: Settings) -> None:
    response = api_client.get(settings.openapi_path)

    assert response.status_code == 200, response.text
    document = response.json()
    assert document.get("openapi") or document.get("swagger")
    assert document.get("paths")


@pytest.mark.api
@pytest.mark.contract
def test_openapi_documenta_healthcheck(api_client: ApiClient, settings: Settings) -> None:
    document = api_client.get(settings.openapi_path).json()

    assert "/api/v2/healthcheck" in document["paths"]
