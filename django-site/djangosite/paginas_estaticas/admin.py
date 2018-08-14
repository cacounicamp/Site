from django import forms
from django.conf import settings
from django.contrib import admin
# Para mensagens de erro
from django.utils.translation import gettext

from .models import *
# Para editor de content da página
from ckeditor.widgets import CKEditorWidget

# Colocamos o editor no formulário de administrador
# Cópia de https://github.com/django/django/blob/master/django/contrib/flatpages/forms.py
class FormPaginaEstatica(forms.ModelForm):
    endereco = forms.RegexField(
        label="URL",
        max_length=200,
        regex=r'^[~.-\/\w]*\/$',
        help_text="Exemplo: 'sobre/contato/'.",
        error_messages={
            "invalid": "Pode conter apenas letras, números, pontos, underlines, traços. Deve possuir barra no fim.",
        },
    )
    conteudo = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = PaginaEstatica
        fields = '__all__'

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco']
        if (settings.APPEND_SLASH and
                'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE and
                not endereco.endswith('/')):
            raise forms.ValidationError(
                gettext("URL is missing a trailing slash."),
                code='missing_trailing_slash',
            )
        return endereco

    def clean(self):
        endereco = self.cleaned_data.get('endereco')

        endereco_identico = PaginaEstatica.objects.filter(endereco=endereco)
        if self.instance.pk:
            endereco_identico = endereco_identico.exclude(pk=self.instance.pk)

        return super().clean()

# Criamos o administrador para o formulário
class AdminPaginaEstatica(admin.ModelAdmin):
    form = FormPaginaEstatica
    list_display = ('endereco', 'titulo')
    search_fields = ('endereco', 'titulo')
    fields = ('endereco', 'titulo', 'conteudo')

# Registramos nossos modelos
admin.site.register(MenuDropdown)
admin.site.register(ItemMenu)

# Registramos o administrador para PaginaEstatica
admin.site.register(PaginaEstatica, AdminPaginaEstatica)
