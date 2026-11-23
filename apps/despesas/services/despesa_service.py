from django.db import transaction

from apps.accounts.interfaces.acesso_service import IAcessoService
from apps.despesas.interfaces.despesa_repository import IDespesaRepository
from apps.despesas.interfaces.despesa_service import IDespesaService
from apps.despesas.interfaces.historico_repository import IHistoricoRepository
from apps.despesas.models import Despesa
from apps.orcamento.interfaces.orcamento_service import IOrcamentoService
from common.dtos import DadosDespesa
from common.enums import StatusDespesa
from common.exceptions import (
    ComprovanteObrigatorioError,
    DespesaImutavelError,
    JustificativaEstouroObrigatoriaError,
    ParecerObrigatorioError,
    PermissaoNegadaError,
    SegregacaoDeFuncoesError,
    TransicaoInvalidaError,
)

CAMPOS_EDITAVEIS = ("tipo", "descricao", "valor", "data_compra", "beneficiario", "chave_pix")


class DespesaService(IDespesaService):
    def __init__(
        self,
        despesas: IDespesaRepository,
        historico: IHistoricoRepository,
        orcamento: IOrcamentoService,
        acesso: IAcessoService,
    ):
        self._despesas = despesas
        self._historico = historico
        self._orcamento = orcamento
        self._acesso = acesso

    def lancar(self, dados: DadosDespesa, solicitante) -> Despesa:
        if not self._acesso.pode_lancar(solicitante):
            raise PermissaoNegadaError("Este perfil não pode lançar despesas.")
        coordenacao_id = self._acesso.coordenacao_id_de(solicitante)
        if coordenacao_id is None:
            raise PermissaoNegadaError("Usuário sem coordenação.")
        if not dados.comprovante:
            raise ComprovanteObrigatorioError("O comprovante fiscal é obrigatório.")

        despesa = Despesa(
            coordenacao_id=coordenacao_id,
            solicitante_id=solicitante.id,
            tipo=dados.tipo,
            descricao=dados.descricao,
            valor=dados.valor,
            data_compra=dados.data_compra,
            beneficiario=dados.beneficiario,
            chave_pix=dados.chave_pix,
            comprovante=dados.comprovante,
        )
        with transaction.atomic():
            self._despesas.salvar(despesa)
            self._historico.registrar(
                despesa, "", StatusDespesa.PENDENTE, solicitante, "Despesa lançada."
            )
        return despesa

    def editar(self, despesa_id: int, usuario, dados: DadosDespesa) -> Despesa:
        with transaction.atomic():
            despesa = self._despesas.obter_para_atualizacao(despesa_id)
            self._exigir_solicitante_e_pendente(despesa, usuario)

            alterados = [
                campo for campo in CAMPOS_EDITAVEIS
                if getattr(despesa, campo) != getattr(dados, campo)
            ]
            if dados.comprovante is not None:
                alterados.append("comprovante")
            if not alterados:
                return despesa

            for campo in CAMPOS_EDITAVEIS:
                setattr(despesa, campo, getattr(dados, campo))
            if dados.comprovante is not None:
                despesa.comprovante = dados.comprovante
            self._despesas.salvar(despesa)
            self._historico.registrar(
                despesa,
                StatusDespesa.PENDENTE,
                StatusDespesa.PENDENTE,
                usuario,
                "Editada: " + ", ".join(alterados),
            )
        return despesa

    def cancelar(self, despesa_id: int, usuario) -> Despesa:
        with transaction.atomic():
            despesa = self._despesas.obter_para_atualizacao(despesa_id)
            self._exigir_solicitante_e_pendente(despesa, usuario)
            despesa.status = StatusDespesa.CANCELADA
            self._despesas.salvar(despesa)
            self._historico.registrar(
                despesa, StatusDespesa.PENDENTE, StatusDespesa.CANCELADA, usuario
            )
        return despesa

    def aprovar(
        self,
        despesa_id: int,
        usuario,
        justificativa_estouro: str | None = None,
    ) -> Despesa:
        self._exigir_triagem(usuario)
        with transaction.atomic():
            despesa = self._despesas.obter_para_atualizacao(despesa_id)
            self._exigir_outro_usuario(despesa, usuario)
            self._exigir_status(despesa, StatusDespesa.PENDENTE)

            justificativa = (justificativa_estouro or "").strip()
            estouro = self._orcamento.verificar_estouro(
                despesa.coordenacao_id, despesa.valor
            )
            if estouro and not justificativa:
                raise JustificativaEstouroObrigatoriaError(
                    "A despesa ultrapassa o saldo da coordenação: informe a justificativa."
                )

            despesa.estouro = estouro
            despesa.justificativa_estouro = justificativa if estouro else ""
            despesa.status = StatusDespesa.APROVADA
            self._despesas.salvar(despesa)
            self._historico.registrar(
                despesa,
                StatusDespesa.PENDENTE,
                StatusDespesa.APROVADA,
                usuario,
                despesa.justificativa_estouro,
            )
        return despesa

    def rejeitar(self, despesa_id: int, usuario, parecer: str) -> Despesa:
        self._exigir_triagem(usuario)
        parecer = (parecer or "").strip()
        if not parecer:
            raise ParecerObrigatorioError("A rejeição exige um parecer.")
        with transaction.atomic():
            despesa = self._despesas.obter_para_atualizacao(despesa_id)
            self._exigir_outro_usuario(despesa, usuario)
            self._exigir_status(despesa, StatusDespesa.PENDENTE)

            despesa.parecer = parecer
            despesa.status = StatusDespesa.REJEITADA
            self._despesas.salvar(despesa)
            self._historico.registrar(
                despesa, StatusDespesa.PENDENTE, StatusDespesa.REJEITADA, usuario, parecer
            )
        return despesa

    def liquidar(self, despesa_id: int, usuario, comprovante_pagamento) -> Despesa:
        self._exigir_triagem(usuario)
        if not comprovante_pagamento:
            raise ComprovanteObrigatorioError(
                "O comprovante do pagamento é obrigatório para liquidar."
            )
        with transaction.atomic():
            despesa = self._despesas.obter_para_atualizacao(despesa_id)
            self._exigir_outro_usuario(despesa, usuario)
            self._exigir_status(despesa, StatusDespesa.APROVADA)

            despesa.comprovante_pagamento = comprovante_pagamento
            despesa.status = StatusDespesa.LIQUIDADA
            self._despesas.salvar(despesa)
            self._historico.registrar(
                despesa, StatusDespesa.APROVADA, StatusDespesa.LIQUIDADA, usuario
            )
        return despesa

    def fila_triagem(self, usuario) -> list[Despesa]:
        self._exigir_triagem(usuario)
        return self._despesas.listar_pendentes()

    def extrato(self, usuario, coordenacao_id: int | None = None) -> list[Despesa]:
        if self._acesso.pode_consultar_tudo(usuario):
            if coordenacao_id is None:
                return self._despesas.listar_todas()
            return self._despesas.listar_por_coordenacao(coordenacao_id)

        propria = self._acesso.coordenacao_id_de(usuario)
        if propria is None or coordenacao_id not in (None, propria):
            raise PermissaoNegadaError("Você só pode ver o extrato da sua coordenação.")
        return self._despesas.listar_por_coordenacao(propria)

    def _exigir_triagem(self, usuario) -> None:
        if not self._acesso.pode_triar(usuario):
            raise PermissaoNegadaError("Somente a Tesouraria pode executar esta ação.")

    @staticmethod
    def _exigir_outro_usuario(despesa: Despesa, usuario) -> None:
        if despesa.solicitante_id == usuario.id:
            raise SegregacaoDeFuncoesError(
                "Quem lançou a despesa não pode decidir sobre ela."
            )

    @staticmethod
    def _exigir_status(despesa: Despesa, esperado: StatusDespesa) -> None:
        if despesa.status != esperado:
            raise TransicaoInvalidaError(
                f"A despesa está {despesa.status}; esperado {esperado}."
            )

    @staticmethod
    def _exigir_solicitante_e_pendente(despesa: Despesa, usuario) -> None:
        if despesa.solicitante_id != usuario.id:
            raise PermissaoNegadaError("Só quem lançou a despesa pode alterá-la.")
        if despesa.status != StatusDespesa.PENDENTE:
            raise DespesaImutavelError(
                "Depois de aprovada, rejeitada ou cancelada, a despesa não pode ser alterada."
            )
