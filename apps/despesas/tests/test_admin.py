from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser("adm", password="x")
        self.client.force_login(admin)

    def test_listagens_abrem(self):
        for nome in (
            "orcamento_coordenacao",
            "accounts_perfilusuario",
            "despesas_despesa",
            "despesas_historicotransicaostatus",
        ):
            resposta = self.client.get(reverse(f"admin:{nome}_changelist"))
            self.assertEqual(resposta.status_code, 200, nome)

    def test_coordenacao_e_perfil_podem_ser_criados_pelo_admin(self):
        for nome in ("orcamento_coordenacao", "accounts_perfilusuario"):
            resposta = self.client.get(reverse(f"admin:{nome}_add"))
            self.assertEqual(resposta.status_code, 200, nome)

    def test_despesa_e_historico_nao_podem_ser_criados_pelo_admin(self):
        for nome in ("despesas_despesa", "despesas_historicotransicaostatus"):
            resposta = self.client.get(reverse(f"admin:{nome}_add"))
            self.assertEqual(resposta.status_code, 403, nome)
