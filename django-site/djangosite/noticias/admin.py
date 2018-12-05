from django.contrib import admin

from .models import Noticia


class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_criacao', 'visivel')


# Registramos a notícia
admin.site.register(Noticia, NoticiaAdmin)
