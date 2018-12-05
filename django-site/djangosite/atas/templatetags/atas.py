from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

from ..models import AtaReuniao, AtaAssembleia


# Registramos a tag
register = template.Library()

@register.simple_tag
def imprime_tipo_ata(ata):
    if isinstance(ata, AtaAssembleia):
        return AtaAssembleia.display_tipo_ata(ata)
    elif isinstance(ata, AtaReuniao):
        return AtaReuniao.display_tipo_ata(ata)
    else:
        return ""


@register.simple_tag
def cor_alert_ata(ata):
    if isinstance(ata, AtaAssembleia):
        return "danger"
    elif isinstance(ata, AtaReuniao):
        return "warning"
    else:
        return "info"


@register.simple_tag
def ultimas_atas():
    # Pegamos as atas
    reunioes = AtaReuniao.objects.all()[0 : settings.ATAS_BARRA_LATERAL]
    assembleias = AtaAssembleia.objects.all()[0 : settings.ATAS_BARRA_LATERAL]

    # Fazemos uma lista de atas
    atas = []
    atas += reunioes
    atas += assembleias

    # Ordenamos por data
    atas.sort(key=lambda ata: ata.data_criacao, reverse=True)

    # Construímos a saída
    saida = """"""
    # Fazemos uma caixa em volta de tudo
    saida += """<div class="alert alert-secondary rounded shadow-sm">"""
    # Fazemos um header
    saida += """<center><h5>Últimas atas</h5></center>"""
    saida += """<hr>"""
    # Adicionamos apenas algumas atas
    num_atas = 0

    # Para cada ata, formamos um quadrado
    for ata in atas:
        num_atas += 1

        # Variáveis da ata
        base_url = 'ata/{}/'.format('reuniao' if isinstance(ata, AtaReuniao) else 'assembleia')
        url_ata = reverse(base_url, args=[ata.pk, slugify(ata.data_criacao)])

        # Abrimos a linha
        saida += """<div class="row">"""
        # Abrimos a coluna
        saida += """<div class="col">"""
        # Abrimos o alerta
        saida += """<div class="alert alert-{0} shadow-sm" role="alert">""".format(cor_alert_ata(ata))
        # Iniciamos o link
        saida += """<a href="{0}" class="alert-link">""".format(url_ata)

        # Adicionamos o nome da ata
        saida += """<b>{0}</b>""".format(ata)

        # Fechamos o link
        saida += """</a>"""
        # Fechamos o alerta
        saida += """</div>"""
        # Fechamos a coluna
        saida += """</div>"""
        # Fechamos a linha
        saida += """</div>"""

        # Paramos se já adicionamos atas suficientes
        if num_atas >= settings.ATAS_BARRA_LATERAL:
            break

    # Terminamos a caixa
    saida += """</div>"""

    # Imprimimos
    return saida
