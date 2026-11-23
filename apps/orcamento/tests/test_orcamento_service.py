from decimal import Decimal

from django.test import SimpleTestCase

from apps.despesas.tests.fakes import FakeCoordenacaoRepository, FakeDespesaRepository
from apps.orcamento.services.orcamento_service import OrcamentoService
from common.enums import StatusDespesa


class OrcamentoServiceTests(SimpleTestCase):
    def setUp(self):
        self.despesas = FakeDespesaRepository()
        self.despesas.soma = Decimal("300.00")
        self.service = OrcamentoService(
            FakeCoordenacaoRepository(Decimal("1000.00")), self.despesas
        )

    def test_saldo_e_teto_menos_aprovadas_e_liquidadas(self):
        self.assertEqual(self.service.calcular_saldo(1), Decimal("700.00"))
        self.assertEqual(
            self.despesas.status_consultados,
            [StatusDespesa.APROVADA, StatusDespesa.LIQUIDADA],
        )

    def test_valor_igual_ao_saldo_nao_e_estouro(self):
        self.assertFalse(self.service.verificar_estouro(1, Decimal("700.00")))

    def test_valor_acima_do_saldo_e_estouro_por_um_centavo(self):
        self.assertTrue(self.service.verificar_estouro(1, Decimal("700.01")))
