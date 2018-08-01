from django.test import TestCase
from paginas_estaticas.models import *

class MostrarMenu(TestCase):

    @classmethod
    def setUpTestData(cls):
        ItemMenu.objects.all().delete()
        MenuDropdown.objects.all().delete()
        item3 = ItemMenu.objects.create(
            indice=3,
            name="Item 3",
            visivel=True,
            endereco="google.com"
        )
        item2 = ItemMenu.objects.create(
            indice=2,
            name="Item 2",
            visivel=True,
            endereco="google.com"
        )
        item0_drop = MenuDropdown.objects.create(
            indice=0,
            name="Item 0",
            visivel=True,
        )
        item_drop2 = ItemMenu.objects.create(
            indice=2,
            name="Item 2 do dropdown",
            visivel=True,
            dropdown=item0_drop,
            endereco="google.com"
        )
        item_drop2_ = ItemMenu.objects.create(
            indice=2,
            name="Item 2 do dropdown duplicate",
            visivel=True,
            dropdown=item0_drop,
            endereco="google.com"
        )
        item_drop0 = ItemMenu.objects.create(
            indice=0,
            name="Item 0 do dropdown",
            visivel=True,
            dropdown=item0_drop,
            endereco="google.com"
        )
        item1 = ItemMenu.objects.create(
            indice=1,
            name="Item 1",
            visivel=True,
            endereco="google.com"
        )
        print('Created objects for tests')

    def test1(self):
        print('### Test 1')
        itens = ItemMenu.objects.filter(dropdown=None).order_by('indice')
        for item in itens:
            print(item)
        print('### End of test 1')

    def test2(self):
        print('### Test 2')
        menus = MenuDropdown.objects.order_by('indice')
        for menu in menus:
            print(menu)
            itens = ItemMenu.objects.filter(dropdown=menu).order_by('indice')
            for item in itens:
                print('\t' + str(item))
        print('### End of test 2')

    def test3(self):
        print('### Test 3')
        print(ItemMenu.objects.get_itens())
        print('### End of test 3')
