import pytest

from softcom_selfhost_automation.clients import ApiClient, HealthcheckClient


@pytest.mark.api
@pytest.mark.smoke
def test_api_esta_online(api_client: ApiClient) -> None:
    response = HealthcheckClient(api_client).status()

    assert response.status_code == 200, response.text
    assert response.content


@pytest.mark.api
@pytest.mark.smoke
def test_healthcheck_informa_a_retaguarda(api_client: ApiClient) -> None:
    response = HealthcheckClient(api_client).info()

    assert response.status_code == 200, response.text
    assert response.content
