from django.forms import ModelForm
from django.conf import settings

from .models import FormularioContato


class FormContato(ModelForm):
    class Meta:
        model = FormularioContato
        fields = ['contato', 'assunto', 'mensagem']
