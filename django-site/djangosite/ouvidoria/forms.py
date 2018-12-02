from django import forms


class FormContato(forms.Form):
    contato = forms.EmailField(required=False, label='Seu e-mail:', max_length=320)
    assunto = forms.CharField(required=True, label='*Assunto:', max_length=140)
    mensagem = forms.CharField(required=True, label='*Mensagem:', widget=forms.Textarea, max_length=4000)
