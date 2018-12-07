from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField


class Gestao(models.Model):
    # Nome da gestão
    nome = models.CharField(max_length=42, null=False, blank=False)
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
    nome = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return self.nome


# Para os cargos
class Membro(models.Model):
    CURSOS = (
        ('EC', 'Engenharia de computação'),
        ('CC', 'Ciência da computação'),
        ('Pós', 'Pós-graduação do IC'),
    )

    # Gestão a qual o membro participa
    gestao = models.ForeignKey(
        Gestao, null=False, blank=False, on_delete=models.CASCADE
    )
    # Cargo
    cargo = models.ForeignKey(
        Cargo, null=False, blank=False, on_delete=models.CASCADE
    )
    # Nome do membro
    nome = models.CharField(max_length=128, null=False, blank=False)
    # Apelido do membro (se houver)
    apelido = models.CharField(max_length=24, null=False, blank=True)
    # Curso do membro
    curso = models.CharField(max_length=4, null=False, blank=False, choices=CURSOS)
    # Ano de ingresso do membro
    ano_ingresso = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self):
        return '{membro.nome} "{membro.apelido}" {membro.curso} {membro.ano_ingresso}'.format(membro=self)
