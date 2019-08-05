from django.contrib import admin

from .models import Noticia


class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_criacao', 'visivel')
    search_fields = ['titulo', 'data_criacao', 'conteudo']


# Registramos a notícia
admin.site.register(Noticia, NoticiaAdmin)
