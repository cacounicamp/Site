import datetime

from django import forms
from django.conf import settings

from .models import TipoAvaliacao, Periodo


def exemplo_ano():
    hoje = datetime.datetime.now()
    return 'Por exemplo: "{ano}", "{ano_anterior}"'.format(ano=hoje.year, ano_anterior=(hoje.year - 2))

class FormAvaliacao(forms.Form):
    # Disciplina: obrigatória, iremos pesquisar o nome posteriormente
    # Exemplo mínimo: "F328", exemplo máximo: "MA311"
    codigo_disciplina = forms.CharField(
        required=True, min_length=4, max_length=5,
        label='Código da disciplina*',
        help_text='Apenas letras e números, sem traços ou espaços. Por exemplo: "f328", "ma311", "MC404".',
    )

    # Docente que fez a prova: não obrigatória, precisaremos prestar atenção
    docente = forms.CharField(
        required=False,
        max_length=settings.MAX_LENGTH_DOCENTE,
        label='"Código" d* docente que fez a prova',
        help_text='Tente preencher com o nome no e-mail ou site d* docente. Por exemplo: Sara Diaz Cardell do IMECC possui e-mail e site com o código "sdcardell". Se não conhecer ou identificar, coloque apenas o sobrenome.',
    )

    # Tipo de avaliação: obrigatório
    tipo_avaliacao = forms.ModelChoiceField(
        required=False,
        label='Tipo de avaliação*',
        queryset=TipoAvaliacao.objects.all(),
        empty_label='Não encontrei o tipo que procuro',
    )

    # Quantificador da avaliação: não obrigatório
    quantificador = forms.IntegerField(
        required=False,
        min_value=0,
        label='Número da avaliação',
        help_text='Seguindo as respostas do item anterior, formaríamos: "Prova 1", "Exame", "Lista de exercícios 4", "Testinho 3". Esse número distingue P1 da P2 da P3.'
    )

    # Período e ano da avaliação
    periodo = forms.ModelChoiceField(
        required=False,
        label='Período da avaliação',
        queryset=Periodo.objects.all(),
        empty_label='Não encontrei o tipo que procuro ou não sei'
    )
    ano = forms.IntegerField(
        required=False,
        min_value=1970,
        label='Ano da avaliação',
        help_text=exemplo_ano()
    )

    #   Arquivo a ser enviado
    # Exige tratamento especial:
    # https://docs.djangoproject.com/en/2.1/ref/forms/api/#binding-uploaded-files
    arquivo = forms.FileField(
        required=True,
        allow_empty_file=False,
        label='Arquivo da avaliação*',
        help_text='Prefira o formato PDF! Há ferramentas que convertem fotos em PDF ou ainda vários PDF em um único PDF.'
    )
