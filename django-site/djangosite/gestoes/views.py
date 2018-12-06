from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.http import Http404
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

from .models import Gestao, Membro


def GestaoView(request, ano_eleito, nome=None):
    try:
        # Encontramos a gestão do ano requisitado
        gestao = Gestao.objects.get(ano_eleito=ano_eleito)

        # Conferimos se o nome está correto no slug
        slug_nome = slugify(gestao.nome)
        if nome != slug_nome:
            return redirect(reverse('gestao/', args=[ano_eleito, slug_nome]))
    except ObjectDoesNotExist:
        # Caso não encontramos, retornamos 404
        raise Http404('Gestão não encontrada!')

    # Fazemos a lista de membros da gestão
    membros = Membro.objects.filter(gestao=gestao).order_by('cargo__nome', 'nome').all()

    # Fazemos o dicionário de pessoas pelo cargo
    cargo_membros = {}
    for membro in membros:
        # Conferimos se o cargo do membro está no dicionário
        if not membro.cargo in cargo_membros:
            # Se não estiver, adicionamos com uma lista com um único membro
            cargo_membros[membro.cargo] = [membro]
        else:
            # Se estiver, adicionamos a lista
            cargo_membros[membro.cargo].append(membro)

    # Como deu tudo certo, imprimimos a página
    context = {
        # O modelo da gestão
        'gestao': gestao,
        # Estrutura de gestões (dicionário cuja chave é cargo e valor é lista de
        # pessoas)
        'cargo_membros': cargo_membros,
        'membros': len(membros)
    }
    return render(request, 'gestao.html', context=context)


def GestoesView(request, pagina=1):
    pass
