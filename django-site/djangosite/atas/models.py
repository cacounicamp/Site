from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField


def formatar_data(data):
    return data.strftime("%d/%m/%Y")


class Ata(models.Model):
    # Conteúdo da ata
    conteudo = RichTextUploadingField(null=False, blank=False)
    # Highlights da ata para atrair visualizações
    highlights = models.CharField(max_length=300, blank=True, null=False)
    # Data de criação
    data_criacao = models.DateTimeField(null=False)
    # Se a ata está visível ou não
    visivel = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        abstract = True


class AtaAssembleia(Ata):
    # Assembleia deliberativa ou não
    deliberativa = models.BooleanField(default=False, null=False)

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
        verbose_name_plural = "atas de assembleia"
        # Ordenamos do mais novo ao mais velho
        ordering = ['-data_criacao']


class AtaReuniao(Ata):
    # Reunião extraordinária ou não
    extraordinaria = models.BooleanField(default=False, null=False, blank=False)

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
        verbose_name_plural = "atas de reunião"
        # Ordenamos do mais novo ao mais velho
        ordering = ['-data_criacao']
