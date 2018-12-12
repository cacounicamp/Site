from django.http import Http404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from paginas_estaticas.models import PaginaEstatica
from util import util

from .models import Membro
from .forms import FormularioVinculo, FormularioDesvinculo


def MembrosView(request):
    try:
        # Tentamos conseguir a página estática de membros para vincularem-se
        pagina = PaginaEstatica.objects.get(endereco='membros/vincular-se/')
    except ObjectDoesNotExist:
        pagina = None

    # Pegamos os membros
    membros = Membro.objects.exclude(data_confirmacao__isnull=True).all()

    # Servimos a página
    context = {
        'pagina': pagina,
        'membros': membros,
    }
    return render(request, 'membros.html', context=context)


def MembroConfirmarAcaoView(request, token):
    # Procuramos o usuário com o token
    try:
        membro = Membro.objects.get(token_uuid=token)
    except ObjectDoesNotExist:
        membro = None

    # Conferimos se o token é ativo ainda
    if not membro.possui_token_ativo():
        # Deixamos um aviso de que o token venceu
        messages.add_message(
            request, messages.WARNING,
            'Token vencido!',
            extra_tags='danger'
        )
    else:
        # Temos um token não vencido, executamos a ação
        if membro.token_acao == 'REG':
            # Confirmamos
            membro.data_confirmacao = timezone.now()

            # Apagamos o token (isso salva o membro)
            membro.apagar_token()

            # Definimos a mensagem
            mensagem = 'Membro vinculado com sucesso!'
        elif membro.token_acao == 'DEL':
            # Apagamos o membro
            membro.delete()

            # Definimos a mensagem
            mensagem = 'Membro desvinculado com sucesso!'
        else:
            # Caso não reconhecemos o token, saímos
            raise Http404('Ação do token não idêntificada!')

        # Adicionamos a mensagem
        messages.add_message(
            request, messages.SUCCESS,
            mensagem,
            extra_tags='success'
        )

    # Redirecionamos à lista de membros
    return redirect(reverse('membros/'))


def MembroVincularView(request):
    # Verificamos se estamos recebendo informação ou temos que servir o
    # formulário
    if request.method == 'POST':

        # Conferimos o Recaptcha
        if not util.recaptcha_valido(request):
            # Avisamos o usuário
            messages.add_message(
                request, messages.ERROR,
                'Recaptcha inválido! Atualize a página e tente novamente mais tarde.',
                extra_tags='danger'
            )

            # Redirecionamos à lista de membros
            return redirect(reverse('membros/'))

        # Pegamos os dados do POST
        form = FormularioVinculo(request.POST)

        # Verificamos se todos os dados respeitam o formulário
        if form.is_valid() and form.cleaned_data['concordo'] is True:

            registro_academico = form.cleaned_data['registro_academico']
            try:
                # Vemos se existe um membro com tal registro acadêmico
                membro = Membro.objects.get(
                    registro_academico=registro_academico
                )
            except ObjectDoesNotExist:
                membro = None

            # Conferimos se o membro existe
            if membro is not None:

                # Conferimos se ele já foi confirmado
                if membro.membro_confirmado():

                    # Deixamos um aviso que o membro já foi confirmado.
                    messages.add_message(
                        request, messages.WARNING,
                        'Você já é membro! Se seu nome não constar na lista abaixo, utilize a página de contato.',
                        extra_tags='warning'
                    )

                    # Redirecionamos à página de membros
                    return redirect(reverse('membros/'))

                elif membro.possui_token_ativo():

                    # Como há token ativo, avisamos que devemos esperar (caso
                    # seja um usuário malicioso)
                    messages.add_message(
                        request, messages.INFO,
                        'Há um membro de mesmo RA com confirmação pendente. Aguarde alguns dias para tentar novamente ou verifique seu e-mail para confirmar a pendência. Se precisar de ajuda, utilize a página de contato.',
                        extra_tags='info'
                    )

                    # Redirecionamos à lista
                    return redirect(reverse('membros/'))

                else:

                    # Como não há nenhum token ativo e o membro não foi
                    # confirmado, refazemos a inscrição
                    membro.delete()
                    membro = None

                    # Fazemos uma mensagem informativa
                    messages.add_message(
                        request, messages.INFO,
                        'Havia um membro de mesmo RA não confirmado, então o seu vínculo foi registrado novamente.',
                        extra_tags='info'
                    )
                    # Continuamos registrando o novo, como se não tivéssemos
                    # encontrado

            # Criamos o modelo de membro
            membro = Membro(
                nome=form.cleaned_data['nome'],

                registro_academico=form.cleaned_data['registro_academico'],

                email_institucional=form.cleaned_data['email_institucional'],
                email=form.cleaned_data['email'],

                ano_ingresso=form.cleaned_data['ano_ingresso'].year,
                curso=form.cleaned_data['curso']
            )

            # Registramos um token de REGistrar vínculo e salvamos o membro
            if membro.registrar_token('REG'):

                # Tentamos enviar o e-mail de confirmação

                # Redirecionamos à 'membros/' com uma mensagem de sucesso
                messages.add_message(
                    request, messages.SUCCESS,
                    'Confira seu e-mail institucional do IC para confirmar-se como membro!',
                    extra_tags='success'
                )
                return redirect(reverse('membros/'))

            else:

                # Se falhamos, mostramos um erro
                raise Http404('Ação inesperada: existe token ativo')

        else:

            # Caso o formulário não for preenchido corretamente, avisamos o
            # membro
            messages.add_message(
                request, messages.ERROR,
                'Para tornar-se membro, é necessário aceitar as condições do estatuto e preencher o formulário corretamente.',
                extra_tags='danger'
            )

            # Redirecionamos ao formulário
            return redirect(reverse('membro/vincular/'))

    else:
        # Se não estamos em POST, temos que servir a página

        try:
            # Tentamos conseguir a página estática de membros para vincularem-se
            pagina = PaginaEstatica.objects.get(endereco='membros/vincular-se/')
        except ObjectDoesNotExist:
            pagina = None

         # Criamos o formulário que estará disponível
        form = FormularioVinculo()

        # Servimos a página
        context = {
            'captcha_site_key': settings.CAPTCHA_SITE_KEY,
            'pagina_titulo': 'Vincular-se ao centro acadêmico',
            'formulario_titulo': 'Formulário de vinculo',
            'pagina': pagina,
            'form': form,
        }
        return render(request, 'membro_formulario.html', context=context)


