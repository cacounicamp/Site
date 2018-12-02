from django.contrib import admin
from .models import FormularioContato


class FormularioContatoAdmin(admin.ModelAdmin):
    list_display = ('assunto', 'contato', 'email_enviado')
    search_fields = ('assunto', 'contato', 'mensagem', 'email_enviado')
    list_per_page = 25
    readonly_fields = ['assunto', 'contato', 'mensagem', 'email_enviado']

admin.site.register(FormularioContato, FormularioContatoAdmin)
