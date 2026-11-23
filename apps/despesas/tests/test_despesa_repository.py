from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase

from apps.despesas.models import Despesa
from apps.despesas.repositories.despesa_repository import DespesaRepository
from apps.despesas.repositories.historico_repository import HistoricoRepository
from apps.orcamento.models import Coordenacao
from common.enums import StatusDespesa, TipoDespesa
from common.exceptions import DespesaNaoEncontradaError


class RepositoriosDeDespesaTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("coord", password="x")
        self.a = Coordenacao.objects.create(nome="A", teto=Decimal("1000.00"))
        self.b = Coordenacao.objects.create(nome="B", teto=Decimal("500.00"))
        self.repo = DespesaRepository()

    def _despesa(self, coordenacao, valor, status=StatusDespesa.PENDENTE):
        return Despesa.objects.create(
            coordenacao=coordenacao,
            solicitante=self.usuario,
            tipo=TipoDespesa.REEMBOLSO,
            descricao="x",
            valor=Decimal(valor),
            data_compra=date(2026, 7, 1),
            beneficiario="B",
            chave_pix="k",
            comprovante="a.jpg",
            status=status,
        )

    def test_somar_valor_filtra_por_coordenacao_e_status_sem_erro_de_centavos(self):
        self._despesa(self.a, "10.10", StatusDespesa.APROVADA)
        self._despesa(self.a, "20.20", StatusDespesa.LIQUIDADA)
        self._despesa(self.a, "99.99", StatusDespesa.PENDENTE)
        self._despesa(self.a, "88.88", StatusDespesa.REJEITADA)
        self._despesa(self.b, "77.77", StatusDespesa.APROVADA)

        total = self.repo.somar_valor(
            self.a.pk, [StatusDespesa.APROVADA, StatusDespesa.LIQUIDADA]
        )

        self.assertEqual(total, Decimal("30.30"))

    def test_somar_valor_sem_despesas_devolve_zero(self):
        self.assertEqual(self.repo.somar_valor(self.a.pk, [StatusDespesa.APROVADA]), Decimal("0"))

    def test_listar_pendentes_so_traz_pendentes(self):
        pendente = self._despesa(self.a, "5.00")
        self._despesa(self.a, "6.00", StatusDespesa.APROVADA)

        self.assertEqual(self.repo.listar_pendentes(), [pendente])

    def test_obter_inexistente_levanta_erro_de_dominio(self):
        with self.assertRaises(DespesaNaoEncontradaError):
            self.repo.obter(999)

    def test_obter_para_atualizacao_funciona_dentro_de_transacao(self):
        despesa = self._despesa(self.a, "5.00")

        with transaction.atomic():
            obtida = self.repo.obter_para_atualizacao(despesa.pk)

        self.assertEqual(obtida.pk, despesa.pk)

    def test_historico_registra_e_lista_por_despesa(self):
        despesa = self._despesa(self.a, "5.00")
        historico = HistoricoRepository()

        historico.registrar(despesa, "", StatusDespesa.PENDENTE, self.usuario, "lançada")

        registros = historico.listar_por_despesa(despesa.pk)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0].observacao, "lançada")
