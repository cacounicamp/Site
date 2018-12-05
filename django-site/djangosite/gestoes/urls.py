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
    path('gestoes/', views.GestoesView, name='gestoes/'),
    path('gestoes/pagina-<int:pagina>/', views.GestoesView, name='gestoes/pagina/'),
    path('gestoes/<int:ano>/', views.GestaoView),
    path('gestoes/<int:ano>-<slug:nome>/', views.GestaoView, name='gestao/'),
]
