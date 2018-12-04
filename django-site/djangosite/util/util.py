import math

from django.shortcuts import render, redirect
from django.http import Http404


def pegar_pagina(request, model, itens_por_pagina, pagina_atual, pagina_html):
    # Eliminamos páginas inexistentes
    if pagina_atual <= 0:
        raise Http404('Página inexistente!')

    # Calculamo o número de páginas
    num_objetos = model.objects.count()
    num_paginas = math.ceil(num_objetos / itens_por_pagina)

    # Eliminamos páginas inexistentes
    if pagina_atual > num_paginas:
        raise Http404('Página inexistente!')

    indice_inicio = (pagina_atual - 1) * itens_por_pagina
    indice_fim = pagina_atual * itens_por_pagina
    objetos = model.objects.all()[indice_inicio : indice_fim]

    # Mostramos a página
    context = {
        'possui_mais_antiga': (pagina_atual < num_paginas),
        'possui_mais_recente': (pagina_atual > 1),
        'pagina_atual': pagina_atual,
        'objetos': objetos
    }
    return render(request, pagina_html, context=context)
