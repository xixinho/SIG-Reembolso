"""Raiz de composição: monta services e repositories (equivalente ao
``ConfigureServices`` do ``Program.cs`` do SmartRules)."""
from apps.accounts.interfaces.acesso_service import IAcessoService
from apps.accounts.services.acesso_service import AcessoService
from apps.despesas.interfaces.despesa_service import IDespesaService
from apps.despesas.repositories.despesa_repository import DespesaRepository
from apps.despesas.repositories.historico_repository import HistoricoRepository
from apps.despesas.services.despesa_service import DespesaService
from apps.orcamento.interfaces.orcamento_service import IOrcamentoService
from apps.orcamento.repositories.coordenacao_repository import CoordenacaoRepository
from apps.orcamento.services.orcamento_service import OrcamentoService


def montar_acesso_service() -> IAcessoService:
    return AcessoService()


def montar_orcamento_service() -> IOrcamentoService:
    return OrcamentoService(CoordenacaoRepository(), DespesaRepository())


def montar_despesa_service() -> IDespesaService:
    return DespesaService(
        DespesaRepository(),
        HistoricoRepository(),
        montar_orcamento_service(),
        montar_acesso_service(),
    )
