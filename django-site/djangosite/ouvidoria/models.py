from django.db import models


# Modelo para página de contato caso o envio do e-mail falhe.
class FormularioContato(models.Model):
    contato = models.EmailField(blank=True, max_length=320)
    assunto = models.CharField(max_length=140)
    mensagem = models.TextField(max_length=4000)
    email_enviado = models.BooleanField(default=False)
