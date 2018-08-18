from django.db import models
from django.core.exceptions import ValidationError

class PaginaEstatica(models.Model):
    # Título da página (aparecerá no nome do endereço)
    titulo = models.CharField(max_length=32, null=False)
    # URL da página
    endereco = models.CharField(unique=True, max_length=200, null=False)
    # Conteúdo da página
    conteudo = models.TextField(blank=True)

    def __str__(self):
        return "'" + self.titulo + "' em '" + self.endereco + "'"

    class Meta:
        verbose_name = "página estática"
        verbose_name_plural = "páginas estáticas"
        ordering = ['endereco']

class MenuManager(models.Manager):
    def get_itens(self):
        elementos = {}

        # Inserimos os dropdowns visíveis
        for item in MenuDropdown.objects.all():
            if not item.visivel:
                continue
            elementos[item] = []

        # Inserimos as opções visíveis
        for item in ItemMenu.objects.all():
            if not item.visivel:
                continue

            if item.dropdown is not None:
                # Verificamos se o dropdown está visível
                if item.dropdown in elementos:
                    elementos[item.dropdown].append(item)
            else:
                elementos[item] = None

        # Ordenamos dentro dos dropdowns e fora
        for chave, valor in elementos.items():
            if valor is not None:
                sorted(valor, key=lambda item: item.indice)
        sorted(elementos, key=lambda item: item.indice)

        return elementos

class ItemMenuAbstrato(models.Model):
    objects = MenuManager()
    # Identificador do item (para podermos criar itens com mesmo nome,
    # diferentes endereços e visibilidades)
    id = models.AutoField(primary_key=True)
    # Ordem que aparecerá na página
    indice = models.IntegerField(null=False)
    # Nome que será exposto ao público
    nome = models.CharField(max_length=32, null=False)
    # Se aparecerá na página
    visivel = models.BooleanField(default=False)
    # Se aparecerá de forma não clicável
    desativado = models.BooleanField(default=False)

    def __str__(self):
        return "'" + self.nome + "' (" + str(self.id) + ")"

    class Meta:
        abstract = True

class MenuDropdown(ItemMenuAbstrato):
    class Meta:
        verbose_name = "item dropdown do menu"
        verbose_name_plural = "itens dropdown do menu"
        ordering = ['indice']

class ItemMenu(ItemMenuAbstrato):
    # Colocamos a opção de páginas estáticas permitindo null
    pagina = models.ForeignKey(
        PaginaEstatica, null=True, blank=True, on_delete=models.CASCADE
    )
    # O endereço que o item possuirá caso não possua página
    endereco = models.CharField(max_length=200, null=True, blank=True)
    # Cada ItemMenu pode ter apenas um MenuDropdown (cada MenuDropdown pode
    # possuir vários ItemMenu)
    dropdown = models.ForeignKey(
        MenuDropdown, null=True, blank=True, on_delete=models.SET_NULL
    )

    def clean(self):
        if self.endereco is None and self.pagina is None:
            raise ValidationError('O item ou deve possuir um endereço ou deve possuir uma página associada.')

    class Meta:
        verbose_name = "item do menu"
        verbose_name_plural = "itens do menu"
        ordering = ['indice']