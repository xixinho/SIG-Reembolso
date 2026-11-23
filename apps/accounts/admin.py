from django.contrib import admin

from apps.accounts.models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "perfil", "coordenacao")
    list_filter = ("perfil", "coordenacao")
    search_fields = ("usuario__username",)
