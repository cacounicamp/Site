"""djangosite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
