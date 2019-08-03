from django.contrib import admin

from .models import Membro


class MembroAdmin(admin.ModelAdmin):
    list_display = ('registro_academico', 'data_confirmacao', 'nome', 'email', 'curso', 'ano_ingresso')
    search_fields = ['registro_academico', 'nome', 'email', 'curso', 'ano_ingresso']
    # Torna o sistema bastante rígido a violações do estatuto
    readonly_fields = ['token_acao', 'token_uuid', 'token_vencimento', 'data_confirmacao']


admin.site.register(Membro, MembroAdmin)
