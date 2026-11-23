from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from apps.orcamento.models import Coordenacao


class FixtureCoordenacoesTests(TestCase):
    fixtures = ["coordenacoes"]

    def test_carrega_as_15_coordenacoes_com_a_soma_dos_tetos_informada(self):
        self.assertEqual(Coordenacao.objects.count(), 15)
        total = sum(c.teto for c in Coordenacao.objects.all())
        self.assertEqual(total, Decimal("194320.18"))

    def test_coordenacoes_sem_verba_tem_teto_zero(self):
        sem_verba = Coordenacao.objects.filter(teto=0).values_list("nome", flat=True)
        self.assertCountEqual(
            sem_verba,
            [
                "Captação de Recursos",
                "Financeiro / Tesouraria",
                "Coordenação Geral",
                "Inscrições e Secretaria",
                "Música e Animação",
                "Som e Iluminação",
            ],
        )

    def test_recarregar_a_fixture_nao_duplica(self):
        call_command("loaddata", "coordenacoes", verbosity=0)

        self.assertEqual(Coordenacao.objects.count(), 15)
