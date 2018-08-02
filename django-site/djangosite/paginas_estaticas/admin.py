from django import forms
from django.contrib import admin
from .models import *
# Para editor de content da página
from ckeditor.widgets import CKEditorWidget
# Para substituir o formulário de FlatPage para outro com editor
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.forms import FlatpageForm

# Colocamos o editor no formulário de administrador
class FormFlatPage(FlatpageForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FlatPage
        fields = '__all__'

class AdminFlatPage(admin.ModelAdmin):
    form = FormFlatPage

admin.site.register(MenuDropdown)
admin.site.register(ItemMenu)

# Recriamos o administrador para FlatPage
admin.site.register(FlatPage, FormFlatPage)
admin.site.unregister(FlatPage)