def MembroDesvincularView(request):
    # Verificamos se estamos recebendo informação ou temos que servir o
    # formulário
    if request.method == 'POST':

        # Conferimos o Recaptcha
        if not util.recaptcha_valido(request):
            # Avisamos o usuário
            messages.add_message(
                request, messages.ERROR,
                'Recaptcha inválido! Atualize a página e tente novamente mais tarde.',
                extra_tags='danger'
            )

            # Redirecionamos à lista de membros
            return redirect(reverse('membros/'))

        # Pegamos os dados do POST
        form = FormularioDesvinculo(request.POST)

        # Verificamos se todos os dados respeitam o formulário
        if form.is_valid():

            registro_academico = form.cleaned_data['registro_academico']
            try:
                # Vemos se existe um membro com tal registro acadêmico
                membro = Membro.objects.get(
                    registro_academico=registro_academico,
                    ano_ingresso=form.cleaned_data['ano_ingresso'].year
                )
            except ObjectDoesNotExist:
                messages.add_message(
                    request, messages.ERROR,
                    'Membro não encontrado! Veja se o nome consta na lista.',
                    extra_tags='danger'
                )

                # Redirecionamos ao formulário
                return redirect(reverse('membros/'))

            # Verificamos se há token ativo
            if membro.possui_token_ativo():
                # Deixamos um aviso
                messages.add_message(
                    request, messages.INFO,
                    'Há um membro de mesmo RA com confirmação pendente. Aguarde alguns dias para tentar novamente ou verifique seu e-mail para confirmar a pendência. Se precisar de ajuda, utilize a página de contato.',
                    extra_tags='info'
                )

                # Redirecionamos ao formulário
                return redirect(reverse('membros/'))

            # Fazemos um token
            if membro.registrar_token('DEL'):

                # Tentamos enviar o e-mail de confirmação

                # Redirecionamos à 'membros/' com uma mensagem de sucesso
                messages.add_message(
                    request, messages.SUCCESS,
                    'Confira seu e-mail institucional do IC para desvincular-se!',
                    extra_tags='success'
                )
                return redirect(reverse('membros/'))

            else:

                # Se falhamos, mostramos um erro
                raise Http404('Ação inesperada: existe token ativo')

        else:

            # Caso o formulário não for preenchido corretamente, avisamos o
            # membro
            messages.add_message(
                request, messages.ERROR,
                'É necessário preencher o formulário corretamente para desvincular-se.',
                extra_tags='danger'
            )

            # Redirecionamos ao formulário
            return redirect(reverse('membro/vincular/'))

    else:
        # Se não estamos em POST, temos que servir a página

        try:
            # Tentamos conseguir a página estática de membros para vincularem-se
            pagina = PaginaEstatica.objects.get(
                endereco='membros/desvincular-se/'
            )
        except ObjectDoesNotExist:
            pagina = None

         # Criamos o formulário que estará disponível
        form = FormularioDesvinculo()

        # Servimos a página
        context = {
            'captcha_site_key': settings.CAPTCHA_SITE_KEY,
            'pagina_titulo': 'Desvincular-se do centro acadêmico',
            'formulario_titulo': 'Formulário de desvinculo',
            'pagina': pagina,
            'form': form,
        }
        return render(request, 'membro_formulario.html', context=context)
