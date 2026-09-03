import pytest

from softcom_selfhost_automation.clients import ApiClient, AuthenticationClient
from softcom_selfhost_automation.config import Settings


@pytest.mark.api
@pytest.mark.smoke
def test_gera_token_com_client_credentials(api_client: ApiClient, settings: Settings) -> None:
    if settings.device_url is not None:
        pytest.skip("SELFHOST_DEVICE_URL configurada; credenciais manuais nao sao necessarias")
    if not settings.credentials_configured:
        pytest.skip("credenciais de automação não configuradas")

    token = AuthenticationClient(api_client).create_token(
        settings.client_id, settings.client_secret
    )

    assert token.value
    assert token.token_type.lower() == "bearer"
    assert token.expires_in > 0


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.desktop
def test_gera_token_com_url_do_dispositivo(api_client: ApiClient, settings: Settings) -> None:
    if settings.device_url is None:
        pytest.skip("SELFHOST_DEVICE_URL nao configurada")

    token = AuthenticationClient(api_client).create_token_from_device_url(str(settings.device_url))

    assert token.value
    assert token.token_type.lower() == "bearer"
    assert token.expires_in > 0


@pytest.mark.api
@pytest.mark.functional
def test_rejeita_grant_type_invalido(api_client: ApiClient) -> None:
    response = api_client.post(
        "/authentication/token",
        data={"grant_type": "password", "client_id": "invalido", "client_secret": "invalido"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 64
    assert payload["message"] == "Unsupported grant_type"
