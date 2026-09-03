import pytest

from softcom_selfhost_automation.assertions.responses import (
    assert_content_response,
    assert_contract_response,
    assert_json_object,
)
from softcom_selfhost_automation.clients import ApiClient
from softcom_selfhost_automation.clients.authentication import DeviceAuthentication
from softcom_selfhost_automation.config import Settings
from softcom_selfhost_automation.endpoint_catalog import (
    DESKTOP_ENDPOINTS,
    EndpointKind,
    EndpointSpec,
    ResponseContract,
)

SAFE_ENDPOINTS = tuple(item for item in DESKTOP_ENDPOINTS if item.kind is EndpointKind.SAFE)
DESTRUCTIVE_ENDPOINTS = tuple(
    item for item in DESKTOP_ENDPOINTS if item.kind is EndpointKind.DESTRUCTIVE
)
DRICAIA_ENDPOINTS = tuple(
    item for item in DESKTOP_ENDPOINTS if item.auth == "dricaia" and item.kind is EndpointKind.SAFE
)
DRICAIA_LOGIN_ENDPOINTS = tuple(item for item in DESKTOP_ENDPOINTS if item.auth == "dricaia_login")
SELFHOST_SAFE_ENDPOINTS = tuple(item for item in SAFE_ENDPOINTS if item.auth == "selfhost")
SELFHOST_DESTRUCTIVE_ENDPOINTS = tuple(
    item for item in DESTRUCTIVE_ENDPOINTS if item.auth == "selfhost"
)


def _request(client: ApiClient, endpoint: EndpointSpec):  # type: ignore[no-untyped-def]
    return client.request(endpoint.method, endpoint.request_path, params=dict(endpoint.query))


def _assert_endpoint_contract(response, endpoint: EndpointSpec) -> None:  # type: ignore[no-untyped-def]
    if endpoint.contract is ResponseContract.CONTENT:
        assert_content_response(response)
        return
    if endpoint.contract is ResponseContract.JSON_OBJECT:
        assert response.status_code not in {404, 405}, response.text
        assert response.status_code < 500, response.text
        assert_json_object(response)
        return
    assert_contract_response(response)


@pytest.mark.api
@pytest.mark.contract
@pytest.mark.desktop
@pytest.mark.parametrize("endpoint", SELFHOST_SAFE_ENDPOINTS, ids=lambda item: item.id)
def test_contrato_dos_endpoints_desktop(
    authorized_client: ApiClient,
    settings: Settings,
    endpoint: EndpointSpec,
) -> None:
    if endpoint.domain == "restaurante" and not settings.restaurant_tests_enabled:
        pytest.skip("configure SELFHOST_RESTAURANT_ENDPOINTS_ENABLED=true")
    response = _request(authorized_client, endpoint)

    _assert_endpoint_contract(response, endpoint)


@pytest.mark.api
@pytest.mark.contract
@pytest.mark.desktop
@pytest.mark.destructive
@pytest.mark.parametrize("endpoint", SELFHOST_DESTRUCTIVE_ENDPOINTS, ids=lambda item: item.id)
def test_contrato_dos_endpoints_desktop_destrutivos(
    authorized_client: ApiClient,
    settings: Settings,
    endpoint: EndpointSpec,
) -> None:
    if not settings.destructive_tests_enabled:
        pytest.skip("configure SELFHOST_DESTRUCTIVE_TESTS_ENABLED=true")
    if endpoint.domain == "restaurante" and not settings.restaurant_tests_enabled:
        pytest.skip("configure SELFHOST_RESTAURANT_ENDPOINTS_ENABLED=true")
    # Sem payload, a rota deve validar a requisicao e nao persistir alteracoes.
    response = _request(authorized_client, endpoint)

    _assert_endpoint_contract(response, endpoint)


@pytest.mark.api
@pytest.mark.contract
@pytest.mark.desktop
@pytest.mark.parametrize("endpoint", DRICAIA_ENDPOINTS, ids=lambda item: item.id)
def test_contrato_dos_endpoints_dricaia_desktop(
    dricaia_client: ApiClient,
    endpoint: EndpointSpec,
) -> None:
    response = _request(dricaia_client, endpoint)

    _assert_endpoint_contract(response, endpoint)


@pytest.mark.api
@pytest.mark.contract
@pytest.mark.desktop
@pytest.mark.parametrize("endpoint", DRICAIA_LOGIN_ENDPOINTS, ids=lambda item: item.id)
def test_contrato_do_login_dricaia_desktop(
    dricaia_token: str,
    authentication: DeviceAuthentication,
    endpoint: EndpointSpec,
) -> None:
    # A fixture faz a chamada real ao login e valida o token retornado.
    assert endpoint.path == "/api/v2/dricaia/login"
    assert dricaia_token
    assert authentication.api_base_url is None or authentication.api_base_url.startswith("http")
