from django.contrib import admin

from .models import Disciplina, CodigoDisciplina, TipoAvaliacao, Periodo, Avaliacao


class CodigoDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome_atualizado', 'disciplina')
    search_fields = ['disciplina__id', 'codigo']
    ordering = ['codigo']


class AvaliacoesAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'periodo', 'ano', 'tipo_avaliacao', 'quantificador_avaliacao', 'docente', 'possui_resolucao', 'visivel')
    ordering = ['visivel', '-ano', '-periodo', '-quantificador_avaliacao', 'tipo_avaliacao', 'disciplina__id', 'docente']
    search_fields = ['disciplina__id', 'docente', 'tipo_avaliacao__nome', 'ano', 'periodo__nome']


admin.site.register(Disciplina)
admin.site.register(CodigoDisciplina, CodigoDisciplinaAdmin)
admin.site.register(TipoAvaliacao)
admin.site.register(Periodo)
admin.site.register(Avaliacao, AvaliacoesAdmin)
