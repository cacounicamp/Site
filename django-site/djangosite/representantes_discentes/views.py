from django.shortcuts import render
from django.conf import settings
from django.http import Http404

from util import util
from .models import RepresentanteDiscente


def RepresentantesDiscentesPagina(request, pagina=1):
    # objects vai retornar um dicionário cuja chave é 'ano_atuacao'
    return util.pegar_pagina(
        request, RepresentanteDiscente.objects.values('ano_atuacao').distinct('ano_atuacao'), 'representantes_discentes_pagina.html',
        settings.REPRESENTANTES_DISCENTES_ANOS_POR_PAGINA, pagina
    )


def RepresentantesDiscentesAno(request, ano_atuacao):
    # Pegamos os representantes deste ano
    representantes = RepresentanteDiscente.objects \
                     .order_by(
                        'comissao__instituicao__nome',
                        'comissao__nome',
                        '-titular',
                        'nome'
                     ) \
                     .filter(ano_atuacao=ano_atuacao) \
                     .all()

    # Se não há representantes registrados, retornamos 404
    if len(representantes) == 0:
        raise Http404('Representantes não registrados!')

    # Fazemos a estrutura para formar a página mais facilmente
    unidade_cargos_representantes = {}
    for representante in representantes:
        # Criamos variáveis
        comissao = representante.comissao
        instituicao = comissao.instituicao

        # Colocamos toda unidade que não está no dicionário
        if instituicao not in unidade_cargos_representantes:
            unidade_cargos_representantes[instituicao] = {}
            # Agora garantimos que a instituição está inicializada

        # Colocamos toda comissão que não está no dicionário
        if comissao not in unidade_cargos_representantes[instituicao]:
            unidade_cargos_representantes[instituicao][comissao] = []
            # Agora garantimos que a comissão possui uma lista de representantes

        # Adicionamos os representantes
        unidade_cargos_representantes[instituicao][comissao].append(representante)

    # Imprimimos a página
    context = {
        'unidade_cargos_representantes': unidade_cargos_representantes,
        'ano_atuacao': ano_atuacao,
        'email_contato': settings.EMAIL_CONTATO_DISPLAY,
    }
    return render(request, 'representantes_discentes_ano.html', context=context)
