from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.despesas.services.despesa_service import DespesaService
from apps.despesas.tests.fakes import (
    FakeAcessoService,
    FakeDespesaRepository,
    FakeHistoricoRepository,
    FakeOrcamentoService,
    usuario,
)
from common.dtos import DadosDespesa
from common.enums import Perfil, StatusDespesa, TipoDespesa
from common.exceptions import (
    ComprovanteObrigatorioError,
    DespesaImutavelError,
    JustificativaEstouroObrigatoriaError,
    ParecerObrigatorioError,
    PermissaoNegadaError,
    SegregacaoDeFuncoesError,
    TransicaoInvalidaError,
)


def dados(**mudancas):
    base = dict(
        tipo=TipoDespesa.REEMBOLSO,
        descricao="Gás de cozinha",
        valor=Decimal("50.00"),
        data_compra=date(2026, 7, 1),
        beneficiario="Maria",
        chave_pix="maria@exemplo.com",
        comprovante="nota.jpg",
    )
    base.update(mudancas)
    return DadosDespesa(**base)


class DespesaServiceTests(TestCase):
    def setUp(self):
        self.despesas = FakeDespesaRepository()
        self.historico = FakeHistoricoRepository()
        self.orcamento = FakeOrcamentoService()
        self.acesso = FakeAcessoService({
            1: (Perfil.COORDENADOR, 10),
            2: (Perfil.COORDENADOR, 20),
            3: (Perfil.TESOURARIA, 30),
            4: (Perfil.TESOURARIA, 30),
            5: (Perfil.ADMINISTRADOR, None),
        })
        self.service = DespesaService(
            self.despesas, self.historico, self.orcamento, self.acesso
        )
        self.coordenador = usuario(1)
        self.outro_coordenador = usuario(2)
        self.tesoureiro = usuario(3)
        self.outro_tesoureiro = usuario(4)
        self.administrador = usuario(5)

    def _lancar(self, solicitante=None, **mudancas):
        return self.service.lancar(dados(**mudancas), solicitante or self.coordenador)

    # --- lançar (RN01) -----------------------------------------------------

    def test_lancar_cria_despesa_pendente_na_coordenacao_do_solicitante(self):
        despesa = self._lancar()

        self.assertEqual(despesa.status, StatusDespesa.PENDENTE)
        self.assertEqual(despesa.coordenacao_id, 10)
        self.assertEqual(despesa.solicitante_id, 1)
        registro = self.historico.registros[0]
        self.assertEqual(registro.status_anterior, "")
        self.assertEqual(registro.status_novo, StatusDespesa.PENDENTE)

    def test_lancar_sem_comprovante_e_recusado_e_nada_e_gravado(self):
        with self.assertRaises(ComprovanteObrigatorioError):
            self._lancar(comprovante=None)

        self.assertEqual(self.despesas.itens, {})
        self.assertEqual(self.historico.registros, [])

    def test_tesoureiro_pode_lancar_na_propria_coordenacao(self):
        despesa = self._lancar(solicitante=self.tesoureiro)

        self.assertEqual(despesa.coordenacao_id, 30)

    def test_administrador_nao_pode_lancar(self):
        with self.assertRaises(PermissaoNegadaError):
            self._lancar(solicitante=self.administrador)

    # --- editar e cancelar (RN05) ------------------------------------------

    def test_editar_registra_historico_pendente_para_pendente(self):
        despesa = self._lancar()

        self.service.editar(
            despesa.pk, self.coordenador, dados(valor=Decimal("75.00"), comprovante=None)
        )

        self.assertEqual(despesa.valor, Decimal("75.00"))
        registro = self.historico.registros[-1]
        self.assertEqual(registro.status_anterior, StatusDespesa.PENDENTE)
        self.assertEqual(registro.status_novo, StatusDespesa.PENDENTE)
        self.assertEqual(registro.observacao, "Editada: valor")

    def test_editar_sem_alteracao_nao_registra_historico(self):
        despesa = self._lancar()

        self.service.editar(despesa.pk, self.coordenador, dados(comprovante=None))

        self.assertEqual(len(self.historico.registros), 1)

    def test_editar_despesa_de_outro_usuario_e_recusado(self):
        despesa = self._lancar()

        with self.assertRaises(PermissaoNegadaError):
            self.service.editar(despesa.pk, self.outro_coordenador, dados(comprovante=None))

    def test_editar_depois_de_aprovada_e_recusado(self):
        despesa = self._lancar()
        self.service.aprovar(despesa.pk, self.tesoureiro)

        with self.assertRaises(DespesaImutavelError):
            self.service.editar(
                despesa.pk, self.coordenador, dados(valor=Decimal("1.00"), comprovante=None)
            )
        self.assertEqual(despesa.valor, Decimal("50.00"))

    def test_cancelar_pendente(self):
        despesa = self._lancar()

        self.service.cancelar(despesa.pk, self.coordenador)

        self.assertEqual(despesa.status, StatusDespesa.CANCELADA)
        self.assertEqual(self.historico.registros[-1].status_novo, StatusDespesa.CANCELADA)

    def test_cancelar_depois_de_aprovada_e_recusado(self):
        despesa = self._lancar()
        self.service.aprovar(despesa.pk, self.tesoureiro)

        with self.assertRaises(DespesaImutavelError):
            self.service.cancelar(despesa.pk, self.coordenador)
        self.assertEqual(despesa.status, StatusDespesa.APROVADA)

    # --- aprovar (RN02, RN03) ----------------------------------------------

    def test_aprovar_sem_estouro(self):
        despesa = self._lancar()

        self.service.aprovar(despesa.pk, self.tesoureiro)

        self.assertEqual(despesa.status, StatusDespesa.APROVADA)
        self.assertFalse(despesa.estouro)
        self.assertEqual(self.historico.registros[-1].usuario, self.tesoureiro)

    def test_aprovar_com_estouro_exige_justificativa_e_nao_altera_a_despesa(self):
        self.orcamento.estouro = True
        despesa = self._lancar()

        with self.assertRaises(JustificativaEstouroObrigatoriaError):
            self.service.aprovar(despesa.pk, self.tesoureiro, "   ")

        self.assertEqual(despesa.status, StatusDespesa.PENDENTE)
        self.assertFalse(despesa.estouro)

    def test_aprovar_com_estouro_e_justificativa_marca_estouro(self):
        self.orcamento.estouro = True
        despesa = self._lancar()

        self.service.aprovar(despesa.pk, self.tesoureiro, "Compra emergencial de remédio")

        self.assertEqual(despesa.status, StatusDespesa.APROVADA)
        self.assertTrue(despesa.estouro)
        self.assertEqual(despesa.justificativa_estouro, "Compra emergencial de remédio")

    def test_tesoureiro_nao_aprova_a_propria_despesa(self):
        despesa = self._lancar(solicitante=self.tesoureiro)

        with self.assertRaises(SegregacaoDeFuncoesError):
            self.service.aprovar(despesa.pk, self.tesoureiro)

        self.service.aprovar(despesa.pk, self.outro_tesoureiro)
        self.assertEqual(despesa.status, StatusDespesa.APROVADA)

    def test_coordenador_nao_aprova(self):
        despesa = self._lancar()

        with self.assertRaises(PermissaoNegadaError):
            self.service.aprovar(despesa.pk, self.outro_coordenador)

    def test_aprovar_duas_vezes_e_transicao_invalida(self):
        despesa = self._lancar()
        self.service.aprovar(despesa.pk, self.tesoureiro)

        with self.assertRaises(TransicaoInvalidaError):
            self.service.aprovar(despesa.pk, self.outro_tesoureiro)

    # --- rejeitar (RN03, RN04) ---------------------------------------------

    def test_rejeitar_sem_parecer_e_recusado(self):
        despesa = self._lancar()

        with self.assertRaises(ParecerObrigatorioError):
            self.service.rejeitar(despesa.pk, self.tesoureiro, "  ")

        self.assertEqual(despesa.status, StatusDespesa.PENDENTE)

    def test_rejeitar_com_parecer(self):
        despesa = self._lancar()

        self.service.rejeitar(despesa.pk, self.tesoureiro, "Nota ilegível")

        self.assertEqual(despesa.status, StatusDespesa.REJEITADA)
        self.assertEqual(despesa.parecer, "Nota ilegível")
        self.assertEqual(self.historico.registros[-1].observacao, "Nota ilegível")

    def test_tesoureiro_nao_rejeita_a_propria_despesa(self):
        despesa = self._lancar(solicitante=self.tesoureiro)

        with self.assertRaises(SegregacaoDeFuncoesError):
            self.service.rejeitar(despesa.pk, self.tesoureiro, "motivo")

    # --- liquidar ----------------------------------------------------------

    def test_liquidar_despesa_aprovada(self):
        despesa = self._lancar()
        self.service.aprovar(despesa.pk, self.tesoureiro)

        self.service.liquidar(despesa.pk, self.outro_tesoureiro, "pix.jpg")

        self.assertEqual(despesa.status, StatusDespesa.LIQUIDADA)
        self.assertEqual(despesa.comprovante_pagamento, "pix.jpg")

    def test_liquidar_pendente_e_transicao_invalida(self):
        despesa = self._lancar()

        with self.assertRaises(TransicaoInvalidaError):
            self.service.liquidar(despesa.pk, self.tesoureiro, "pix.jpg")

    def test_liquidar_sem_comprovante_de_pagamento_e_recusado(self):
        despesa = self._lancar()
        self.service.aprovar(despesa.pk, self.tesoureiro)

        with self.assertRaises(ComprovanteObrigatorioError):
            self.service.liquidar(despesa.pk, self.outro_tesoureiro, None)

        self.assertEqual(despesa.status, StatusDespesa.APROVADA)

    def test_tesoureiro_nao_liquida_a_propria_despesa(self):
        despesa = self._lancar(solicitante=self.tesoureiro)
        self.service.aprovar(despesa.pk, self.outro_tesoureiro)

        with self.assertRaises(SegregacaoDeFuncoesError):
            self.service.liquidar(despesa.pk, self.tesoureiro, "pix.jpg")

    # --- consultas ---------------------------------------------------------

    def test_fila_de_triagem_so_para_a_tesouraria(self):
        despesa = self._lancar()

        self.assertEqual(self.service.fila_triagem(self.tesoureiro), [despesa])
        with self.assertRaises(PermissaoNegadaError):
            self.service.fila_triagem(self.coordenador)
        with self.assertRaises(PermissaoNegadaError):
            self.service.fila_triagem(self.administrador)

    def test_extrato_do_coordenador_e_so_da_propria_coordenacao(self):
        minha = self._lancar()
        self._lancar(solicitante=self.outro_coordenador)

        self.assertEqual(self.service.extrato(self.coordenador), [minha])
        with self.assertRaises(PermissaoNegadaError):
            self.service.extrato(self.coordenador, coordenacao_id=20)

    def test_administrador_e_tesouraria_veem_todas_as_coordenacoes(self):
        a = self._lancar()
        b = self._lancar(solicitante=self.outro_coordenador)

        self.assertCountEqual(self.service.extrato(self.administrador), [a, b])
        self.assertCountEqual(self.service.extrato(self.tesoureiro), [a, b])
        self.assertEqual(self.service.extrato(self.administrador, coordenacao_id=20), [b])
