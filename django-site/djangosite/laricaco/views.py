import requests

from xml.dom import minidom

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from util import util
from .forms import LariCACoForm
from paginas_estaticas.models import PaginaEstatica


def LariCACoView(request):

    def preparar_pagina(form):
        # Preparamos a página para ser servida
        try:
            # Verificamos se há uma página estática
            pagina = PaginaEstatica.objects.get(endereco='/laricaco/')
        except ObjectDoesNotExist:
            pagina = None

        # Preparamos os dados para renderizar a página
        context = {
            'captcha_site_key': settings.CAPTCHA_SITE_KEY,
            'pagina': pagina,
            'form': form
        }
        # Servimos a página
        return render(request, 'laricaco.html', context)


    # Conferimos se estamos recebendo ou enviando a página
    if request.method != 'POST':

        # Pegamos um formulário para ser preenchido e servimos a página
        return preparar_pagina(LariCACoForm())

    else:

        # Estamos recebendo formulário
        form = LariCACoForm(request.POST)

        # Conferimos o Recaptcha
        if not util.recaptcha_valido(request):
            # Avisamos o usuário
            messages.add_message(
                request, messages.SUCCESS,
                'Recaptcha inválido! Atualize a página e tente novamente mais tarde.',
                extra_tags='danger'
            )

            # Mostramos a página com a mensagem de erro
            return preparar_pagina(form)

        # Se o Recaptcha está correto, continuamos processando o formulário
        # Verificamos se é válido
        if not form.is_valid():
            # Caso o formulário não for preenchido corretamente, avisamos
            form.add_error(
                None,
                'O formulário não foi preenchido corretamente!'
            )

            # Redirecionamos ao formulário
            return preparar_pagina(form)

        # Se o formulário está correto, continuamos...
        valor = float(form.cleaned_data['valor'])
        valor_extra = round(
            valor * settings.LARICACO_TAXA_PORCENTAGEM + settings.LARICACO_TAXA_CONSTANTE,
            2
        )

        # Determinamos URL da API do PagSeguro
        url = util.pagseguro_api_url('v2/checkout')
        # Determinamos os parâmetros
        parametros = {
            'currency': 'BRL',
            # Não permitem acentos
            'itemId1': 'Credito para LariCACo',
            'itemDescription1': 'Credito de R${0:.2f} para ser utilizado no LariCACo.'.format(valor),
            'itemAmount1': '{0:.2f}'.format(valor),
            'itemQuantity1': 1,
            'itemWeight1': 0,
            'shippingAddressRequired': 'false',
            'receiverEmail': 'caco@ic.unicamp.br',
            'extraAmount': '{0:.2f}'.format(valor_extra)
        }
        # Passamos ao PagSeguro a compra e recebemos o código para continuar
        retorno = requests.post(url, data=parametros)
        try:
            retorno.raise_for_status()
        except HttpError:
            # Se não conseguimos um status OK, mostramos ao usuário que pelo
            # menos tentamos
            raise

        # Pegamos código da resposta
        # "<code>codigo</code>" -> código é um nó do tipo "#text" cujo valor é
        # o código
        codigo = minidom.parseString(retorno.text).getElementsByTagName('code')[0].firstChild.nodeValue
        # Pegamos URL para redirecionar
        url_redirect = util.pagseguro_url('v2/checkout/payment.html?code={0}'.format(codigo))

        # Redirecionamos usuário
        return redirect(url_redirect)
