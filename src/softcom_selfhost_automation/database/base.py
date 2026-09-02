from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class DatabaseAdapter(ABC):
    """Contrato mínimo para preparação e conferência auxiliar de dados."""

    @abstractmethod
    def fetch_one(self, statement: str, parameters: Mapping[str, Any]) -> Mapping[str, Any] | None:
        """Retorna uma linha sem expor detalhes do driver ao teste."""

    @abstractmethod
    def execute(self, statement: str, parameters: Mapping[str, Any]) -> None:
        """Executa uma alteração explicitamente parametrizada."""

    @abstractmethod
    def close(self) -> None:
        """Libera as conexões mantidas pelo adaptador."""
