import pytest

from softcom_selfhost_automation.capabilities import is_endpoint_supported
from softcom_selfhost_automation.config import Environment


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v2/healthcheck"),
        ("POST", "/authentication/token"),
        ("POST", "/api/v2/balanco"),
        ("GET", "/api/v2/clientes/clientes"),
    ],
)
def test_endpoints_compartilhados(method: str, path: str) -> None:
    assert is_endpoint_supported(method, path, Environment.DESKTOP)
    assert is_endpoint_supported(method, path, Environment.WEB)


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/balanco"),
        ("GET", "/api/produtos/produtos/collector"),
        ("GET", "/api/agenda"),
        ("POST", "/api/financeiro/recebimentos/recebimento"),
    ],
)
def test_endpoints_exclusivos_do_desktop(method: str, path: str) -> None:
    assert is_endpoint_supported(method, path, Environment.DESKTOP)
    assert not is_endpoint_supported(method, path, Environment.WEB)


def test_restaurante_requer_banco_de_mesas() -> None:
    assert not is_endpoint_supported("GET", "/api/restaurantes/mesa", Environment.DESKTOP)
    assert is_endpoint_supported(
        "GET",
        "/api/restaurantes/mesa",
        Environment.DESKTOP,
        mesas_database_enabled=True,
    )
