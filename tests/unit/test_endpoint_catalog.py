from softcom_selfhost_automation.endpoint_catalog import (
    DESKTOP_ENDPOINTS,
    DESKTOP_V1_ENDPOINTS,
    DESKTOP_V2_ENDPOINTS,
    EndpointKind,
)


def test_catalogo_nao_possui_metodo_e_rota_duplicados() -> None:
    keys = [(endpoint.method, endpoint.path) for endpoint in DESKTOP_ENDPOINTS]

    assert len(keys) == len(set(keys))


def test_catalogo_contem_todos_os_dominios_v1_solicitados() -> None:
    domains = {endpoint.domain for endpoint in DESKTOP_V1_ENDPOINTS}

    assert {
        "api_status",
        "balanco",
        "catraca",
        "clientes",
        "empresa",
        "grupos",
        "produtos",
        "promocao",
        "restaurante",
        "vendas",
        "vendas360_webhook",
        "vendedores",
        "vinculos_fiscais",
    }.issubset(domains)


def test_catalogo_v2_contem_todas_as_rotas_enumeradas() -> None:
    assert DESKTOP_V2_ENDPOINTS
    assert all(endpoint.path.startswith("/api/v2/") for endpoint in DESKTOP_V2_ENDPOINTS)


def test_operacoes_de_escrita_estao_marcadas_como_destrutivas() -> None:
    assert all(
        endpoint.kind is EndpointKind.DESTRUCTIVE
        for endpoint in DESKTOP_ENDPOINTS
        if endpoint.method in {"POST", "PUT", "PATCH", "DELETE"}
        and "healthcheck" not in endpoint.path
        and endpoint.auth != "dricaia_login"
    )


def test_rotas_parametrizadas_possuem_caminho_de_amostra() -> None:
    assert all(endpoint.sample_path for endpoint in DESKTOP_ENDPOINTS if "{" in endpoint.path)
