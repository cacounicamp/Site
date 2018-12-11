from django.db import models
from django.conf import settings


# Modelo para página de contato caso o envio do e-mail falhe.
class FormularioContato(models.Model):
    contato = models.EmailField(blank=True, max_length=settings.MAX_LENGTH_CONTATO_CONTATO)
    assunto = models.CharField(max_length=settings.MAX_LENGTH_ASSUNTO_CONTATO, null=False, blank=False)
    mensagem = models.TextField(max_length=settings.MAX_LENGTH_MENSAGEM_CONTATO, null=False, blank=False)
    email_enviado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "formulário de contato"
        verbose_name_plural = "formulários de contato"
