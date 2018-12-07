from django.db import models

from gestoes.models import Membro


# Instituição em que a Comissão/Congregação/Conselho ocorre (ex. Unicamp, IC, FEEC)
class Instituicao(models.Model):
    # Nome da instituição
    nome = models.CharField(max_length=128, unique=True, null=False, blank=False)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"
        ordering = ['nome']


# Comissão/Congregação/Conselho em que possuimos representantes
class Comissao(models.Model):
    # Nome da comissão
    nome = models.CharField(max_length=128, unique=True, null=False, blank=False)
    # Instituição em que a comissão atua
    instituicao = models.ForeignKey(
        Instituicao, null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.nome + ' de ' + str(self.instituicao)

    class Meta:
        verbose_name = "Comissão/Congregação/Conselho"
        verbose_name_plural = "Comissões/Congregações/Conselhos"
        ordering = ['nome']


class RepresentanteDiscente(models.Model):
    # Nome d* representante discente
    nome = models.CharField(max_length=128, null=False, blank=False)

    # Se representante é titular
    titular = models.BooleanField(default=True, null=False, blank=False)

    # Ano de ingresso d* representante
    ano_ingresso = models.PositiveIntegerField(null=False, blank=False)
    # Curso d* representante
    curso = models.CharField(max_length=4, null=False, blank=False, choices=Membro.CURSOS)

    # Ano de atuação d* representante
    ano_atuacao = models.PositiveIntegerField(null=False, blank=False)
    # Comissão em que o representante participa
    comissao = models.ForeignKey(
        Comissao, null=False, blank=False, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "representante discente"
        verbose_name_plural = "representantes discentes"
        ordering = ['-ano_atuacao', 'nome']
