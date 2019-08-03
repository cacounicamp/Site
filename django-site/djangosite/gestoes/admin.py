from django.contrib import admin

from .models import Gestao, Cargo, Membro


# Classe para não mostrar o modelo
class EscondeAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class MembroAdmin(admin.ModelAdmin):
    list_display = ('gestao', 'cargo', 'nome', 'apelido', 'ano_ingresso', 'curso')
    search_fields = ['nome', 'apelido', 'gestao__nome', 'gestao__ano_eleito', 'cargo__nome', 'curso']


admin.site.register(Gestao, EscondeAdmin)
admin.site.register(Cargo, EscondeAdmin)
admin.site.register(Membro, MembroAdmin)
