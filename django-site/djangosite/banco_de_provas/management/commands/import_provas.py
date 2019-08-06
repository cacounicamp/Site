import re
import os
import uuid
import json
import shutil

from banco_de_provas.models import *
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist



class Command(BaseCommand):
    help = 'Analisa as entradas de provas dadas pelo arquivo JSON do site ' \
    ' antigo e as insere no banco de dados.'

    #
    # Argumentos
    #
    def add_arguments(self, parser):
        parser.add_argument(
            'arquivo',
            help='Arquivo .JSON do banco de dados do site antigo'
        )
        parser.add_argument(
            'old_media_root',
            help='Caminho até a pasta que contém "banco_de_prova/" do site antigo'
        )

    #
    # Controlador do comando
    #
    def handle(self, *args, **options):
        nome_arquivo = options['arquivo']
        old_media_root = options['old_media_root']

        # Abrimos o arquivo de importação
        with open(nome_arquivo, encoding='utf-8') as arquivo:
            provas_json = json.load(arquivo)

        # Compilamos expressões regulares para os tipos
        padroes = [
        ]
        # Testamos os tipos
        #testar_lista('tipos', lista_tipos, padroes)


        # Registramos as expressões regulares
        # Para análise do código da disciplina
        re_codigo_disc = re.compile('[A-Za-z]{1,2}\d{3}') # cód. disc.
        # Para análise do período
        re_periodo_ano_sem = re.compile('(\d{4})\D{1,3}(\d)') # ano semestre
        re_periodo_sem_ano = re.compile('(\d)\D{1,3}(\d{4})') # semestre ano
        re_periodo_ano_fer = re.compile('(\d{4})fer') # ano em per. de férias
        re_periodo_ano = re.compile('(\d{4})') # ano com semestre desc.
        periodo_1sem = Periodo.objects.get(nome='1º semestre')
        periodo_2sem = Periodo.objects.get(nome='2º semestre')
        periodo_fer = Periodo.objects.get(nome='Férias de verão')
        # Para os docentes
        re_docentes = re.compile('[a-z0-9_]*')
        # Para análise do tipo de prova
        # Teremos listas de tuplas: lista de exp. reg., objeto de TipoAvaliacao e se possui res.
        re_tipos = [
            (
                [
                    # prova diurna com resolução
                    re.compile('(p|P)(\d).*(d|D).*(res)'),
                    re.compile('(p|P)(\d).*(d|D).*(sol)'),
                    re.compile('(p|P)(\d).*(d|D).*(gab)'),
                    re.compile('(p|P)(\d).*(res).*(d|D)'),
                    re.compile('(p|P)(\d).*(sol).*(d|D)'),
                    re.compile('(p|P)(\d).*(gab).*(d|D)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova diurna'),
                2,
                True
            ),
            (
                [
                    # prova diurna sem resolução
                    re.compile('(p|P)(\d).*(d|D)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova diurna'),
                2,
                False
            ),
            (
                [
                    # prova noturna com resolução
                    re.compile('(p|P)(\d).*(n|N).*(res)'),
                    re.compile('(p|P)(\d).*(n|N).*(sol)'),
                    re.compile('(p|P)(\d).*(n|N).*(gab)'),
                    re.compile('(p|P)(\d).*(res).*(n|N)'),
                    re.compile('(p|P)(\d).*(sol).*(n|N)'),
                    re.compile('(p|P)(\d).*(gab).*(n|N)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova noturna'),
                2,
                True
            ),
            (
                [
                    # prova noturna sem resolução
                    re.compile('(p|P)(\d).*(n|N)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova noturna'),
                2,
                False
            ),
            (
                [
                    # prova com resolução
                    re.compile('(p|P)(\d).*(res)'),
                    re.compile('(p|P)(\d).*(sol)'),
                    re.compile('(p|P)(\d).*(gab)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova'),
                2,
                True
            ),
            (
                [
                    # prova com resolução
                    re.compile('(res).*(p|P)(\d)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova'),
                3,
                True
            ),
            (
                [
                    # prova sem resolução
                    re.compile('(p|P)(\d)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova'),
                2,
                False
            ),
            (
                [
                    # prova sem resolução sem quantificador
                    re.compile('(p|P)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova'),
                None,
                False
            ),
            (
                [
                    # prova substitutiva com resolução (nome implícito)
                    re.compile('(sub).*(res)'),
                    re.compile('(2c).*(res)'),
                ],
                TipoAvaliacao.objects.get(nome='Prova substitutiva'),
                None,
                True
            ),
            (
                [
                    # prova substitutiva sem resolução
                    re.compile('(p|P)(\d).*sub'),
                ],
                TipoAvaliacao.objects.get(nome='Prova substitutiva'),
                2,
                False
            ),
            (
                [
                    # prova substitutiva (nome implícito)
                    re.compile('(sub).*'),
                    re.compile('(2c).*'),
                ],
                TipoAvaliacao.objects.get(nome='Prova substitutiva'),
                None,
                False
            ),
            (
                [
                    # prova do semestre todo
                    re.compile('(p|P)1.*p2.*ex'),
                ],
                TipoAvaliacao.objects.get(nome='Compilado de avaliações'),
                None,
                False
            ),
            (
                [
                    # lista com resolução
                    re.compile('(l|L).*(\d).*(res)'),
                    re.compile('(l|L).*(\d).*(gab)'),
                    re.compile('(l|L).*(\d).*(sol)'),
                ],
                TipoAvaliacao.objects.get(nome='Lista de exercícios'),
                2,
                True
            ),
            (
                [
                    # lista com resolução sem quantificador
                    re.compile('(l|L).*(res)'),
                    re.compile('(l|L).*(gab)'),
                    re.compile('(l|L).*(sol)'),
                ],
                TipoAvaliacao.objects.get(nome='Lista de exercícios'),
                None,
                True
            ),
            (
                [
                    # lista sem resolução
                    re.compile('(l|L).*(\d)'),
                ],
                TipoAvaliacao.objects.get(nome='Lista de exercícios'),
                2,
                False
            ),
            (
                [
                    # lista sem resolução sem quantificador
                    re.compile('(l|L).*'),
                ],
                TipoAvaliacao.objects.get(nome='Lista de exercícios'),
                None,
                False
            ),
            (
                [
                    # exercício capítulo X com resolução
                    re.compile('(ex).*(cap).*(\d).*(res)'),
                    re.compile('(ex).*(cap).*(\d).*(gab)'),
                    re.compile('(ex).*(cap).*(\d).*(sol)'),
                ],
                TipoAvaliacao.objects.get(nome='Exercícios do capítulo'),
                3,
                True
            ),
            (
                [
                    # exercício capítulo X sem resolução
                    re.compile('(ex).*(cap).*(\d)'),
                ],
                TipoAvaliacao.objects.get(nome='Exercícios do capítulo'),
                3,
                False
            ),
            (
                [
                    # exercício com resolução
                    re.compile('(ex).*(\d).*(res)'),
                    re.compile('(ex).*(\d).*(gab)'),
                    re.compile('(ex).*(\d).*(sol)'),
                    # atividade com resolução
                    re.compile('(at).*(\d).*(res)'),
                    re.compile('(at).*(\d).*(re)'), # nome esquisito
                ],
                TipoAvaliacao.objects.get(nome='Exercício de avaliação'),
                2,
                True
            ),
            (
                [
                    # exercício sem resolução
                    re.compile('(ex).*(\d)'),
                    # atividade sem resolução
                    re.compile('(at).*(\d)'),
                ],
                TipoAvaliacao.objects.get(nome='Exercício de avaliação'),
                2,
                False
            ),
            (
                [
                    # exercício sem resolução e sem quantificador
                    re.compile('(exe).*'),
                ],
                TipoAvaliacao.objects.get(nome='Exercício de avaliação'),
                None,
                False
            ),
            (
                [
                    # exame com resolução
                    re.compile('(exa).*(res)'),
                    re.compile('(exa).*(sol)'),
                    re.compile('(exa).*(gab)'),
                    # exame com resolução (nome ambíguo)
                    re.compile('(ex).*(res)'),
                    re.compile('(ex).*(gab)'),
                    re.compile('(ex).*(sol)'),
                ],
                TipoAvaliacao.objects.get(nome='Exame'),
                None,
                True
            ),
            (
                [
                    # exame sem resolução
                    re.compile('(exa).*'),
                    re.compile('(Exa).*'),
                    # exame sem resolução (nome ambíguo)
                    re.compile('(ex).*'),
                    # exame diurno sem resolução
                    re.compile('(exa).*(d|D)'),
                    # exame noturno sem resolução
                    re.compile('(exa).*(n|N)'),
                ],
                TipoAvaliacao.objects.get(nome='Exame'),
                None,
                False
            ),
            (
                [
                    # teste com resolução
                    re.compile('(t|T).*(\d).*(res)'),
                    re.compile('(t|T).*(\d).*(sol)'),
                    re.compile('(t|T).*(\d).*(gab)'),
                    re.compile('(quiz).*(\d).*(res)'),
                    re.compile('(quiz).*(\d).*(sol)'),
                    re.compile('(quiz).*(\d).*(gab)'),
                ],
                TipoAvaliacao.objects.get(nome='Testinho'),
                2,
                True
            ),
            (
                [
                    # teste sem resolução
                    re.compile('(t|T).*(\d)'),
                ],
                TipoAvaliacao.objects.get(nome='Testinho'),
                2,
                False
            ),
            (
                [
                    # anotações de aula
                    re.compile('(anot).*'),
                ],
                TipoAvaliacao.objects.get(nome='Anotações de aula'),
                None,
                False
            ),
        ]

        """Função para avaliar se a string é permitida por alguma das várias expressões regulares."""
        def valida_expressao(lista_expressoes, string):
            # Conferimos se a string valida alguma expressão regular
            for expressao in lista_expressoes:
                match = expressao.match(string)
                # Se validou essa expressão, retornamos True
                if match is not None:
                    return (True, match)
            # Se não validou nenhuma, retornamos
            return (False, None)

        # Lista de provas que não passaram nos testes
        provas_falhadas = []
        # Lista de provas que inserimos
        aval_inseridas = []

        # Determinamos as características da prova
        for prova in provas_json:

            # Obtemos o código da disciplina
            codigo_string = prova['codigo_disciplina'].lower().replace(' ', '')
            # Conferimos se o código é válido
            if re_codigo_disc.match(codigo_string) is None:
                provas_falhadas.append(prova)
                continue
            # Conferimos se o código cabe no banco de dados
            if len(codigo_string) > settings.MAX_LENGTH_CODIGO_DISCIPLINA:
                provas_falhadas.append(prova)
                continue

            # Obtemos o período de aplicação da prova
            # OBS: .match().group(0) é a match inteira (trecho todo)
            periodo_string = prova['periodo']
            ano = None
            periodo = None
            # Tentamos com "ano semestre"
            match_periodo = re_periodo_ano_sem.match(periodo_string)
            if match_periodo is not None:
                # Pegamos o primeiro ou segundo semestre
                if int(match_periodo.group(2)) == 1:
                    periodo = periodo_1sem
                elif int(match_periodo.group(2)) == 2:
                    periodo = periodo_2sem
                elif int(match_periodo.group(2)) == 3: # caso especial para prova da marina de ME210
                    periodo = periodo_2sem
                else:
                    provas_falhadas.append(prova)
                    continue
                # Pegamos o ano
                ano = int(match_periodo.group(1))
            # Tentamos com "semestre ano"
            match_periodo = re_periodo_sem_ano.match(periodo_string)
            if match_periodo is not None:
                # Pegamos o primeiro ou segundo semestre
                if int(match_periodo.group(1)) == 1:
                    periodo = periodo_1sem
                elif int(match_periodo.group(1)) == 2:
                    periodo = periodo_2sem
                else:
                    provas_falhadas.append(prova)
                    continue
                # Pegamos o ano
                ano = int(match_periodo.group(2))
            # Tentamos com "ano férias"
            match_periodo = re_periodo_ano_fer.match(periodo_string)
            if match_periodo is not None:
                # Pegamos o período de férias
                periodo = periodo_fer
                # Pegamos o ano
                ano = int(match_periodo.group(1))
            # Tentamos com "ano"
            match_periodo = re_periodo_ano.match(periodo_string)
            if match_periodo is not None:
                # Pegamos o ano
                ano = int(match_periodo.group(1))
            # Conferimos range do ano caso existir (018 não vale)
            if (ano is not None and ano not in range(1960, 2020)):
                provas_falhadas.append(prova)
                continue

            # Obtemos o tipo de avaliação
            tipo_avaliacao = None
            quantificador = None
            possui_resolucao = None
            # Procuramos o tipo que se encaixa
            for (exp_regs, tipo, indice_quantif, resolucao) in re_tipos:
                match = None
                # Procuramos em todas as expressões regulares
                for exp_reg in exp_regs:
                    match = exp_reg.match(prova['tipo_avaliacao'])
                    if match is not None:
                        break
                    else:
                        match = None
                # Se encontramos algum, definimos parâmetros e paramos
                if match is not None:
                    tipo_avaliacao = tipo
                    possui_resolucao = resolucao
                    if indice_quantif is not None:
                        quantificador = match.group(indice_quantif)
                    break
            # Conferimos se foi possível definir o tipo da prova
            if tipo_avaliacao is None:
                provas_falhadas.append(prova)
                continue

            # Obtemos o nome do docente
            docente = prova['docente'].lower().replace(' ', '_').replace('-', '_').replace('.', '')
            if len(docente) == 0:
                docente = None
            if (docente is not None and re_docentes.match(docente) is None):
                # Para possivelmente identificar caractere inválido
                print('Docente inválido: "{0}"'.format(docente))
                docente = None
            # Conferimos se o nome cabe no banco de dados
            if (docente is not None and len(docente) > settings.MAX_LENGTH_DOCENTE):
                provas_falhadas.append(prova)
                continue

            # Salvamos o código da disciplina
            try:
                codigo_disciplina = CodigoDisciplina.objects.get(
                    codigo=codigo_string
                )
                # Se o código já foi registrado, basta pegar a disciplina correspondente
                disciplina = codigo_disciplina.disciplina
            except ObjectDoesNotExist:
                # Se não há código registrado, precisamos criar uma nova
                # Criamos uma nova disciplina autorizada pois estamos importando
                disciplina = Disciplina(
                    autorizada=True
                )
                disciplina.save()
                # Agora criamos um nome para a disciplina
                # Consideramos o nome como o mais atualizado
                codigo_disciplina = CodigoDisciplina(
                    disciplina=disciplina,
                    nome_atualizado=True,
                    codigo=codigo_string.lower()
                )
                codigo_disciplina.save()

            # Obtemos o nome do arquivo (como em models.determinar_nome_arquivo)
            if quantificador is None:
                quantificador_str = ''
            else:
                quantificador_str = str(quantificador)
            # Começamos com a lista de atributos obrigatórios
            id_disciplina = str(disciplina.id)
            atributos = [
                id_disciplina,
                tipo_avaliacao.nome + quantificador_str,
            ]
            # Incluímos com o número de opcionais
            if docente is not None:
                atributos.append(docente)
            if periodo is not None:
                atributos.append(periodo.nome)
            if ano is not None:
                atributos.append(str(ano))
            # Criamos um trecho aleatório
            atributos.append(str(uuid.uuid4()))
            # Pegamos a extensão do nome do arquivo
            split = prova['arquivo'].split('.')
            if len(split) > 1:
                extensao_str = '.' + split[len(split) - 1].replace(' ', '')
            else:
                extensao_str = '.extensao_desconhecida'
            arquivo = settings.PROVAS_PATH + slugify('-'.join(atributos)) + extensao_str
            # Conferimos se o nome do arquivo cabe no banco de dados
            if len(arquivo) > settings.MAX_LENGTH_NOME_ARQUIVO:
                provas_falhadas.append(prova)
                continue

            # Agora inserimos a avaliação
            avaliacao = Avaliacao(
                disciplina=disciplina,
                docente=docente,
                tipo_avaliacao=tipo_avaliacao,
                quantificador_avaliacao=quantificador,
                periodo=periodo,
                ano=ano,
                possui_resolucao=possui_resolucao,
                arquivo=arquivo,
                visivel=True
            )
            aval_inseridas.append(avaliacao)

            print('Docente:', '"{0}" -> "{1}"'.format(prova['docente'], docente if docente is not None else ''))
            print('Códico disciplina:', '"{0}" -> "{1}"'.format(prova['codigo_disciplina'], codigo_string))
            print('Período:', '"{0}" -> {1} - {2}'.format(prova['periodo'], ano, periodo))
            print('Tipo:', '"{0}" -> {1} {2}, {3}'.format(prova['tipo_avaliacao'], tipo_avaliacao, quantificador, 'possui res.' if possui_resolucao else 'não possui res.'))
            print('Arquivo:', '"{0}" -> "{1}"'.format(prova['arquivo'], arquivo))
            avaliacao.save()
            # Copiamos o arquivo para o novo caminho
            shutil.copy(os.path.join(old_media_root, prova['arquivo']), os.path.join(settings.MEDIA_ROOT, arquivo))
            print()

        print()
        print(len(provas_falhadas), 'provas falhadas:')
        for prova in provas_falhadas:
            print('\t', prova['arquivo'])
        print()

        print('Salvamos', len(aval_inseridas), 'provas')
