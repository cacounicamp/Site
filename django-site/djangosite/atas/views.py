from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.http import Http404
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

from .models import AtaReuniao, AtaAssembleia
from paginas_estaticas.models import PaginaEstatica
from util import util



def AtasView(request):
    # Buscamos as N primeiras atas de assembleia
    atas_reunioes = AtaReuniao.objects.all()[0 : settings.ATAS_POR_PAGINA]

    # Analogamente às de reunião
    atas_assembleias = AtaAssembleia.objects.all()[0 : settings.ATAS_POR_PAGINA]

    # Pegamos a página atas/participe/
    try:
        participe = PaginaEstatica.objects.get(endereco='atas/participe/')
    except ObjectDoesNotExist:
        participe = None

    context = {
        'pagina_participe': participe,
        'atas_reunioes': atas_reunioes,
        'atas_assembleias': atas_assembleias
    }
    return render(request, 'atas.html', context=context)


def AtasAssembleiasView(request, pagina=1):
    return util.pegar_pagina(
        request, AtaAssembleia, 'atas_especificas.html',
        settings.ATAS_ASSEMBLEIA_POR_PAGINA, pagina, context={
            'titulo': 'Atas de assembleias',
            'ata_url': 'ata/assembleia/',
            'atas_pagina_url': 'atas/assembleias/pagina/'
        }
    )


def AtasReunioesView(request, pagina=1):
    return util.pegar_pagina(
        request, AtaReuniao, 'atas_especificas.html',
        settings.ATAS_REUNIAO_POR_PAGINA, pagina, context={
            'titulo': 'Atas de reuniões',
            'ata_url': 'ata/reuniao/',
            'atas_pagina_url': 'atas/reunioes/pagina/'
        }
    )


def pagina_ata_especifica(request, classe_ata, url_retorno, url_especifica, identificador, data):
    try:
        # Encontramos a ata pelo identificador
        ata = classe_ata.objects.get(pk=identificador)

        # Conferimos se precisamos corrigir a URL
        data_slug = slugify(ata.data_criacao)
        if data != data_slug:
            # Se o nome está incorreto, redirecionamos ao certo
            return redirect(reverse(url_especifica, args=[identificador, data_slug]))
    except ObjectDoesNotExist:
        # Caso não encontramos a ata, retornamos not found
        raise Http404('Ata não existe!')

    # Caso encontramos e não há erro, mostramos a ata
    context = {
        'ata': ata,
        'url_retorno': url_retorno
    }
    return render(request, 'ata_especifica.html', context=context)


def AtaAssembleiaView(request, identificador, data=None):
    return pagina_ata_especifica(request, AtaAssembleia, 'atas/assembleias/', 'ata/assembleia/', identificador, data)


def AtaReuniaoView(request, identificador, data=None):
    return pagina_ata_especifica(request, AtaReuniao, 'atas/reunioes/', 'ata/reuniao/', identificador, data)
