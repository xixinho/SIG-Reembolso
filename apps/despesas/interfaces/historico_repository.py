from abc import ABC, abstractmethod

from apps.despesas.models import Despesa, HistoricoTransicaoStatus


class IHistoricoRepository(ABC):
    @abstractmethod
    def registrar(
        self,
        despesa: Despesa,
        status_anterior: str,
        status_novo: str,
        usuario,
        observacao: str = "",
    ) -> HistoricoTransicaoStatus:
        pass

    @abstractmethod
    def listar_por_despesa(self, despesa_id: int) -> list[HistoricoTransicaoStatus]:
        pass
