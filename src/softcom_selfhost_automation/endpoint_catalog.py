from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EndpointKind(StrEnum):
    SAFE = "safe"
    DESTRUCTIVE = "destructive"


class ResponseContract(StrEnum):
    V1_ENVELOPE = "v1_envelope"
    JSON_OBJECT = "json_object"
    CONTENT = "content"


@dataclass(frozen=True, slots=True)
class EndpointSpec:
    domain: str
    method: str
    path: str
    kind: EndpointKind = EndpointKind.SAFE
    query: tuple[tuple[str, str], ...] = ()
    sample_path: str | None = None
    auth: str = "selfhost"
    contract: ResponseContract = ResponseContract.V1_ENVELOPE

    @property
    def request_path(self) -> str:
        return self.sample_path or self.path

    @property
    def id(self) -> str:
        return f"{self.domain}-{self.method.lower()}-{self.path.strip('/').replace('/', '-')}"


# V1 solicitado para o Desktop. Rotas parametrizadas usam amostras deliberadamente
# inexistentes nos testes de contrato para validar o endpoint sem alterar massa.
DESKTOP_V1_ENDPOINTS = (
    EndpointSpec("api_status", "GET", "/api/status", contract=ResponseContract.CONTENT),
    EndpointSpec("api_status", "GET", "/api/status/info", contract=ResponseContract.CONTENT),
    EndpointSpec("balanco", "GET", "/api/balanco", contract=ResponseContract.JSON_OBJECT),
    EndpointSpec("balanco", "POST", "/api/balanco", EndpointKind.DESTRUCTIVE),
    EndpointSpec("catraca", "POST", "/api/catraca/liberar", EndpointKind.DESTRUCTIVE),
    EndpointSpec("catraca", "POST", "/api/catraca/gerar", EndpointKind.DESTRUCTIVE),
    EndpointSpec("clientes", "GET", "/api/clientes/clientes"),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/clientes/page/{id}",
        sample_path="/api/clientes/clientes/page/1",
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/clientes/page/{page}/{size}",
        sample_path="/api/clientes/clientes/page/1/10",
    ),
    EndpointSpec(
        "clientes", "GET", "/api/clientes/clientes/{id}", sample_path="/api/clientes/clientes/0"
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/clientes/cpf_cnpj/{cpf_cnpj}",
        sample_path="/api/clientes/clientes/cpf_cnpj/00000000000",
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/clientes/busca/{filtro}",
        sample_path="/api/clientes/clientes/busca/PYTEST_INEXISTENTE",
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/clientes/ultima_sincronizacao/{sync}",
        sample_path="/api/clientes/clientes/ultima_sincronizacao/0",
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/clientes/ultima_sincronizacao/{sync}/page/{id}",
        sample_path="/api/clientes/clientes/ultima_sincronizacao/0/page/1",
    ),
    EndpointSpec("clientes", "POST", "/api/clientes/clientes", EndpointKind.DESTRUCTIVE),
    EndpointSpec(
        "clientes",
        "PUT",
        "/api/clientes/clientes/{id}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/clientes/clientes/0",
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/clientes/compras/{clienteId}",
        sample_path="/api/clientes/clientes/compras/0",
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/veiculos/{client_id}",
        sample_path="/api/clientes/veiculos/0",
    ),
    EndpointSpec(
        "clientes", "GET", "/api/clientes/placa/{placa}", sample_path="/api/clientes/placa/PYTEST00"
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/clientes/veiculos/page/{id}",
        sample_path="/api/clientes/veiculos/page/1",
    ),
    EndpointSpec("clientes", "POST", "/api/clientes/veiculos", EndpointKind.DESTRUCTIVE),
    EndpointSpec("empresa", "GET", "/api/empresa"),
    EndpointSpec("empresa", "GET", "/api/empresa/links"),
    EndpointSpec("empresa", "GET", "/api/empresas"),
    EndpointSpec("grupos", "GET", "/api/produtos/grupos"),
    EndpointSpec(
        "grupos", "GET", "/api/produtos/grupos/page/{id}", sample_path="/api/produtos/grupos/page/1"
    ),
    EndpointSpec(
        "grupos", "GET", "/api/produtos/grupos/{id}", sample_path="/api/produtos/grupos/0"
    ),
    EndpointSpec("produtos", "GET", "/api/produtos/produtos"),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/produtos/produtos/page/{id}",
        sample_path="/api/produtos/produtos/page/1",
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/produtos/produtos/ultima_sincronizacao/{sync}",
        sample_path="/api/produtos/produtos/ultima_sincronizacao/0",
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/produtos/produtos/ultima_sincronizacao/{sync}/page/{id}",
        sample_path="/api/produtos/produtos/ultima_sincronizacao/0/page/1",
    ),
    EndpointSpec(
        "produtos", "GET", "/api/produtos/produtos/{id}", sample_path="/api/produtos/produtos/0"
    ),
    EndpointSpec(
        "produtos", "GET", "/api/produtos/produtos2/{id}", sample_path="/api/produtos/produtos2/0"
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/produtos/deletados/ultima_sincronizacao/{sync}",
        sample_path="/api/produtos/deletados/ultima_sincronizacao/0",
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/produtos/deletados/ultima_sincronizacao/{sync}/page/{id}",
        sample_path="/api/produtos/deletados/ultima_sincronizacao/0/page/1",
    ),
    EndpointSpec("produtos", "GET", "/api/produtos/promocao"),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/produtos/produtos/relacionados/{produtoId}",
        sample_path="/api/produtos/produtos/relacionados/0",
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/produtos/produtos/collector",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec("promocao", "GET", "/api/promocao"),
    EndpointSpec("restaurante", "GET", "/api/restaurantes/observacao"),
    EndpointSpec("restaurante", "GET", "/api/restaurantes/configuracao"),
    EndpointSpec("restaurante", "GET", "/api/restaurantes/mesa"),
    EndpointSpec(
        "restaurante", "GET", "/api/restaurantes/mesa/{id}", sample_path="/api/restaurantes/mesa/0"
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/restaurantes/auth/mesa/{id}",
        sample_path="/api/restaurantes/auth/mesa/0",
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/restaurantes/mesa/adiantamento/{id}",
        sample_path="/api/restaurantes/mesa/adiantamento/0",
    ),
    EndpointSpec("restaurante", "GET", "/api/restaurantes/produto-combo"),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/restaurantes/produto-combo/{id}",
        sample_path="/api/restaurantes/produto-combo/0",
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/restaurantes/mesa/{id}/concorrencia/status",
        sample_path="/api/restaurantes/mesa/0/concorrencia/status",
    ),
    EndpointSpec("restaurante", "GET", "/api/restaurantes/dricaia"),
    EndpointSpec("restaurante", "POST", "/api/restaurantes/mesa", EndpointKind.DESTRUCTIVE),
    EndpointSpec("restaurante", "POST", "/api/restaurantes/mesa2", EndpointKind.DESTRUCTIVE),
    EndpointSpec(
        "restaurante",
        "DELETE",
        "/api/restaurantes/mesa/{id}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/restaurantes/mesa/0",
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/restaurantes/mesa/{mesa}/items",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/restaurantes/mesa/0/items",
    ),
    EndpointSpec(
        "restaurante",
        "DELETE",
        "/api/restaurantes/mesa/{mesa}/items/{guid}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/restaurantes/mesa/0/items/00000000-0000-0000-0000-000000000000",
    ),
    EndpointSpec(
        "restaurante", "POST", "/api/restaurantes/mesa/adiantamento", EndpointKind.DESTRUCTIVE
    ),
    EndpointSpec("restaurante", "POST", "/api/restaurantes/chamar", EndpointKind.DESTRUCTIVE),
    EndpointSpec(
        "restaurante",
        "PATCH",
        "/api/restaurantes/mesa/{id}/lacrar",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/restaurantes/mesa/0/lacrar",
    ),
    EndpointSpec(
        "restaurante",
        "PATCH",
        "/api/restaurantes/mesa/{id}/concorrencia",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/restaurantes/mesa/0/concorrencia",
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/restaurantes/transferencia/mesa/items",
        EndpointKind.DESTRUCTIVE,
    ),
    EndpointSpec(
        "restaurante", "POST", "/api/restaurantes/transferencia/mesa", EndpointKind.DESTRUCTIVE
    ),
    EndpointSpec("restaurante", "POST", "/api/restaurantes/mesa/aviso", EndpointKind.DESTRUCTIVE),
    EndpointSpec("restaurante", "PATCH", "/api/restaurantes/reimpressao", EndpointKind.DESTRUCTIVE),
    EndpointSpec("vendas", "GET", "/api/vendas/vendas/pre-venda"),
    EndpointSpec(
        "vendas",
        "GET",
        "/api/vendas/vendas/completa/{id}",
        sample_path="/api/vendas/vendas/completa/0",
    ),
    EndpointSpec("vendas", "POST", "/api/vendas/vendas", EndpointKind.DESTRUCTIVE),
    EndpointSpec(
        "vendas",
        "POST",
        "/api/vendas/vendas/cancela/{chave}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/vendas/vendas/cancela/PYTEST_INEXISTENTE",
    ),
    EndpointSpec("vendas360_webhook", "POST", "/api/vendas360/webhook", EndpointKind.DESTRUCTIVE),
    EndpointSpec("vendedores", "POST", "/authentication/user", EndpointKind.DESTRUCTIVE),
    EndpointSpec("vendedores", "GET", "/api/vendedores/garcom"),
    EndpointSpec("vendedores", "GET", "/api/funcionario"),
    EndpointSpec(
        "vendedores", "GET", "/api/funcionario/page/{id}", sample_path="/api/funcionario/page/1"
    ),
    EndpointSpec(
        "vinculos_fiscais",
        "GET",
        "/api/produtos/vinculosfiscais/ultima_sincronizacao/{sync}",
        sample_path="/api/produtos/vinculosfiscais/ultima_sincronizacao/0",
    ),
    EndpointSpec(
        "vinculos_fiscais",
        "GET",
        "/api/produtos/vinculosfiscais/{id}",
        sample_path="/api/produtos/vinculosfiscais/0",
    ),
)


