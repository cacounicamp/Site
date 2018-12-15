from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('ouvidoria.urls')),
    path('', include('paginas_estaticas.urls')),
    path('', include('noticias.urls')), # Notícias possuirá a raiz do site
    path('', include('atas.urls')),
    path('', include('gestoes.urls')),
    path('', include('representantes_discentes.urls')),
    path('', include('membros.urls')),
    path('', include('banco_de_provas.urls')),
]

# Em desenvolvemento, servimos manualmente media/
if settings.DEBUG:
    urlpatterns = urlpatterns + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
