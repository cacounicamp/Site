from django.urls import path

from . import views


urlpatterns = [
    # Lista maior de atas de assembleias apenas
    path('atas/assembleias/', views.AtasAssembleiasView, name='atas/assembleias/'),
    path('atas/assembleias/pagina-<int:pagina>', views.AtasAssembleiasView, name='atas/assembleias/pagina/'),
    # Em detalhe
    path('atas/assembleias/<int:identificador>-<slug:data>/', views.AtaAssembleiaView, name='ata/assembleia/'),
    # Atalho
    path('atas/assembleias/<int:identificador>/', views.AtaAssembleiaView),

    # Lista maior de atas de reuniões apenas
    path('atas/reunioes/', views.AtasReunioesView, name='atas/reunioes/'),
    path('atas/reunioes/pagina-<int:pagina>/', views.AtasReunioesView, name='atas/reunioes/pagina/'),
    # Em detalhe
    path('atas/reunioes/<int:identificador>-<slug:data>/', views.AtaReuniaoView, name='ata/reuniao/'),
    # Atalho
    path('atas/reunioes/<int:identificador>/', views.AtaReuniaoView),

    # Listas das últimas atas das duas categorias
    path('atas/', views.AtasView, name='atas/'),
]
