from django.conf import settings
from django.shortcuts import render, redirect
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .models import *


def PaginaEstaticaEnderecoView(request, endereco):
    try:
        # Se não tem '/' final e precisamos, adicionamos
        precisa_redirecionar = False
        if not endereco.endswith('/') and settings.APPEND_SLASH:
            endereco = "{0}/".format(endereco)
            precisa_redirecionar = True

        # Tentamos buscar a página com mesmo endereço se está ativa
        pagina = PaginaEstatica.objects.get(endereco=endereco, url_ativa=True)

        # Se encontramos uma página e precisamos redirecionar, redirecionamos
        if precisa_redirecionar:
            return redirect(endereco)
    except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
        # Caso não encontramos, retornamos nada para manter o que foi escolhido
        # pelo django inicialmente
        return None

    # Se encontramos, exibimos
    context = {
        # Para substituirmos as infrmações da página em 'templates/padrao.html'
        'pagina': pagina
    }
    return render(request, 'padrao.html', context=context)
