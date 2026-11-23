from django.contrib import admin

from apps.orcamento.models import Coordenacao


@admin.register(Coordenacao)
class CoordenacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "teto")
    search_fields = ("nome",)
