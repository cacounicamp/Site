from django.urls import path

from . import views


urlpatterns = [
    path('representantes-discentes/', views.RepresentantesDiscentesPagina, name='representantes-discentes/'),
    path('representantes-discentes/pagina-<int:pagina>/', views.RepresentantesDiscentesPagina, name='representantes-discentes/pagina/'),

    path('representantes-discentes/<int:ano_atuacao>/', views.RepresentantesDiscentesAno, name='representantes-discentes/ano/'),
]
