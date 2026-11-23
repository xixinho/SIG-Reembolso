from decimal import Decimal

from django.db.models import Sum

from apps.despesas.interfaces.despesa_repository import IDespesaRepository
from apps.despesas.models import Despesa
from common.enums import StatusDespesa
from common.exceptions import DespesaNaoEncontradaError


class DespesaRepository(IDespesaRepository):
    def obter(self, despesa_id: int) -> Despesa:
        return self._obter(Despesa.objects, despesa_id)

    def obter_para_atualizacao(self, despesa_id: int) -> Despesa:
        # select_for_update só vale dentro de transaction.atomic (o service abre).
        return self._obter(Despesa.objects.select_for_update(), despesa_id)

    def salvar(self, despesa: Despesa) -> Despesa:
        despesa.save()
        return despesa

    def listar_pendentes(self) -> list[Despesa]:
        pendentes = Despesa.objects.filter(status=StatusDespesa.PENDENTE)
        return list(pendentes.order_by("criado_em"))

    def listar_por_coordenacao(self, coordenacao_id: int) -> list[Despesa]:
        return list(Despesa.objects.filter(coordenacao_id=coordenacao_id))

    def listar_todas(self) -> list[Despesa]:
        return list(Despesa.objects.all())

    def somar_valor(self, coordenacao_id: int, status: list[str]) -> Decimal:
        total = Despesa.objects.filter(
            coordenacao_id=coordenacao_id, status__in=status
        ).aggregate(total=Sum("valor"))["total"]
        return total or Decimal("0")

    @staticmethod
    def _obter(consulta, despesa_id: int) -> Despesa:
        try:
            return consulta.get(pk=despesa_id)
        except Despesa.DoesNotExist as erro:
            raise DespesaNaoEncontradaError(
                f"Despesa {despesa_id} não encontrada."
            ) from erro
