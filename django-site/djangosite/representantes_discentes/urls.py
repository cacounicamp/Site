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
    path('representantes-discentes/', views.RepresentantesDiscentesPagina, name='representantes-discentes/'),
    path('representantes-discentes/pagina-<int:pagina>/', views.RepresentantesDiscentesPagina, name='representantes-discentes/pagina/'),

    path('representantes-discentes/<int:ano_atuacao>/', views.RepresentantesDiscentesAno, name='representantes-discentes/ano/'),
]
