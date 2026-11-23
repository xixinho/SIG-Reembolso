from apps.despesas.interfaces.historico_repository import IHistoricoRepository
from apps.despesas.models import Despesa, HistoricoTransicaoStatus


class HistoricoRepository(IHistoricoRepository):
    def registrar(
        self,
        despesa: Despesa,
        status_anterior: str,
        status_novo: str,
        usuario,
        observacao: str = "",
    ) -> HistoricoTransicaoStatus:
        return HistoricoTransicaoStatus.objects.create(
            despesa=despesa,
            status_anterior=status_anterior,
            status_novo=status_novo,
            usuario=usuario,
            observacao=observacao,
        )

    def listar_por_despesa(self, despesa_id: int) -> list[HistoricoTransicaoStatus]:
        return list(HistoricoTransicaoStatus.objects.filter(despesa_id=despesa_id))
