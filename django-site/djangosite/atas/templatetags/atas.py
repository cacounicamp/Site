from django import template

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

