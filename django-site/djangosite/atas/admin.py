from django.contrib import admin

from .models import AtaReuniao, AtaAssembleia


class AtaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'data_criacao')
    search_fields = ['data_criacao', 'conteudo']


admin.site.register(AtaReuniao, AtaAdmin)
admin.site.register(AtaAssembleia, AtaAdmin)
