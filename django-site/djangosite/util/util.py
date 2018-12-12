import math
import requests

from django.http import Http404
from django.conf import settings
from django.shortcuts import render, redirect


RECAPTCHA_URL = 'https://www.google.com/recaptcha/api/siteverify'


def recaptcha_valido(request):
    # Pegamos da request o código do usuário
    recaptcha_resposta = request.POST.get('g-recaptcha-response')

    dados = {
        'secret': settings.CAPTCHA_SECRET_KEY,
        'response': recaptcha_resposta
    }
    # Verificamos o Recaptcha
    recaptcha_resultado = requests.post(RECAPTCHA_URL, data=dados).json()

    # Imprimimos o resultado do recaptcha se estivermos em DEBUG
    if settings.DEBUG:
        print('Resultado do recaptcha: "{}"'.format(recaptcha_resultado))

    # Retornamos o resultado
    return recaptcha_resultado['success']


def pegar_pagina(request, objects, pagina_html, itens_por_pagina, pagina_atual, context={}):
    # Eliminamos páginas inexistentes
    if pagina_atual <= 0:
        raise Http404('Página inexistente!')

    # Calculamo o número de páginas
    num_objetos = objects.count()
    num_paginas = math.ceil(num_objetos / itens_por_pagina)

    # Eliminamos páginas inexistentes
    if pagina_atual > num_paginas:
        raise Http404('Página inexistente!')

    indice_inicio = (pagina_atual - 1) * itens_por_pagina
    indice_fim = pagina_atual * itens_por_pagina
    objetos = objects.all()[indice_inicio : indice_fim]

    # Mostramos a página
    context['possui_mais_antiga'] = (pagina_atual < num_paginas)
    context['possui_mais_recente'] = (pagina_atual > 1)
    context['pagina_atual'] = pagina_atual
    context['objetos'] = objetos

    return render(request, pagina_html, context=context)
