from django.db import models
from django.conf import settings


# Instituição em que a Comissão/Congregação/Conselho ocorre (ex. Unicamp, IC, FEEC)
class Instituicao(models.Model):
    # Nome da instituição
    nome = models.CharField(max_length=settings.MAX_LENGTH_NOME, null=False, blank=False)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"
        ordering = ['nome']


# Comissão/Congregação/Conselho em que possuimos representantes
class Comissao(models.Model):
    # Nome da comissão
    nome = models.CharField(max_length=settings.MAX_LENGTH_NOME, null=False, blank=False)
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
    nome = models.CharField(max_length=settings.MAX_LENGTH_NOME, null=False, blank=False)

    # Se representante é titular
    titular = models.BooleanField(default=True, null=False, blank=False)

    # Ano de ingresso d* representante
    ano_ingresso = models.PositiveIntegerField(null=True, blank=True)
    # Curso d* representante
    curso = models.CharField(max_length=settings.MAX_LENGTH_CURSOS, null=False, blank=False, choices=settings.CURSOS)

    # Ano de atuação d* representante
    ano_atuacao = models.PositiveIntegerField(null=False, blank=False)
    # Comissão em que o representante participa
    comissao = models.ForeignKey(
        Comissao, null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return '{rd.nome} ({rd.curso}{ano_ingresso}): {titularidade} em {rd.ano_atuacao} de {rd.comissao}'.format(rd=self, titularidade='titular' if self.titular else 'suplente', ano_ingresso=str(self.ano_ingresso) + ' ' if self.ano_ingresso else '')

    class Meta:
        verbose_name = "representante discente"
        verbose_name_plural = "representantes discentes"
        ordering = ['-ano_atuacao', 'nome']
