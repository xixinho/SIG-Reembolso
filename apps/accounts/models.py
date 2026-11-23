from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from common.enums import Perfil


class PerfilUsuario(models.Model):
    """Perfil de acesso do usuário e a coordenação a que ele pertence.

    Coordenador e Tesouraria lançam despesas e por isso exigem coordenação.
    O Administrador só consulta e não pertence a nenhuma.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_usuario",
    )
    perfil = models.CharField(max_length=20, choices=Perfil.choices)
    coordenacao = models.ForeignKey(
        "orcamento.Coordenacao",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    class Meta:
        verbose_name = "perfil de usuário"
        verbose_name_plural = "perfis de usuário"

    def clean(self):
        exige = self.perfil in (Perfil.COORDENADOR, Perfil.TESOURARIA)
        if exige and self.coordenacao_id is None:
            raise ValidationError({"coordenacao": "Este perfil exige uma coordenação."})

    def __str__(self):
        return f"{self.usuario} ({self.get_perfil_display()})"
