from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .config import Environment


class Capability(StrEnum):
    BOTH = "both"
    DESKTOP_ONLY = "desktop_only"
    RESTAURANT = "restaurant"


@dataclass(frozen=True, slots=True)
class EndpointCapability:
    method: str
    path: str
    capability: Capability
    reason: str

    def supports(self, environment: Environment, *, mesas_database_enabled: bool) -> bool:
        if self.capability is Capability.BOTH:
            return True
        if self.capability is Capability.DESKTOP_ONLY:
            return environment is Environment.DESKTOP
        return mesas_database_enabled


# Matriz inicial levantada a partir dos desvios por TipoBancoDados e usos diretos
# de ContextoRemoto. Ela deve evoluir junto com as regras de produto.
ENDPOINT_CAPABILITIES = (
    EndpointCapability("GET", "/api/v2/healthcheck", Capability.BOTH, "Infraestrutura"),
    EndpointCapability("GET", "/api/v2/healthcheck/info", Capability.BOTH, "Infraestrutura"),
    EndpointCapability("POST", "/authentication/token", Capability.BOTH, "Autenticação adaptada"),
    EndpointCapability(
        "GET", "/api/balanco", Capability.DESKTOP_ONLY, "V1 não implementada no WEB"
    ),
    EndpointCapability(
        "POST", "/api/balanco", Capability.DESKTOP_ONLY, "V1 não implementada no WEB"
    ),
    EndpointCapability(
        "GET",
        "/api/produtos/produtos/collector",
        Capability.DESKTOP_ONLY,
        "Retorna não implementado no WEB",
    ),
    EndpointCapability("GET", "/api/promocao", Capability.DESKTOP_ONLY, "Retorna data nulo no WEB"),
    EndpointCapability(
        "GET", "/api/pagamentos/clientes", Capability.DESKTOP_ONLY, "Retorna data nulo no WEB"
    ),
    EndpointCapability(
        "POST",
        "/api/financeiro/recebimentos/recebimento",
        Capability.DESKTOP_ONLY,
        "Acessa ContextoRemoto diretamente",
    ),
    EndpointCapability(
        "PUT",
        "/api/financeiro/recebimentos/recebimento",
        Capability.DESKTOP_ONLY,
        "Acessa ContextoRemoto diretamente",
    ),
    EndpointCapability(
        "GET", "/api/restaurantes/mesa", Capability.RESTAURANT, "Requer banco auxiliar de mesas"
    ),
)


DESKTOP_ONLY_PREFIXES = (
    "/api/agenda",
    "/api/assistencia",
    "/api/checklist",
    "/api/comandos",
    "/api/contas-receber",
    "/api/dricaia",
    "/api/reports",
    "/api/vendas360",
    "/painel_os",
)


def is_endpoint_supported(
    method: str,
    path: str,
    environment: Environment,
    *,
    mesas_database_enabled: bool = False,
) -> bool:
    normalized_path = "/" + path.strip("/")
    for endpoint in ENDPOINT_CAPABILITIES:
        if endpoint.method == method.upper() and endpoint.path == normalized_path:
            return endpoint.supports(environment, mesas_database_enabled=mesas_database_enabled)

    if normalized_path.startswith("/api/restaurantes"):
        return mesas_database_enabled
    if normalized_path.startswith(DESKTOP_ONLY_PREFIXES):
        return environment is Environment.DESKTOP
    return True
