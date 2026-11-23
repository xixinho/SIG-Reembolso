from django.contrib import admin

from apps.despesas.models import Despesa, HistoricoTransicaoStatus


class SomenteConsultaAdmin(admin.ModelAdmin):
    """Despesa e histórico só mudam pelos services, que aplicam RN01 a RN05;
    no admin ficam apenas para consulta."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Despesa)
class DespesaAdmin(SomenteConsultaAdmin):
    list_display = (
        "id", "tipo", "coordenacao", "solicitante", "valor", "status", "estouro", "criado_em",
    )
    list_filter = ("status", "tipo", "coordenacao", "estouro")
    search_fields = ("descricao", "beneficiario")


@admin.register(HistoricoTransicaoStatus)
class HistoricoTransicaoStatusAdmin(SomenteConsultaAdmin):
    list_display = ("despesa", "status_anterior", "status_novo", "usuario", "data_hora")
    list_filter = ("status_novo",)
