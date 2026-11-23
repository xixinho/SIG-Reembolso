"""Dublês em memória das interfaces, para testar os services sem banco
(o papel do Moq nos testes do SmartRules)."""
from decimal import Decimal
from types import SimpleNamespace

from apps.accounts.interfaces.acesso_service import IAcessoService
from apps.despesas.interfaces.despesa_repository import IDespesaRepository
from apps.despesas.interfaces.historico_repository import IHistoricoRepository
from apps.orcamento.interfaces.coordenacao_repository import ICoordenacaoRepository
from apps.orcamento.interfaces.orcamento_service import IOrcamentoService
from common.enums import Perfil
from common.exceptions import DespesaNaoEncontradaError, PermissaoNegadaError


def usuario(usuario_id: int):
    return SimpleNamespace(id=usuario_id)


class FakeDespesaRepository(IDespesaRepository):
    def __init__(self):
        self.itens = {}
        self.soma = Decimal("0")
        self.status_consultados = None
        self._proximo = 1

    def obter(self, despesa_id):
        try:
            return self.itens[despesa_id]
        except KeyError as erro:
            raise DespesaNaoEncontradaError(str(despesa_id)) from erro

    def obter_para_atualizacao(self, despesa_id):
        return self.obter(despesa_id)

    def salvar(self, despesa):
        if despesa.pk is None:
            despesa.pk = self._proximo
            self._proximo += 1
        self.itens[despesa.pk] = despesa
        return despesa

    def listar_pendentes(self):
        return [d for d in self.itens.values() if d.status == "PENDENTE"]

    def listar_por_coordenacao(self, coordenacao_id):
        return [d for d in self.itens.values() if d.coordenacao_id == coordenacao_id]

    def listar_todas(self):
        return list(self.itens.values())

    def somar_valor(self, coordenacao_id, status):
        self.status_consultados = list(status)
        return self.soma


class FakeHistoricoRepository(IHistoricoRepository):
    def __init__(self):
        self.registros = []

    def registrar(self, despesa, status_anterior, status_novo, usuario, observacao=""):
        registro = SimpleNamespace(
            despesa=despesa,
            status_anterior=status_anterior,
            status_novo=status_novo,
            usuario=usuario,
            observacao=observacao,
        )
        self.registros.append(registro)
        return registro

    def listar_por_despesa(self, despesa_id):
        return [r for r in self.registros if r.despesa.pk == despesa_id]


class FakeAcessoService(IAcessoService):
    """``perfis`` mapeia o id do usuário para (Perfil, coordenacao_id)."""

    def __init__(self, perfis):
        self._perfis = perfis

    def perfil_de(self, usuario):
        try:
            return self._perfis[usuario.id][0]
        except KeyError as erro:
            raise PermissaoNegadaError("Usuário sem perfil de acesso.") from erro

    def coordenacao_id_de(self, usuario):
        self.perfil_de(usuario)
        return self._perfis[usuario.id][1]

    def pode_lancar(self, usuario):
        return self.perfil_de(usuario) in (Perfil.COORDENADOR, Perfil.TESOURARIA)

    def pode_triar(self, usuario):
        return self.perfil_de(usuario) == Perfil.TESOURARIA

    def pode_consultar_tudo(self, usuario):
        return self.perfil_de(usuario) in (Perfil.TESOURARIA, Perfil.ADMINISTRADOR)


class FakeOrcamentoService(IOrcamentoService):
    def __init__(self, estouro=False):
        self.estouro = estouro

    def calcular_saldo(self, coordenacao_id):
        return Decimal("0")

    def verificar_estouro(self, coordenacao_id, valor):
        return self.estouro


class FakeCoordenacaoRepository(ICoordenacaoRepository):
    def __init__(self, teto):
        self._teto = teto

    def obter(self, coordenacao_id):
        return SimpleNamespace(id=coordenacao_id, teto=self._teto)

    def listar(self):
        return []
