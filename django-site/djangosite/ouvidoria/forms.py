from django import forms
from django.conf import settings

from .models import FormularioContato


class FormContato(forms.Form):
    contato = forms.EmailField(required=False, label='Seu e-mail:', max_length=settings.MAX_LENGTH_EMAIL)
    assunto = forms.CharField(required=True, label='*Assunto:', max_length=settings.MAX_LENGTH_ASSUNTO_CONTATO)
    mensagem = forms.CharField(required=True, label='*Mensagem:', widget=forms.Textarea, max_length=settings.MAX_LENGTH_MENSAGEM_CONTATO)

    class Meta:
        model = FormularioContato
