from django import forms
from django.conf import settings
from django.contrib import admin
# Para mensagens de erro
from django.utils.translation import gettext

from .models import *
# Para editor de content da página
from ckeditor_uploader.widgets import CKEditorUploadingWidget


def append_slash():
    return settings.APPEND_SLASH and \
    'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE

def help_text():
    exemplos = ['/sobre/contato', '/this-is_sparta']
    # Colocamos trailing slash
    if append_slash():
        exemplos = ['{0}/'.format(exemplo) for exemplo in exemplos]
    # Colocamos aspas
    exemplos = ['"{0}"'.format(exemplo) for exemplo in exemplos]
    # Fazemos o texto final
    return 'Exemplo: {0}'.format(', '.join(exemplos))

# Colocamos o editor no formulário de administrador
# Cópia de https://github.com/django/django/blob/master/django/contrib/flatpages/forms.py
class FormPaginaEstatica(forms.ModelForm):
    # Campo para o endereço
    endereco = forms.RegexField(
        label="URL",
        max_length=200,
        regex=r'(\/)|(\/[\/_\-\w]*\/)' if append_slash() \
                else r'(\/)|(\/[\/_\-\w]*[_\-\w])',
        help_text=help_text,
        error_messages={
            "invalid": "Pode conter apenas letras, números, underlines e traços. Deve possuir barra inicial.",
        },
    )

    # Utilizamos o editor melhorado no campo de conteúdo
    conteudo = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = PaginaEstatica
        fields = '__all__'

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco']

        # Conferimos se a '/' final é obrigatória
        if (append_slash() and not endereco.endswith('/')):
            # Se for e ela não está no endereço, retornamos erro
            raise forms.ValidationError(
                gettext("URL is missing a trailing slash."),
                code='missing_trailing_slash',
            )

        # Se tudo está ok, retornamos
        return endereco

    def clean(self):
        endereco = self.cleaned_data.get('endereco')

        # Verificamos se há um endereço idêntico
        endereco_identico = PaginaEstatica.objects.filter(endereco=endereco)
        if self.instance.pk:
            endereco_identico = endereco_identico.exclude(pk=self.instance.pk)

        return super().clean()


# Criamos o administrador para o formulário
class AdminPaginaEstatica(admin.ModelAdmin):
    form = FormPaginaEstatica
    list_display = ('endereco', 'titulo', 'url_ativa')
    search_fields = ('endereco', 'titulo', 'url_ativa')
    fields = ('endereco', 'titulo', 'url_ativa', 'conteudo')


# Administrador para item comum do menu (ordering)
class AdminItemMenu(admin.ModelAdmin):
    list_display = ('nome', 'dropdown', 'indice')
    ordering = ('dropdown', 'indice')


# Registramos nossos modelos
admin.site.register(MenuDropdown)
admin.site.register(ItemMenu, AdminItemMenu)

# Registramos o administrador para PaginaEstatica
admin.site.register(PaginaEstatica, AdminPaginaEstatica)
