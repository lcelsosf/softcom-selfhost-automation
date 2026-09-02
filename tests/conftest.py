from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from softcom_selfhost_automation.capabilities import is_endpoint_supported
from softcom_selfhost_automation.clients import ApiClient, AuthenticationClient
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


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    environment = Environment(config.getoption("--environment"))
    run_api_tests = bool(config.getoption("--run-api-tests"))

    for item in items:
        if item.get_closest_marker("api") and not run_api_tests:
            item.add_marker(pytest.mark.skip(reason="use --run-api-tests para acessar a API"))
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
def access_token(settings: Settings, api_client: ApiClient) -> str:
    if not settings.credentials_configured:
        pytest.skip("configure SELFHOST_CLIENT_ID e SELFHOST_CLIENT_SECRET")
    return (
        AuthenticationClient(api_client)
        .create_token(settings.client_id, settings.client_secret)
        .value
    )


@pytest.fixture(scope="session")
def authorized_client(settings: Settings, access_token: str) -> Iterator[ApiClient]:
    with ApiClient(
        str(settings.base_url),
        timeout=settings.request_timeout,
        verify_ssl=settings.verify_ssl,
        token=access_token,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def endpoint_is_supported(settings: Settings):  # type: ignore[no-untyped-def]
    def check(method: str, path: str) -> bool:
        return is_endpoint_supported(
            method,
            path,
            settings.environment,
            mesas_database_enabled=settings.mesas_database_enabled,
        )

    return check
