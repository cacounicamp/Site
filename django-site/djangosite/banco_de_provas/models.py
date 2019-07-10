import uuid

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import post_delete, pre_save


class TipoAvaliacao(models.Model):
    # Nome do tipo de avaliação
    nome = models.CharField(
        primary_key=True, max_length=settings.MAX_LENGTH_TIPO_AVALIACAO,
        help_text='Por exemplo: "Prova", "Lista" ou "Testinho"',
        null=False, blank=False
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "tipo de avaliação"
        verbose_name_plural = "tipos de avaliações"
        ordering = ['nome']


class Periodo(models.Model):
    # Nome do período
    nome = models.CharField(
        primary_key=True, max_length=settings.MAX_LENGTH_PERIODO,
        help_text='Por exemplo: "Primeiro semestre" ou "Férias de verão"',
        null=False, blank=False
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "período"
        verbose_name_plural = "períodos"
        ordering = ['nome']


class Disciplina(models.Model):
    id = models.AutoField(primary_key=True)

    # Para verificarmos se a disciplina criada automáticamente já foi autorizada
    # por um membro do centro acadêmico
    autorizada = models.BooleanField(
        default=True,
        help_text='Define se a disciplina será mostrada nas pesquisas ou se foi criada automáticamente e ainda não aprovada. Para aprovar, confira se é uma disciplina que teve nome alterado recentemente e portanto já possui provas em outro nome.',
        null=False, blank=False
    )

    # Função mostra apenas os nomes atualizados de tal disciplina
    def display(self):
        codigos = []
        for codigo in CodigoDisciplina.objects.filter(disciplina=self, nome_atualizado=True).all():
            codigos.append(codigo.codigo)

        if len(codigos) == 0:
            return 'Código não especificado'
        else:
            return ', '.join(codigos)

    # Função mostra nomes atualizados com asterisco
    def __str__(self):
        codigos = []
        for codigo in CodigoDisciplina.objects.filter(disciplina=self).all():
            codigos.append(codigo.codigo + ('*' if codigo.nome_atualizado else ''))
        return 'Disciplina #{disciplina.id} {status}<-- {codigos}'.format(
            disciplina=self,
            codigos=', '.join(codigos),
            status='' if self.autorizada else '[NÃO CONFIRMADA] '
        )

    def save(self, *args, **kwargs):
        # observação: isso não acontece sempre... em algumas páginas de
        # administrador eu noto, mas não em todas. O mais efetivo é alterar
        # na página de avaliações alguma disciplina qualquer

        # Conferimos se há Disciplinas vazias e apagamos se houver

        # Vemos quais são referenciadas por códigos
        ids_utilizados = CodigoDisciplina.objects.values_list(
            'disciplina__id', flat=True
        )
        # Apagamos os não utilizados
        disciplinas = Disciplina.objects.exclude(id__in=ids_utilizados)
        # Para não sermos redundantes...
        if self.id is not None:
            disciplinas = disciplinas.exclude(id=self.id)
        disciplinas.delete()

        if settings.DEBUG:
            print('Possívelmente excluímos algumas disciplinas não referenciadas.')

        super().save(*args, **kwargs) # continuamos o save normal

    class Meta:
        verbose_name = "disciplina"
        verbose_name_plural = "disciplinas"
        # Pegamos as registradas mais recentemente
        ordering = ['-id']


class CodigoDisciplina(models.Model):
    # Disciplina à qual associamos esse código
    disciplina = models.ForeignKey('Disciplina', on_delete=models.CASCADE)

    # Se esse código é o código atual da disciplina
    nome_atualizado = models.BooleanField(
        default=True,
        help_text='Diz se esse nome aparecerá como o nome da disciplina ao buscar uma prova.',
        null=False, blank=False
    )

    # Código da disciplina
    codigo = models.CharField(
        # primary_key faz com que quando é alterado pelo administrador, crie uma
        # duplicata. Por exemplo, temos "MC302". Se alterarmos o nome para
        # "MC322", ele irá inserir um código com "MC322" e manter "MC302"
        primary_key=True,
        max_length=settings.MAX_LENGTH_CODIGO_DISCIPLINA,
        help_text='Por exemplo, "MC202", "F328"',
        null=False, blank=False
    )

    def __str__(self):
        return '{modelo.codigo} --> disciplina id={modelo.disciplina.id}'.format(modelo=self)

    class Meta:
        verbose_name = "código da disciplina"
        verbose_name_plural = "códigos de disciplinas"
        ordering = ['disciplina__id', 'codigo']


# Nome do arquivo da avaliação a ser salva
def determinar_nome_arquivo(instance, filename):
    if instance.quantificador_avaliacao is None:
        quantificador = ''
    else:
        quantificador = str(instance.quantificador_avaliacao)

    # Começamos com a lista de atributos obrigatórios
    id_disciplina = str(instance.disciplina.id)
    atributos = [
        id_disciplina,
        instance.tipo_avaliacao.nome + quantificador,
    ]

    # Incluímos com o número de opcionais
    if instance.docente is not None:
        atributos.append(instance.docente)
    if instance.periodo is not None:
        atributos.append(instance.periodo.nome)
    if instance.ano is not None:
        atributos.append(str(instance.ano))

    # Criamos um trecho aleatório
    atributos.append(str(uuid.uuid4()))

    # Pegamos a extensão do nome do arquivo
    if len(filename) > 0:
        split = filename.split('.')
        extensao = '.' + split[len(split) - 1].replace(' ', '')
    else:
        extensao = '.extensao_desconhecida'

    return settings.PROVAS_PATH + slugify('-'.join(atributos)) + extensao


class Avaliacao(models.Model):
    # Disciplina associada à avaliação (criamos utilizando o nome do formulário
    # associado a alguma instância de disciplina que representará todos os
    # nomes)
    disciplina = models.ForeignKey('Disciplina', on_delete=models.PROTECT)

    # Docente que fez a avaliação (pode ser omitido)
    docente = models.CharField(
        max_length=settings.MAX_LENGTH_DOCENTE,
        help_text='Tente tornar o mais próximo do e-mail ou "código" do docente. Por exemplo, Sara Diaz Cardell do IMECC possui e-mail/site com "sdcardell", então usamos "sdcardell".',
        null=True, blank=True
    )

    #   Tipo da avaliação
    # Não podem ser omitidos -- quem está enviando deve saber o que está
    # enviando..
    # Por exemplo "Prova"
    tipo_avaliacao = models.ForeignKey('TipoAvaliacao', on_delete=models.PROTECT, null=False, blank=False)
    # Por exemplo 1, para formar "Prova 1". Pode ser dispensado
    quantificador_avaliacao = models.PositiveIntegerField(null=True, blank=True)

    #   Semestre da avaliação (pode ser omitido)
    # Período
    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, null=True, blank=True)
    # Ano
    ano = models.PositiveIntegerField(null=True, blank=True)

    # Se a prova possui resolução
    possui_resolucao = models.BooleanField(default=False, null=False, blank=False)

    # Arquivo associado à avaliação
    arquivo = models.FileField(upload_to=determinar_nome_arquivo)

    # Se a avaliação está visível a tod*s
    visivel = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        atributos = [
            str(self.disciplina),
            str(self.tipo_avaliacao),
            'visivel' if self.visivel else 'invisível'
        ]

        # Verificamos os atributos opcionais
        if self.docente is not None:
            atributos.append(self.docente)
        if self.quantificador_avaliacao is not None:
            atributos.append(str(self.quantificador_avaliacao))
        if self.periodo is not None:
            atributos.append(str(self.periodo))
        if self.ano is not None:
            atributos.append(str(self.ano))

        # Fazemos a string
        return ' - '.join(atributos)

    class Meta:
        verbose_name = "avaliação"
        verbose_name_plural = "avaliações"
        # Ordenamos em ordem cronológica de semestre (do mais recente ao mais
        # antigo)
        ordering = ['-ano', '-periodo', '-quantificador_avaliacao', 'tipo_avaliacao', 'disciplina__id', 'docente']


@receiver(post_delete, sender=Avaliacao)
def receiver_avaliacao_deletada(sender, instance, **kwargs):
    # Apagamos o arquivo
    instance.arquivo.delete(False)

# Fonte: https://djangosnippets.org/snippets/10638/
@receiver(pre_save, sender=Avaliacao)
def receiver_avaliacao_alterada(sender, instance, **kwargs):
    # Conferimos se existe no banco de dados
    if not instance.pk:
        return

    # Pegamos o antigo arquivo
    try:
        antigo_arquivo = sender.objects.get(pk=instance.pk).arquivo
    except sender.DoesNotExist:
        return

    # Pegamos o novo arquivo
    novo_arquivo = instance.arquivo
    # Conferimos se o arquivo é diferente
    if antigo_arquivo != novo_arquivo:
        antigo_arquivo.delete(False)
