from django.conf import settings
from django.db import models

from common.enums import StatusDespesa, TipoDespesa


class Despesa(models.Model):
    """Reembolso, adiantamento ou fundo de caixa lançado por uma coordenação.

    Os três tipos seguem o mesmo fluxo. As regras de negócio (comprovante
    obrigatório, parecer na rejeição, segregação de funções, imutabilidade após
    aprovação, estouro de saldo) e as transições de status ficam em
    ``services.py``, não aqui.
    """

    coordenacao = models.ForeignKey(
        "orcamento.Coordenacao",
        on_delete=models.PROTECT,
        related_name="despesas",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="despesas_solicitadas",
    )
    tipo = models.CharField(max_length=20, choices=TipoDespesa.choices)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_compra = models.DateField()
    beneficiario = models.CharField(max_length=150)
    chave_pix = models.CharField(max_length=100)
    comprovante = models.ImageField(upload_to="comprovantes/%Y/%m/")
    status = models.CharField(
        max_length=20,
        choices=StatusDespesa.choices,
        default=StatusDespesa.PENDENTE,
    )
    parecer = models.TextField(blank=True)
    estouro = models.BooleanField(default=False)
    justificativa_estouro = models.TextField(blank=True)
    comprovante_pagamento = models.ImageField(
        upload_to="comprovantes_pagamento/%Y/%m/",
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.pk} - {self.coordenacao}"


class HistoricoTransicaoStatus(models.Model):
    """Trilha de auditoria: quem mudou o status da despesa, de quê para quê.

    Só recebe registros novos; edição e exclusão são recusadas.
    """

    despesa = models.ForeignKey(
        Despesa,
        on_delete=models.PROTECT,
        related_name="historico",
    )
    status_anterior = models.CharField(
        max_length=20,
        choices=StatusDespesa.choices,
        blank=True,
    )
    status_novo = models.CharField(max_length=20, choices=StatusDespesa.choices)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transicoes_realizadas",
    )
    data_hora = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "histórico de transição de status"
        verbose_name_plural = "histórico de transições de status"
        ordering = ["data_hora"]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise PermissionError("O histórico de transições é imutável.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("O histórico de transições é imutável.")

    def __str__(self):
        return f"{self.despesa_id}: {self.status_anterior or '-'} -> {self.status_novo}"
