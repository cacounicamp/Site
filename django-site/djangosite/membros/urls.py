from django.urls import path

from . import views


urlpatterns = [
    path('membros/', views.MembrosView, name='membros/'),
    path('membros/vincular-se/', views.MembroVincularView, name='membro/vincular/'),
    path('membros/desvincular-se/', views.MembroDesvincularView, name='membro/desvincular/'),
    path('membros/confirmar-token/<uuid:token>/', views.MembroConfirmarAcaoView, name='membro/token/'),
]
