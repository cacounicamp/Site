from django.urls import path

from . import views


urlpatterns = [
    path('noticias/<int:identificador>-<slug:titulo>/', views.NoticiaDetalheView, name='noticia/'),
    # Atalho para a de cima (link irá se corrigir)
    path('noticias/<int:identificador>/', views.NoticiaDetalheView),
    path('noticias/', views.NoticiasView, name='noticias/'),
    path('noticias/pagina-<int:pagina>/', views.NoticiasView, name="noticias/pagina/"),
    path('', views.NoticiasRaizView, name='/'),
]
