from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify

from ckeditor_uploader.fields import RichTextUploadingField


def formatar_data(data):
    return data.strftime("%d/%m/%Y")


class Ata(models.Model):
    # Conteúdo da ata
    conteudo = RichTextUploadingField(null=False, blank=False)
    # Highlights da ata para atrair visualizações
    highlights = models.CharField(max_length=settings.MAX_LENGTH_HIGHLIGHT_ATAS, blank=True, null=False)
    # Data de criação
    data_criacao = models.DateTimeField(null=False)
    # Se a ata está visível ou não
    visivel = models.BooleanField(default=True, null=False, blank=False)

    def get_data_slug(self):
        return slugify('ata de ' + self.data_criacao.strftime("%d-%m-%Y %H:%M %Z"))

    def get_url(self):
        return reverse(self.get_url_especifica(), args=[self.pk, self.get_data_slug()])

    class Meta:
        abstract = True


class AtaAssembleia(Ata):
    # Assembleia deliberativa ou não
    deliberativa = models.BooleanField(default=False, null=False)

    def get_url_especifica(self):
        return 'ata/assembleia/'

    def display_tipo_ata(ata):
        if ata.deliberativa:
            return 'Assembleia deliberativa'
        else:
            return 'Assembleia não deliberativa'

    def __str__(self):
        if self.deliberativa:
            return 'Assembleia deliberativa de ' + formatar_data(self.data_criacao)
        else:
            return 'Assembleia não deliberativa de ' + formatar_data(self.data_criacao)

    class Meta:
        verbose_name = "ata de assembleia"
        verbose_name_plural = "atas de assembleias"
        # Ordenamos do mais novo ao mais velho
        ordering = ['-data_criacao']


class AtaReuniao(Ata):
    # Reunião extraordinária ou não
    extraordinaria = models.BooleanField(default=False, null=False, blank=False)

    def get_url_especifica(self):
        return 'ata/reuniao/'

    def display_tipo_ata(ata):
        if ata.extraordinaria:
            return 'Reunião extraordinária'
        else:
            return 'Reunião ordinária'

    def __str__(self):
        if self.extraordinaria:
            return 'Reunião extraordinária de ' + formatar_data(self.data_criacao)
        else:
            return 'Reunião ordinária de ' + formatar_data(self.data_criacao)

    class Meta:
        verbose_name = "ata de reunião"
        verbose_name_plural = "atas de reuniões"
        # Ordenamos do mais novo ao mais velho
        ordering = ['-data_criacao']
