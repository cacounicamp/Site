# Para os erros ao enviar e-mail
from smtplib import SMTPException

from django.http import Http404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from paginas_estaticas.models import PaginaEstatica

from .models import Avaliacao, CodigoDisciplina, Disciplina, Periodo, TipoAvaliacao
from .forms import FormAvaliacao


def BancoDeProvasView(request):
    try:
        # Tentamos conseguir a página estática de membros para vincularem-se
        pagina = PaginaEstatica.objects.get(endereco='banco-de-provas/')
    except ObjectDoesNotExist:
        pagina = None

    # Pegamos os dados da query
    busca = request.GET.get('busca')

    if busca is None:
        avaliacoes = None
    else:
        # Buscamos todos os códigos de disciplinas
        disciplinas = []
        codigos = CodigoDisciplina.objects.filter(codigo__icontains=busca).all()
        for codigo in codigos:
            disciplinas.append(codigo.disciplina)

        # Buscamos as avaliações com qualquer combinação desses dados
        avaliacoes = Avaliacao.objects.filter(
            Q(disciplina__in=disciplinas) | \
            Q(docente__icontains=busca) | \
            Q(tipo_avaliacao__nome__icontains=busca) | \
            Q(quantificador_avaliacao__icontains=busca) | \
            Q(periodo__nome__icontains=busca) | \
            Q(ano__icontains=busca),
            # Filtramos as avaliações visíveis
            visivel=True
        ).all()[0:settings.MAX_LENGTH_MAX_AVALIACOES]

    # Servimos a página
    context = {
        'pagina': pagina,
        'busca': busca,
        'avaliacoes': avaliacoes,
    }
    return render(request, 'banco_de_provas.html', context=context)


def SubmeterProvaView(request):
    pass
