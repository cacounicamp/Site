from django.core.management.base import BaseCommand

import json

from banco_de_provas.models import Periodo, Disciplina, CodigoDisciplina, \
    Avaliacao


class Command(BaseCommand):
    help = 'Importa as provas do banco de provas do site anterior através de ' \
    'um arquivo JSON'

    #
    # Controlador do comando
    #
    def handle(self, *args, **options):
        with open('provas.json', encoding='utf-8') as arquivo:
            # Abrimos o arquivo de importação
            provas_json = json.load(arquivo)

        # Guardamos os objetos a serem inseridos
        avaliacoes_inserir = []

        # Função para obter em cache disciplinas
        disciplinas = {}
        def obter_disciplina(codigo):
            # Vemos se está salvo em cache
            if codigo in disciplinas:
                return disciplinas[codigo]

            # Se não está, continuamos procurando
            try:
                # Primeiro, no banco de dados
                codigo_disciplina = CodigoDisciplina.objects.get(
                    codigo=codigo
                )

                # Pegamos a disciplina através do código já registrado
                disciplina = codigo_disciplina.disciplina

                # Adicionamos no cache e retornamos
                disciplinas[codigo] = disciplina
                return disciplina
            except ObjectDoesNotExist:
                # Se não há código registrado, precisamos criar uma nova

                # Criamos uma nova disciplina autorizada pois estamos
                # importando
                disciplina = Disciplina(
                    autorizada=True
                )
                # Salvamos e colocamos no cache
                disciplina.save()
                disciplinas[codigo] = disciplina

                # Agora criamos um nome para a disciplina
                # Consideramos o nome como o mais atualizado
                codigo_disciplina = CodigoDisciplina(
                    disciplina=disciplina,
                    nome_atualizado=True,
                    codigo=codigo
                )
                codigo_disciplina.save()

                # retornamos a disciplina
                return disciplina


        # Função para determinar tipo e quantificador da prova, além de se
        # possui resolução
        def obter_tipo_avaliacao(tipo):
            return (None, None, None)


        # Função para determinar período e ano da prova
        def obter_periodo_avaliacao(periodo_string):
            return (None, None)


        # Com essas funções, importamos as provas

        # Para cada prova...
        for prova in provas_json:
            # Pegamos as informações
            codigo_string = prova['codigo_disciplina'].lower()
            docente_string = prova['docente'].lower()
            tipo_avaliacao_string = prova['tipo_avaliacao']
            periodo_string = prova['periodo']
            arquivo_string = prova['arquivo']

            # Obtemos a disciplina a partir do código
            disciplina = obter_disciplina(codigo_string)

            # Determinamos o tipo de avaliação a partir da string
            (tipo_avaliacao, quantificador, possui_resolucao) = \
                obter_tipo_avaliacao(tipo_avaliacao_string)

            (periodo, ano) = \
                obter_periodo_avaliacao(periodo_string)

            # Criamos uma ata com as informações
            avaliacao = Avaliacao(
                disciplina=disciplina,
                docente=docente,
                tipo_avaliacao=tipo_avaliacao,
                quantificador_avaliacao=quantificador,
                periodo=periodo, # aceita None (período é uma instância mesmo)
                ano=ano,
                possui_resolucao=possui_resolucao,
                arquivo=arquivo
            )
            avaliacoes_inserir.append(avaliacao)

        # Agora inserimos as atas
        print('Inserindo {} avaliações.'.format(len(avaliacoes_inserir)))
        Avaliacao.objects.bulk_create(avaliacoes_inserir)
