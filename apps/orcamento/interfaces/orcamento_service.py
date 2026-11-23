from abc import ABC, abstractmethod
from decimal import Decimal


class IOrcamentoService(ABC):
    @abstractmethod
    def calcular_saldo(self, coordenacao_id: int) -> Decimal:
        """Teto menos as despesas aprovadas e liquidadas."""

    @abstractmethod
    def verificar_estouro(self, coordenacao_id: int, valor: Decimal) -> bool:
        """True se o valor ultrapassa o saldo atual da coordenação."""
