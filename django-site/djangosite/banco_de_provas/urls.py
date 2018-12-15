from django.urls import path
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    path('banco-de-provas/', views.BancoDeProvasView, name='banco-de-provas/'),
    path('banco-de-provas/contribuir/', views.SubmeterProvaView, name='banco-de-provas/contribuir/'),

    # Para as pessoas que salvam a página do CACo nos favoritos não perderem o
    # site
    path('bancodeprovas/', RedirectView.as_view(pattern_name='banco-de-provas/', permanent=True)),
]
