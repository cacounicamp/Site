from django import forms
from django.conf import settings


class LariCACoForm(forms.Form):
    valor = forms.DecimalField(
        required=True,
        label='Valor de crédito',
        help_text=' '.join([
            'Valor que poderá utilizar no LariCACo.',
            'Uma taxa de {0}% + R${1:.2f} por utilizar o PagSeguro será cobrada.'.format(
                settings.LARICACO_TAXA_PORCENTAGEM,
                settings.LARICACO_TAXA_CONSTANTE
            ),
        ]),
        max_value=settings.LARICACO_MAX_VALOR,
        min_value=settings.LARICACO_MIN_VALOR,
        decimal_places=2 # por ser dinheiro
    )
