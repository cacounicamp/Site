from django.shortcuts import render

from .models import *

def PaginaEstaticaView(request, pk):
    pagina = PaginaEstatica.objects.get(pk=pk)
    context = {
        'pagina': pagina,
        'paginas_estaticas': ItemMenu.objects.get_itens()
    }

    return render(request, 'flatpages/default.html', context=context)
