import requests

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from paginas_estaticas.models import PaginaEstatica
from .forms import FormContato

recaptcha_url = ''

def ContatoView(request):
    if request.method == 'POST':
        form = FormContato(request.POST)
        if form.is_valid():

            # Verificamos a resposta do recaptcha
            recaptcha_resposta = request.POST.get('g-recaptcha-response')
            print(recaptcha_resposta)
            dados = {
                'secret': settings.CAPTCHA_SECRET_KEY,
                'response': recaptcha_resposta
            }
            recaptcha_resultado = requests.post('https://www.google.com/recaptcha/api/siteverify', data=dados).json()
            print(recaptcha_resultado)

            if recaptcha_resultado['success']:
                # Será enviado para 'contato/sucesso/'
                return redirect('sucesso/')

        # Em caso de falhas, será enviado para 'contato/falha'
        return redirect('falha/')
    else:
        try:
            pagina = PaginaEstatica.objects.get(endereco='contato/')
        except ObjectDoesNotExist:
            pagina = None
        form = FormContato()

        context = {
            'pagina': pagina,
            'captcha_site_key': settings.CAPTCHA_SITE_KEY,
            'form': form
        }

        return render(request, 'contato.html', context=context)
