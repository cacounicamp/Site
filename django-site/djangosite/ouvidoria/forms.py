from django.forms import ModelForm

from .models import FormularioContato


class FormContato(ModelForm):
    class Meta:
        model = FormularioContato
        fields = ['contato', 'assunto', 'mensagem']
