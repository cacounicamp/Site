from django.urls import path

from . import views


urlpatterns = [
    path('contato/', views.ContatoView, name='contato/'),
]
