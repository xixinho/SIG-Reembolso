from decimal import Decimal

from apps.despesas.interfaces.despesa_repository import IDespesaRepository
from apps.orcamento.interfaces.coordenacao_repository import ICoordenacaoRepository
from apps.orcamento.interfaces.orcamento_service import IOrcamentoService
from common.enums import StatusDespesa

# Despesas que já abatem o teto: pendentes, rejeitadas e canceladas não contam.
STATUS_COMPROMETIDOS = [StatusDespesa.APROVADA, StatusDespesa.LIQUIDADA]


class OrcamentoService(IOrcamentoService):
    def __init__(
        self,
        coordenacoes: ICoordenacaoRepository,
        despesas: IDespesaRepository,
    ):
        self._coordenacoes = coordenacoes
        self._despesas = despesas

    def calcular_saldo(self, coordenacao_id: int) -> Decimal:
        coordenacao = self._coordenacoes.obter(coordenacao_id)
        gasto = self._despesas.somar_valor(coordenacao_id, STATUS_COMPROMETIDOS)
        return coordenacao.teto - gasto

    def verificar_estouro(self, coordenacao_id: int, valor: Decimal) -> bool:
        return valor > self.calcular_saldo(coordenacao_id)
