from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import PerfilUsuario
from apps.accounts.services.acesso_service import AcessoService
from apps.orcamento.models import Coordenacao
from common.enums import Perfil
from common.exceptions import PermissaoNegadaError


class AcessoServiceTests(TestCase):
    def setUp(self):
        self.coordenacao = Coordenacao.objects.create(nome="Cozinha", teto=Decimal("100.00"))
        self.service = AcessoService()

    def _usuario(self, nome, perfil, coordenacao=None):
        usuario = get_user_model().objects.create_user(nome, password="x")
        PerfilUsuario.objects.create(usuario=usuario, perfil=perfil, coordenacao=coordenacao)
        return usuario

    def test_coordenador_lanca_mas_nao_tria_nem_consulta_tudo(self):
        u = self._usuario("c", Perfil.COORDENADOR, self.coordenacao)

        self.assertTrue(self.service.pode_lancar(u))
        self.assertFalse(self.service.pode_triar(u))
        self.assertFalse(self.service.pode_consultar_tudo(u))
        self.assertEqual(self.service.coordenacao_id_de(u), self.coordenacao.pk)

    def test_tesouraria_lanca_tria_e_consulta_tudo(self):
        u = self._usuario("t", Perfil.TESOURARIA, self.coordenacao)

        self.assertTrue(self.service.pode_lancar(u))
        self.assertTrue(self.service.pode_triar(u))
        self.assertTrue(self.service.pode_consultar_tudo(u))

    def test_administrador_so_consulta(self):
        u = self._usuario("a", Perfil.ADMINISTRADOR)

        self.assertFalse(self.service.pode_lancar(u))
        self.assertFalse(self.service.pode_triar(u))
        self.assertTrue(self.service.pode_consultar_tudo(u))
        self.assertIsNone(self.service.coordenacao_id_de(u))

    def test_usuario_sem_perfil_e_negado(self):
        u = get_user_model().objects.create_user("sem", password="x")

        with self.assertRaises(PermissaoNegadaError):
            self.service.perfil_de(u)

    def test_coordenador_e_tesouraria_exigem_coordenacao(self):
        u = get_user_model().objects.create_user("x", password="x")

        for perfil in (Perfil.COORDENADOR, Perfil.TESOURARIA):
            with self.assertRaises(ValidationError):
                PerfilUsuario(usuario=u, perfil=perfil).full_clean(exclude=["usuario"])

        PerfilUsuario(usuario=u, perfil=Perfil.ADMINISTRADOR).full_clean(exclude=["usuario"])
