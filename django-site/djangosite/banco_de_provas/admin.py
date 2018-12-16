from django.contrib import admin

from .models import Disciplina, CodigoDisciplina, TipoAvaliacao, Periodo, Avaliacao


# Classe para não mostrar o modelo
class EscondeAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class CodigoDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome_atualizado', 'disciplina')


class AvaliacoesAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'periodo', 'ano', 'tipo_avaliacao', 'quantificador_avaliacao', 'docente', 'visivel')
    ordering = ['visivel', '-ano', '-periodo', '-quantificador_avaliacao', 'tipo_avaliacao', 'disciplina__id', 'docente']


admin.site.register(Disciplina, EscondeAdmin)
admin.site.register(CodigoDisciplina, CodigoDisciplinaAdmin)
admin.site.register(TipoAvaliacao)
admin.site.register(Periodo)
admin.site.register(Avaliacao, AvaliacoesAdmin)
