from django.core.management.base import BaseCommand

import json


class Command(BaseCommand):
    help = 'Analisa as entradas de provas dadas pelo arquivo JSON do site ' \
    ' antigo'

    #
    # Controlador do comando
    #
    def handle(self, *args, **options):
        # Abrimos o arquivo de importação
        with open('provas.json', encoding='utf-8') as arquivo:
            provas_json = json.load(arquivo)


        # Função para tratar lista como um conjunto (sem duplicatas)
        def adicionar_unicamente(lista, item):
            if item not in lista:
                lista.append(item)


        lista_periodos = []
        lista_tipos = []
        lista_codigos = []
        # Agora verificamos quais entradas existem
        for prova in provas_json:
            adicionar_unicamente(lista_periodos, prova['periodo'])
            adicionar_unicamente(lista_tipos, prova['tipo_avaliacao'])
            adicionar_unicamente(lista_codigos, prova['codigo_disciplina'])

        print('Lista de períodos:')
        for periodo in lista_periodos:
            print(periodo)
        print('\n\n\n')

        print('Lista de tipos de avaliação:')
        for tipos in lista_tipos:
            print(tipos)
        print('\n\n\n')

        print('Lista de códigos de disciplinas:')
        for codigos in lista_codigos:
            print(codigos)
        print('\n\n\n')
