from django.db import models

class MenuManager(models.Manager):
    def get_itens(self):
        elementos = {}
        for item in MenuDropdown.objects.all():
            elementos[item] = []
        for item in ItemMenu.objects.all():
            if item.dropdown is not None:
                elementos[item.dropdown].append(item)
            else:
                elementos[item] = None
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
    name = models.CharField(max_length=32, null=False)
    # Se aparecerá na página
    visivel = models.BooleanField(default=False)
    # Se aparecerá de forma não clicável
    desativado = models.BooleanField(default=False)

    def __str__(self):
        return "'" + self.name + "' (" + str(self.id) + ")"

    class Meta:
        abstract = True

class MenuDropdown(ItemMenuAbstrato):
    #manager = MenuManager()
    class Meta:
        ordering = ['indice']

class ItemMenu(ItemMenuAbstrato):
    #manager = MenuManager()
    # O endereço que o item possuirá (ItemMenuDropdown não precisa de endereço)
    endereco = models.URLField(null=False)
    # Cada ItemMenu pode ter apenas um MenuDropdown (cada MenuDropdown pode
    # possuir vários ItemMenu)
    dropdown = models.ForeignKey(
        MenuDropdown, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['indice']
