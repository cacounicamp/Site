import datetime

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from .models import Membro


def exemplo_ano():
    hoje = datetime.datetime.now()
    return 'Exemplos: "{ano}", "{ano_anterior}"'.format(ano=hoje.year, ano_anterior=(hoje.year - 2))


def concordo_com_estatuto():
    return mark_safe('Li e concordo com o <a href="{url}">estatuto do CACo</a>*:'.format(url=settings.ESTATUTO_URL))


class FormularioVinculo(forms.Form):
    # Nome do membro
    nome = forms.CharField(required=True, label='Nome completo*:', max_length=settings.MAX_LENGTH_NOME)

    # Registro acadêmico do membro
    registro_academico = forms.IntegerField(required=True, label='Seu registro acadêmico (RA)*:', min_value=0)

    # E-mail institucional do membro (é obrigatório)
    email_institucional = forms.EmailField(required=True, label='E-mail institucional*:', help_text='Deve ser do Instituto da Computação (IC) da Unicamp. Será usado para confirmação e deve coincidir com seu RA.', max_length=settings.MAX_LENGTH_EMAIL)

    # E-mail de contato do membro (não é obrigatório)
    email = forms.EmailField(required=False, label='E-mail de contato:', help_text='O que você lê com mais frequência. Por exemplo, Gmail, Outlook.', max_length=settings.MAX_LENGTH_EMAIL)

    # Anode ingresso do membro
    ano_ingresso = forms.DateField(required=True, label='Ano de ingresso*:', help_text=exemplo_ano(), input_formats=['%Y'])

    # Curso do membro
    curso = forms.ChoiceField(required=True, label='Curso*:', choices=settings.CURSOS)

    concordo = forms.BooleanField(required=True, label=concordo_com_estatuto())

    def clean_email_institucional(self):
        email = self.cleaned_data['email_institucional']

        if not email.split('@')[1].endswith('ic.unicamp.br'):
            raise forms.ValidationError(
                'E-mail institucional deve ser do Instituto da Computação (IC)! Se acredita que isso é um engano, envie-nos uma mensagem pela página de contato',
                code='invalid'
            )

        return email


class FormularioDesvinculo(forms.Form):
    # Registro acadêmico do membro
    registro_academico = forms.IntegerField(required=True, label='Seu registro acadêmico (RA)*:', min_value=0)

    # Ano de ingresso do membro
    ano_ingresso = forms.DateField(required=True, label='Ano de ingresso*:', help_text=exemplo_ano(), input_formats=['%Y'])


class FormularioConfirmarAcao(forms.Form):
    # Se o usuário confirmou a ação desejada
    acao_confirmada = forms.BooleanField(required=True, label='Confirmar ação', help_text='Se você leu, aceita o estatuto e deseja confirmar a ação do token enviado por e-mail.')


class FormularioAdminResetar(forms.Form):
    resetar = forms.BooleanField(required=True, label='Resetar lista', help_text='Se você quer mesmo resetar a lista de membros do centro acadêmico, marque essa caixa.')
