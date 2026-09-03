from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from softcom_selfhost_automation.capabilities import is_endpoint_supported
from softcom_selfhost_automation.clients import ApiClient, AuthenticationClient
from softcom_selfhost_automation.clients.authentication import DeviceAuthentication
from softcom_selfhost_automation.config import Environment, Settings, load_settings


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("selfhost")
    group.addoption(
        "--environment",
        choices=[item.value for item in Environment],
        default=Environment.DESKTOP.value,
        help="ERP alvo: desktop (SQL Server) ou web (SoftcomShop/MySQL)",
    )
    group.addoption(
        "--run-api-tests",
        action="store_true",
        default=False,
        help="Executa testes que fazem chamadas à instância configurada",
    )
    group.addoption(
        "--run-destructive-tests",
        action="store_true",
        default=False,
        help="Executa endpoints que criam, alteram ou removem dados",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    environment = Environment(config.getoption("--environment"))
    run_api_tests = bool(config.getoption("--run-api-tests"))
    run_destructive_tests = bool(config.getoption("--run-destructive-tests"))

    for item in items:
        if item.get_closest_marker("api") and not run_api_tests:
            item.add_marker(pytest.mark.skip(reason="use --run-api-tests para acessar a API"))
        if item.get_closest_marker("destructive") and not run_destructive_tests:
            item.add_marker(
                pytest.mark.skip(reason="use --run-destructive-tests para alterar dados")
            )
        if item.get_closest_marker("desktop") and environment is not Environment.DESKTOP:
            item.add_marker(pytest.mark.skip(reason="endpoint disponível somente no Desktop"))
        if item.get_closest_marker("web") and environment is not Environment.WEB:
            item.add_marker(pytest.mark.skip(reason="endpoint disponível somente no WEB"))


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    project_root = Path(__file__).resolve().parents[1]
    environment = str(pytestconfig.getoption("--environment"))
    return load_settings(environment, project_root / "config")


@pytest.fixture(scope="session")
def api_client(settings: Settings) -> Iterator[ApiClient]:
    with ApiClient(
        str(settings.base_url),
        timeout=settings.request_timeout,
        verify_ssl=settings.verify_ssl,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def authentication(settings: Settings, api_client: ApiClient) -> DeviceAuthentication:
    authentication = AuthenticationClient(api_client)
    if settings.device_url is not None:
        return authentication.create_authentication_from_device_url(str(settings.device_url))
    if settings.credentials_configured:
        return DeviceAuthentication(
            token=authentication.create_token(settings.client_id, settings.client_secret)
        )
    pytest.skip("configure SELFHOST_DEVICE_URL ou SELFHOST_CLIENT_ID/SELFHOST_CLIENT_SECRET")


@pytest.fixture(scope="session")
def authorized_client(
    settings: Settings, authentication: DeviceAuthentication
) -> Iterator[ApiClient]:
    with ApiClient(
        authentication.api_base_url or str(settings.base_url),
        timeout=settings.request_timeout,
        verify_ssl=settings.verify_ssl,
        token=authentication.token.value,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def openapi_documents(
    pytestconfig: pytest.Config,
) -> dict[str, dict[str, Any]]:
    project_root = Path(str(pytestconfig.rootpath))
    documents: dict[str, dict[str, Any]] = {}
    for version in ("v1", "v2"):
        baseline = project_root / "schemas" / f"{version}.openapi.json"
        if not baseline.is_file():
            raise AssertionError(f"Baseline OpenAPI não encontrado: {baseline}")
        document = json.loads(baseline.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise AssertionError(f"Baseline OpenAPI {version} não contém um objeto JSON")
        documents[version] = document
    return documents


@pytest.fixture(scope="session")
def dricaia_token(settings: Settings, authentication: DeviceAuthentication) -> str:
    if not settings.dricaia_credentials_configured:
        pytest.skip("configure SELFHOST_DRICAIA_EMAIL e SELFHOST_DRICAIA_PASSWORD")

    base_url = authentication.api_base_url or str(settings.base_url)
    with ApiClient(
        base_url,
        timeout=settings.request_timeout,
        verify_ssl=settings.verify_ssl,
    ) as login_client:
        response = login_client.post(
            "/api/v2/dricaia/login",
            json={"email": settings.dricaia_email, "password": settings.dricaia_password},
        )
        response.raise_for_status()
        payload = response.json()
        token = payload.get("data", {}).get("token") if isinstance(payload, dict) else None
        if not token:
            raise AssertionError(f"Token DricaIA ausente na resposta: {payload}")

    return str(token)


@pytest.fixture(scope="session")
def dricaia_client(
    settings: Settings, authentication: DeviceAuthentication, dricaia_token: str
) -> Iterator[ApiClient]:
    base_url = authentication.api_base_url or str(settings.base_url)

    with ApiClient(
        base_url,
        timeout=settings.request_timeout,
        verify_ssl=settings.verify_ssl,
        token=dricaia_token,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def endpoint_is_supported(settings: Settings):  # type: ignore[no-untyped-def]
    def check(method: str, path: str) -> bool:
        return is_endpoint_supported(
            method,
            path,
            settings.environment,
            mesas_database_enabled=settings.restaurant_tests_enabled,
        )

    return check
