from django.db import models
from django.conf import settings

from ckeditor_uploader.fields import RichTextUploadingField


class Gestao(models.Model):
    # Nome da gestão
    nome = models.CharField(max_length=settings.MAX_LENGTH_NOME, null=False, blank=False)
    # Ano de eleicao (ano de atuacao - 1)
    ano_eleito = models.PositiveIntegerField(unique=True, null=False)
    # Conteúdo da página da gestão (texto de posse, informações sobre eleição
    # etc)
    conteudo = RichTextUploadingField()

    def __str__(self):
        return 'Gestão {0} de {1}/{2}'.format(self.nome, self.ano_eleito, self.ano_eleito + 1)

    class Meta:
        verbose_name = "gestão"
        verbose_name_plural = "gestões"
        ordering = ['-ano_eleito']


# Compartilhada entre todas as gestões (uniformização do nome do cargo <3)
class Cargo(models.Model):
    # Nome do cargo
    nome = models.CharField(max_length=settings.MAX_LENGTH_CARGOS, null=False, blank=False)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "cargo da gestão"
        verbose_name_plural = "cargos das gestões"


# Para os cargos
class Membro(models.Model):
    # Gestão a qual o membro participa
    gestao = models.ForeignKey(
        Gestao, null=False, blank=False, on_delete=models.CASCADE
    )
    # Cargo
    cargo = models.ForeignKey(
        Cargo, null=False, blank=False, on_delete=models.CASCADE
    )
    # Nome do membro
    nome = models.CharField(max_length=settings.MAX_LENGTH_NOME, null=False, blank=False)
    # Apelido do membro (se houver)
    apelido = models.CharField(max_length=settings.MAX_LENGTH_APELIDO, null=False, blank=True)
    # Curso do membro
    curso = models.CharField(max_length=settings.MAX_LENGTH_CURSOS, null=False, blank=False, choices=settings.CURSOS)
    # Ano de ingresso do membro
    ano_ingresso = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self):
        return '{membro.nome} "{membro.apelido}" {membro.curso} {membro.ano_ingresso}'.format(membro=self)

    class Meta:
        verbose_name = "membro da gestão"
        verbose_name_plural = "membros das gestões"
