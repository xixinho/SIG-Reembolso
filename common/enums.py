from django.db import models


class TipoDespesa(models.TextChoices):
    REEMBOLSO = "REEMBOLSO", "Reembolso"
    ADIANTAMENTO = "ADIANTAMENTO", "Adiantamento"
    FUNDO_DE_CAIXA = "FUNDO_DE_CAIXA", "Fundo de caixa"


class StatusDespesa(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    APROVADA = "APROVADA", "Aprovada"
    REJEITADA = "REJEITADA", "Rejeitada"
    LIQUIDADA = "LIQUIDADA", "Liquidada"
    CANCELADA = "CANCELADA", "Cancelada"


class Perfil(models.TextChoices):
    COORDENADOR = "COORDENADOR", "Coordenador"
    TESOURARIA = "TESOURARIA", "Tesouraria"
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
