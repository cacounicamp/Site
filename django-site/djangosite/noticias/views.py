from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.http import Http404
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

from util import util
from .models import Noticia


def NoticiaDetalheView(request, identificador, titulo=None):
    try:
        # Encontramos a notícia pelo identificador (não pelo nome)
        noticia = Noticia.objects.get(pk=identificador)

        # Conferimos se devemos mostrar essa notícia
        if not noticia.visivel:
            raise ObjectDoesNotExist()

        # Conferimos se precisamos corrigir a URL
        titulo_slug = slugify(noticia.titulo)
        if titulo != titulo_slug:
            # Se o nome está incorreto, redirecionamos ao certo
            return redirect(reverse('noticia/', args=[identificador, titulo_slug]))
    except ObjectDoesNotExist:
        # Caso não encontramos a notícia ou não é visível, retornamos not found
        raise Http404('Notícia não existe!')

    # Caso encontramos e não há erro, mostramos a notícia
    context = {
        'noticia': noticia
    }
    return render(request, 'noticia_detalhe.html', context=context)


def NoticiasView(request, pagina=1):
    return util.pegar_pagina(request, Noticia, settings.NOTICIAS_POR_PAGINA, pagina, 'noticias.html')


# Caso especial para a primeira página do site: menos notícias, aparecem por
# completo
def NoticiasRaizView(request, pagina=1):
    return util.pegar_pagina(request, Noticia, settings.NOTICIAS_POR_PAGINA_RAIZ, pagina, 'noticias_raiz.html')
