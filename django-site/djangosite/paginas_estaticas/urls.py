from django.contrib import admin
from django.urls import path
from django.db.utils import ProgrammingError

from . import views
from .models import PaginaEstatica

urlpatterns = [
]

# Função prepara todas as URLs de páginas estáticas
def recarregar_urls():
    try:
        urlpatterns.clear()
        # Para cada página dinãmica...
        for pagina in PaginaEstatica.objects.all():
            # Não fazemos o endereço para páginas com URL ativa
            if not pagina.url_ativa:
                continue

            # Registramos a URL
            urlpatterns.append(
                path(
                    # Endereço para o resolver
                    '' if pagina.endereco == '/' else pagina.endereco,
                    # View para a página
                    views.PaginaEstaticaView,
                    # Passamos para a view o primary_key (do banco de dados) para
                    # conseguir a exata página com a melhor performance
                    {'pk': pagina.pk},
                    # Definimos o nome da URL como o próprio endereço, já que é único
                    name=pagina.endereco
                )
            )
    except ProgrammingError:
        pass


# Definimos todas as URLs
recarregar_urls()
