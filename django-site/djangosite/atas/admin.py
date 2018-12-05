from django.contrib import admin

from .models import AtaReuniao, AtaAssembleia


class AtaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'data_criacao')


admin.site.register(AtaReuniao, AtaAdmin)
admin.site.register(AtaAssembleia, AtaAdmin)
