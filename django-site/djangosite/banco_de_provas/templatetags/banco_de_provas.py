from django import template


# Registramos a tag
register = template.Library()

@register.filter
def field_obrigatorio(campo):
    return campo.field.required or campo.label.endswith('*')
