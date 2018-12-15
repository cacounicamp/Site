from django.contrib import admin

from .models import Disciplina, CodigoDisciplina, TipoAvaliacao, Periodo, Avaliacao

# Classe para não mostrar o modelo
class EscondeAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

admin.site.register(Disciplina, EscondeAdmin)
admin.site.register(CodigoDisciplina)
admin.site.register(TipoAvaliacao)
admin.site.register(Periodo)
admin.site.register(Avaliacao)
