from django.shortcuts import render

from .models import *

def PaginaEstaticaView(request, pk):
    pagina = PaginaEstatica.objects.get(pk=pk)
    context = {
        # Para substituirmos as infrmações da página em 'templates/padrao.html'
        'pagina': pagina
    }

    return render(request, 'padrao.html', context=context)
