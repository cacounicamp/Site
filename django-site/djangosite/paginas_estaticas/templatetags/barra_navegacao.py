from django import template
from django.urls import reverse, NoReverseMatch

from ..models import *


# Registramos a tag
register = template.Library()

@register.simple_tag
def imprime_barra_navegacao(url):
    resultado = ""
    itens = ItemMenu.objects.get_itens()

    for menu, lista_dropdowns in itens.items():
        if lista_dropdowns is not None:
            if menu.desativado:
                resultado += \
                    """<li class="nav-item dropdown">
                      <a class="nav-link disabled">{0}</a>
                    </li>""".format(menu.nome)
            else:
                resultado += \
                    """<li class="nav-item dropdown">
                          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">{0}</a>
                          <div class="dropdown-menu" aria-labelledby="navbarDropdown">""".format(menu.nome)

                for dropdown in lista_dropdowns:
                    if not dropdown.desativado:
                        if dropdown.endereco is not None:
                            resultado += """<a class="dropdown-item" href="{1}">{0}</a>""".format(dropdown.nome, dropdown.endereco)
                        else:
                            endereco = dropdown.pagina.endereco
                            resultado += """<a class="dropdown-item {2}" href="{1}">{0}</a>""".format(dropdown.nome, endereco, '' if endereco != url else 'active')

                # Terminamos o dropdown
                resultado += \
                    """</div>
                    </li>"""

        # Menus que não são dropdown
        else:
            if menu.desativado:
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link disabled">{0}</a>
                    </li>""".format(menu.nome)
            elif menu.endereco is not None:
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link {2}" href="{1}">{0}</a>
                    </li>""".format(menu.nome, menu.endereco, '' if menu.endereco != url else 'active')
            else:
                endereco = menu.pagina.endereco
                print('endereço =', endereco, 'url =', url)
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link {2}" href="{1}">{0}</a>
                    </li>""".format(menu.nome, endereco, '' if endereco != url else 'active')

    return resultado
