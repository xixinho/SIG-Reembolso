from abc import ABC, abstractmethod
from decimal import Decimal

from apps.despesas.models import Despesa


class IDespesaRepository(ABC):
    @abstractmethod
    def obter(self, despesa_id: int) -> Despesa:
        """Levanta DespesaNaoEncontradaError se não existir."""

    @abstractmethod
    def obter_para_atualizacao(self, despesa_id: int) -> Despesa:
        """Como ``obter``, mas trava a linha até o fim da transação."""

    @abstractmethod
    def salvar(self, despesa: Despesa) -> Despesa:
        pass

    @abstractmethod
    def listar_pendentes(self) -> list[Despesa]:
        pass

    @abstractmethod
    def listar_por_coordenacao(self, coordenacao_id: int) -> list[Despesa]:
        pass

    @abstractmethod
    def listar_todas(self) -> list[Despesa]:
        pass

    @abstractmethod
    def somar_valor(self, coordenacao_id: int, status: list[str]) -> Decimal:
        """Soma o valor das despesas da coordenação nos status informados."""
