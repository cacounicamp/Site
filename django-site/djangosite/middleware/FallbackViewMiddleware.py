from django.conf import settings

from paginas_estaticas import views


class FallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Conferimos se não encontramos algo
        if response.status_code == 404:
            if settings.DEBUG:
                print('404 detectado em', request.path, 'redirecionando para página estática procurar.')
            # Verificamos se conseguimos uma resposta
            view_response = views.PaginaEstaticaEnderecoView(request, request.path)
            # Se não é nula nossa resposta, retornamos ela
            if view_response is not None:
                return view_response

        return response
