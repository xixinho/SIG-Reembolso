from django.db import models


class Coordenacao(models.Model):
    """Coordenação operacional do evento e o teto de verba que ela pode gastar.

    O saldo não é gravado: é derivado do teto e das despesas aprovadas e
    liquidadas, para nunca divergir do histórico.
    """

    nome = models.CharField(max_length=100, unique=True)
    teto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "coordenação"
        verbose_name_plural = "coordenações"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