DESKTOP_V2_ENDPOINTS = (
    EndpointSpec("healthcheck", "GET", "/api/v2/healthcheck", contract=ResponseContract.CONTENT),
    EndpointSpec(
        "healthcheck", "GET", "/api/v2/healthcheck/info", contract=ResponseContract.CONTENT
    ),
    EndpointSpec(
        "device",
        "POST",
        "/api/v2/device/add",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "balanco",
        "POST",
        "/api/v2/balanco",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "catraca",
        "POST",
        "/api/v2/catraca/liberar",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "catraca",
        "POST",
        "/api/v2/catraca/gerar",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/v2/clientes/clientes",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/v2/clientes/clientes/{id}",
        sample_path="/api/v2/clientes/clientes/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "POST",
        "/api/v2/clientes/clientes",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "PUT",
        "/api/v2/clientes/clientes/{id}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/clientes/clientes/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/v2/clientes/clientes/ultima_sincronizacao/{timestamp}",
        sample_path="/api/v2/clientes/clientes/ultima_sincronizacao/0",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/v2/clientes/contato",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/v2/clientes/contato/{clienteId}",
        sample_path="/api/v2/clientes/contato/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/v2/clientes/financeiro/detalhe",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "clientes",
        "GET",
        "/api/v2/clientes/financeiro/detalhe/{clienteId}",
        sample_path="/api/v2/clientes/financeiro/detalhe/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec("empresa", "GET", "/api/v2/empresa", contract=ResponseContract.JSON_OBJECT),
    EndpointSpec(
        "empresa",
        "GET",
        "/api/v2/empresa/empresas/{page}",
        sample_path="/api/v2/empresa/empresas/1",
        query=(("per_page", "10"),),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "financeiro",
        "GET",
        "/api/v2/financeiro/forma-pagamento",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "financeiro",
        "GET",
        "/api/v2/financeiro/cartoes",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "funcionarios",
        "GET",
        "/api/v2/funcionarios",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "grupos",
        "GET",
        "/api/v2/produtos/grupos",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "movimentacao",
        "POST",
        "/api/v2/movimentacao",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "nfenfce",
        "GET",
        "/api/v2/nfenfce/serie",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "vinculos_fiscais",
        "GET",
        "/api/v2/nfenfce/vinculos-fiscais",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/v2/produtos/produtos",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "produtos",
        "PUT",
        "/api/v2/produtos/produtos/{produtoId}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/produtos/produtos/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/v2/produtos/simplificado",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/v2/produtos/compras",
        query=(("data_hora_entrada", "1970-01-01T00:00:00"), ("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/v2/produtos/deletados",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/v2/produtos/nfe-classificacao-tributaria",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "produtos",
        "GET",
        "/api/v2/produtos/produto-composicao",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "promocao",
        "GET",
        "/api/v2/produtos/promocoes",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/observacao",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/configuracao",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/mesa",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/mesa/{id}",
        sample_path="/api/v2/restaurantes/mesa/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/auth/mesa/{id}",
        sample_path="/api/v2/restaurantes/auth/mesa/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/mesa/adiantamento/{id}",
        sample_path="/api/v2/restaurantes/mesa/adiantamento/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/produto-combo",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/produto-combo/{id}",
        sample_path="/api/v2/restaurantes/produto-combo/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/mesa/{id}/concorrencia/status",
        sample_path="/api/v2/restaurantes/mesa/0/concorrencia/status",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "GET",
        "/api/v2/restaurantes/dricaia",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/v2/restaurantes/mesa",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/v2/restaurantes/mesa2",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "DELETE",
        "/api/v2/restaurantes/mesa/{id}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/restaurantes/mesa/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/v2/restaurantes/mesa/{mesa}/items",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/restaurantes/mesa/0/items",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "DELETE",
        "/api/v2/restaurantes/mesa/{mesa}/items",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/restaurantes/mesa/0/items",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "DELETE",
        "/api/v2/restaurantes/mesa/{mesa}/items/{guid}",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/restaurantes/mesa/0/items/00000000-0000-0000-0000-000000000000",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/v2/restaurantes/mesa/adiantamento",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "PATCH",
        "/api/v2/restaurantes/mesa/{id}/lacrar",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/restaurantes/mesa/0/lacrar",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "PATCH",
        "/api/v2/restaurantes/mesa/{id}/concorrencia",
        EndpointKind.DESTRUCTIVE,
        sample_path="/api/v2/restaurantes/mesa/0/concorrencia",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/v2/restaurantes/transferencia/mesa/items",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/v2/restaurantes/transferencia/mesa",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "POST",
        "/api/v2/restaurantes/mesa/aviso",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "restaurante",
        "PATCH",
        "/api/v2/restaurantes/reimpressao",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "vendas",
        "GET",
        "/api/v2/vendas/completa/{id}",
        sample_path="/api/v2/vendas/completa/0",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "vendas",
        "GET",
        "/api/v2/vendas/pre-vendas",
        query=(("page", "1"), ("per_page", "10")),
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "vendas",
        "POST",
        "/api/v2/vendas",
        EndpointKind.DESTRUCTIVE,
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "dricaia",
        "POST",
        "/api/v2/dricaia/login",
        auth="dricaia_login",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "dricaia",
        "GET",
        "/api/v2/dricaia/customer",
        auth="dricaia",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "dricaia",
        "GET",
        "/api/v2/dricaia/enterprises",
        auth="dricaia",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "dricaia",
        "GET",
        "/api/v2/dricaia/financial",
        auth="dricaia",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "dricaia",
        "GET",
        "/api/v2/dricaia/purchases",
        auth="dricaia",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "dricaia",
        "GET",
        "/api/v2/dricaia/sales",
        auth="dricaia",
        contract=ResponseContract.JSON_OBJECT,
    ),
    EndpointSpec(
        "dricaia",
        "GET",
        "/api/v2/dricaia/stock",
        auth="dricaia",
        contract=ResponseContract.JSON_OBJECT,
    ),
)


DESKTOP_ENDPOINTS = DESKTOP_V1_ENDPOINTS + DESKTOP_V2_ENDPOINTS
