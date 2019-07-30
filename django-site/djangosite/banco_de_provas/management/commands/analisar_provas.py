from django.core.management.base import BaseCommand

import re
import json

from .models import *


class Command(BaseCommand):
    help = 'Analisa as entradas de provas dadas pelo arquivo JSON do site ' \
    ' antigo'

    #
    # Argumentos
    #
    def add_arguments(self, parser):
        parser.add_argument(
            'arquivo',
            help='Arquivo .JSON do banco de dados do site antigo'
        )

    #
    # Controlador do comando
    #
    def handle(self, *args, **options):
        nome_arquivo = options['arquivo']

        # Abrimos o arquivo de importação
        with open(nome_arquivo, encoding='utf-8') as arquivo:
            provas_json = json.load(arquivo)


        # Função para imprimir com aspas
        def imprimir_lista(lista):
            for item in lista:
                print(item.join(['"', '"']))


        # Agora verificamos quais entradas existem

        lista_periodos = set()
        lista_tipos = set()
        lista_codigos = set()
        # Para todas as provas...
        for prova in provas_json:
            lista_periodos.add(prova['periodo'])
            lista_tipos.add(prova['tipo_avaliacao'])
            lista_codigos.add(prova['codigo_disciplina'])

        # Imprimimos o que obtemos

        print('Lista de períodos:')
        imprimir_lista(lista_periodos)
        print('\n\n\n')

        print('Lista de tipos de avaliação:')
        imprimir_lista(lista_tipos)
        print('\n\n\n')

        print('Lista de códigos de disciplinas:')
        imprimir_lista(lista_codigos)
        print('\n\n\n')


        # Analisaremos os períodos agora, separando ano de período

        # Função para conferir o padrão na lista
        def conferir_padrao(exp_reg, lista):
            itens_matched = set()
            itens_unmatched = set()
            # Para cada item na lista...
            for item in lista:
                # Testamos com a expressão regular
                resultado = exp_reg.match(item)

                # Adicionamos às listas de resultado
                if resultado is None:
                    itens_unmatched.add(item)
                else:
                    itens_matched.add(item)

            return (itens_matched, itens_unmatched)


        # Função para teste dos padrões na lista completa
        def testar_lista(nome, lista, padroes):
            restante = lista

            # Processamos agora os padrões
            for padrao in padroes:
                (matched, unmatched) = conferir_padrao(padrao, restante)
                print('Matched de {0} com "{1}":'.format(nome, padrao.pattern))
                imprimir_lista(matched)
                print('\n\n')
                restante = restante - matched

            # Imprimimos o resto
            print('Unmatched de {0}:'.format(nome))
            imprimir_lista(restante)
            print('\n\n')


        # Testamos os padrões para as listas

        # Compilamos expressões regulares para os períodos
        padroes = [
            # ano semestre
            re.compile('(\d{4})\D{1,3}(\d)'),
            # semestre ano
            re.compile('(\d)\D{1,3}(\d{4})'),
            # ano férias
            re.compile('(\d{4})fer'),
            # ano apenas (sem semestre)
            re.compile('(\d{4})')
        ]
        # Testamos os períodos
        testar_lista('períodos', lista_periodos, padroes)


        # Compilamos expressões regulares para os códigos
        padroes = [
            # disciplinas válidas
            re.compile('[A-Za-z]{1,2}\d{3}'),

            # disciplinas válidas com espaço
            re.compile('[A-Za-z]{1} \d{3}'),
        ]
        # Testamos os códigos
        testar_lista('códigos', lista_codigos, padroes)


        # Compilamos expressões regulares para os tipos
        padroes = [
            # prova diurna com resolução
            re.compile('(p|P)(\d).*(d|D).*(res)'),
            re.compile('(p|P)(\d).*(d|D).*(sol)'),
            re.compile('(p|P)(\d).*(d|D).*(gab)'),
            re.compile('(p|P)(\d).*(res).*(d|D)'),
            re.compile('(p|P)(\d).*(sol).*(d|D)'),
            re.compile('(p|P)(\d).*(gab).*(d|D)'),
            # prova noturna com resolução
            re.compile('(p|P)(\d).*(n|N).*(res)'),
            re.compile('(p|P)(\d).*(n|N).*(sol)'),
            re.compile('(p|P)(\d).*(n|N).*(gab)'),
            re.compile('(p|P)(\d).*(res).*(n|N)'),
            re.compile('(p|P)(\d).*(sol).*(n|N)'),
            re.compile('(p|P)(\d).*(gab).*(n|N)'),
            # prova com resolução
            re.compile('(p|P)(\d).*(res)'),
            re.compile('(p|P)(\d).*(sol)'),
            re.compile('(p|P)(\d).*(gab)'),
            re.compile('(res).*(p|P)(\d)'),

            # prova diurna sem resolução
            re.compile('(p|P)(\d).*(d|D)'),
            # prova noturna sem resolução
            re.compile('(p|P)(\d).*(n|N)'),
            # prova substitutiva sem resolução
            re.compile('(p|P)(\d).*sub'),
            # prova do semestre todo
            re.compile('(p|P)1.*p2.*ex'),
            # prova sem resolução
            re.compile('(p|P)(\d)'),
            # prova sem resolução sem quantificador
            re.compile('(p|P)'),

            # prova substitutiva com resolução (nome implícito)
            re.compile('(sub).*(res)'),
            re.compile('(2c).*(res)'),
            # prova substitutiva (nome implícito)
            re.compile('(sub).*'),
            re.compile('(2c).*'),

            # lista com resolução
            re.compile('(l|L).*(\d).*(res)'),
            re.compile('(l|L).*(\d).*(gab)'),
            re.compile('(l|L).*(\d).*(sol)'),
            # lista com resolução sem quantificador
            re.compile('(l|L).*(res)'),
            re.compile('(l|L).*(gab)'),
            re.compile('(l|L).*(sol)'),

            # lista sem resolução
            re.compile('(l|L).*(\d)'),
            # lista sem resolução sem quantificador
            re.compile('(l|L).*'),

            # exercício capítulo X com resolução
            re.compile('(ex).*(cap).*(\d).*(res)'),
            re.compile('(ex).*(cap).*(\d).*(gab)'),
            re.compile('(ex).*(cap).*(\d).*(sol)'),
            # exercício com resolução
            re.compile('(ex).*(\d).*(res)'),
            re.compile('(ex).*(\d).*(gab)'),
            re.compile('(ex).*(\d).*(sol)'),
            # exercício capítulo X sem resolução
            re.compile('(ex).*(cap).*(\d)'),
            # exercício sem resolução
            re.compile('(ex).*(\d)'),
            re.compile('(exe).*'),

            # exame diurno sem resolução
            re.compile('(exa).*(d|D)'),
            # exame noturno sem resolução
            re.compile('(exa).*(n|N)'),
            # exame com resolução
            re.compile('(exa).*(res)'),
            re.compile('(exa).*(sol)'),
            re.compile('(exa).*(gab)'),
            # exame com resolução (nome ambíguo)
            re.compile('(ex).*(res)'),
            re.compile('(ex).*(gab)'),
            re.compile('(ex).*(sol)'),
            # exame sem resolução
            re.compile('(exa).*'),
            re.compile('(Exa).*'),
            # exame sem resolução (nome ambíguo)
            re.compile('(ex).*'),

            # teste com resolução
            re.compile('(t|T).*(\d).*(res)'),
            re.compile('(t|T).*(\d).*(sol)'),
            re.compile('(t|T).*(\d).*(gab)'),
            re.compile('(quiz).*(\d).*(res)'),
            re.compile('(quiz).*(\d).*(sol)'),
            re.compile('(quiz).*(\d).*(gab)'),
            # teste sem resolução
            re.compile('(t|T).*(\d)'),

            # atividade com resolução
            re.compile('(at).*(\d).*(res)'),
            re.compile('(at).*(\d).*(re)'), # nome esquisito
            # atividade sem resolução
            re.compile('(at).*(\d)'),

            # anotações de aula
            re.compile('(anot).*'),
        ]
        # Testamos os tipos
        testar_lista('tipos', lista_tipos, padroes)


        # Determinamos as características da prova
        for prova in provas_json:

            # Pegamos todas as informações
            codigo_string = form.cleaned_data['codigo_disciplina'].lower()
            docente = form.cleaned_data['docente'].lower()
            # Tipo de avaliação deve possuir uma opção chave para os formulários
            # como "Não sei dizer ou não encontrei o tipo que procuro"
            tipo_avaliacao = form.cleaned_data['tipo_avaliacao']
            quantificador = form.cleaned_data['quantificador']
            periodo = form.cleaned_data['periodo']
            ano = form.cleaned_data['ano']
            possui_resolucao = form.cleaned_data['possui_resolucao']
            arquivo = form.cleaned_data['arquivo']
