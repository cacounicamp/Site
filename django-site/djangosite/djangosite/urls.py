import os

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.shortcuts import render
from django.conf.urls.static import static


def handle400(request):
    return render(request, '400.html')

def handle403(request):
    return render(request, '403.html')

def handle404(request):
    return render(request, '404.html')

def handle500(request):
    return render(request, '500.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('400/', handle400),
    path('403/', handle403),
    path('404/', handle404),
    path('500/', handle500),
    path('', include('ouvidoria.urls')),
    path('', include('noticias.urls')), # Notícias possuirá a raiz do site
    path('', include('atas.urls')),
    path('', include('gestoes.urls')),
    path('', include('representantes_discentes.urls')),
    path('', include('membros.urls')),
    path('', include('banco_de_provas.urls')),
    path('', include('laricaco.urls')),
]

# Em desenvolvemento, servimos manualmente media/
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_DEBUG_ROOT)
