from django.contrib import admin

from .models import RepresentanteDiscente, Instituicao, Comissao


# Classe para não mostrar o modelo
class EscondeAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class RepresentanteDiscenteAdmin(admin.ModelAdmin):
    list_display = ('ano_atuacao', 'comissao', 'nome')


admin.site.register(Instituicao, EscondeAdmin)
admin.site.register(Comissao, EscondeAdmin)
admin.site.register(RepresentanteDiscente, RepresentanteDiscenteAdmin)
