from django.core.management.base import BaseCommand

import json
from datetime import datetime

from atas.models import AtaReuniao


class Command(BaseCommand):
    help = 'Importa as atas de reunião do site anterior através de um arquivo' \
           ' JSON'

    #
    # Controlador do comando
    #
    def handle(self, *args, **options):
        with open('atas.json', encoding='utf-8') as arquivo:
            atas_inserir = []
            atas = json.load(arquivo)

            # Temos uma lista de atas
            for ata in atas:
                # Tentamos definir a data de criação da ata
                try:
                    # [::-1] inverte a string, o replace substitui apenas UM
                    # dois pontos, que será o último, na parte da timezone.
                    # Dessa forma, conseguimos utilizar "%z" corretamente.
                    data_criacao = datetime.strptime(
                        ata['data_criacao'][::-1].replace(':', '', 1)[::-1],
                        '%Y-%m-%d %H:%M:%S.%f%z'
                    )
                except ValueError:
                    data_criacao = datetime.strptime(
                        ata['data_criacao'],
                        '%Y-%m-%d %H:%M:%S%z'
                    )

                # Criamos uma ata com as informações
                atas_inserir.append(AtaReuniao(
                    conteudo=ata['conteudo'],
                    highlights=ata['highlights'],
                    data_criacao=data_criacao,
                ))

            # Agora inserimos as atas
            print('Inserindo {} atas.'.format(len(atas_inserir)))
            AtaReuniao.objects.bulk_create(atas_inserir)
