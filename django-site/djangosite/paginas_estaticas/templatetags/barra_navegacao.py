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
                    # Não mostramos itens desativados neste caso (não fica bonito)
                    if not dropdown.desativado:
                        # Determinamos o endereço do item dropdown
                        if dropdown.endereco is not None:
                            endereco = dropdown.endereco
                        else:
                            endereco = dropdown.pagina.endereco
                        # Imprimimos o item
                        resultado += """<a class="dropdown-item {2}" href="{1}">{0}</a>""".format(dropdown.nome, endereco, '' if endereco != url else 'active')

                # Terminamos o dropdown
                resultado += \
                    """</div>
                    </li>"""

        # Menus que não são dropdown
        else:
            # Se está desativado, desativamos mas ainda mostramos
            if menu.desativado:
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link disabled">{0}</a>
                    </li>""".format(menu.nome)
            else:
                # Como item de dropdown, determinamos o endereço
                if menu.endereco is not None:
                    endereco = menu.endereco
                else:
                    endereco = menu.pagina.endereco
                # Adicionamos o item conferindo endereço
                resultado += \
                    """<li class="nav-item">
                      <a class="nav-link {2}" href="{1}">{0}</a>
                    </li>""".format(menu.nome, endereco, '' if endereco != url else 'active')

    return resultado
