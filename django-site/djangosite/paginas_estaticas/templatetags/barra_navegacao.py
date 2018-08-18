from django import template
from django.urls import reverse

from ..models import MenuManager, MenuDropdown, ItemMenu

# Registramos a tag
register = template.Library()

@register.tag
def imprime_barra_navegacao(url):
    resultado = ""
    itens = ItemMenu.objects.get_itens()

    for menu, lista_dropdowns in itens:
        if len(lista_dropdowns) > 0:
            if menu.desativado:
                resultado += \
                    """<li class="nav-item dropdown">
                      <a class="nav-link disabled">{0}</a>
                    </li>""".format(pagina.nome)
            else:
                resultado += \
                    """<li class="nav-item dropdown">
                          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">{0}</a>
                          <div class="dropdown-menu" aria-labelledby="navbarDropdown">"""

                for dropdown in lista_dropdowns:
                    if not dropdown.desativado:
                        if dropdown.endereco is not None:
                            resultado += """<a class="dropdown-item" href="{1}">{0}</a>""".format(dropdown.nome, dropdown.endereco)
                        else:
                            url_reverso = reverse(dropdown.pagina.endereco)
                            resultado += """<a class="dropdown-item {2}" href="{1}">{0}</a>""".format(dropdown.nome, url_reverso, '' if url_reverso is not url else 'active')

                # Terminamos o dropdown
                resultado += \
                    """</div>
                    </li>"""

        # Menus que não são dropdown
        else:
            if pagina.desativado:
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link disabled">{0}</a>
                    </li>""".format(pagina.nome)
            elif pagina.endereco is not None:
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link" href="{1}">{0}</a>
                    </li>""".format(pagina.nome, pagina.endereco)
            else:
                url_reverso = reverse(pagina.pagina.endereco)
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link {2}" href="{1}">{0}</a>
                    </li>""".format(pagina.nome, url_reverso, '' if url_reverso is not url else 'active')
