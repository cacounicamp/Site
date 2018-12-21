from django.db import models
from django.conf import settings
from django.utils import timezone

from ckeditor_uploader.fields import RichTextUploadingField


class Noticia(models.Model):
    # Título da notícia
    titulo = models.CharField(max_length=settings.MAX_LENGTH_TITULO_NOTICIAS, null=False, blank=False)
    # Subtítulo/descricao/resumo da notícia
    resumo = models.CharField(max_length=settings.MAX_LENGTH_RESUMO_NOTICIAS, null=False, blank=False)
    # Notícia visível
    visivel = models.BooleanField(default=True, null=False)
    # Conteúdo da notícia
    conteudo = RichTextUploadingField(null=False, blank=False)
    # Data de criação
    data_criacao = models.DateTimeField(null=False, default=timezone.now)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "notícia"
        verbose_name_plural = "notícias"
        # Ordenamos do mais novo ao mais velho
        ordering = ['-data_criacao']
