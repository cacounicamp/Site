from django.shortcuts import render

from .models import *

def PaginaEstaticaView(request, pk):
    pagina = PaginaEstatica.objects.get(pk=pk)
    context = {
        'pagina': pagina
    }

    return render(request, 'flatpages/default.html', context=context)
