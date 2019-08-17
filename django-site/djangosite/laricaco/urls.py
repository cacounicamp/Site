from django.urls import path

from . import views


urlpatterns = [
    path('laricaco/', views.LariCACoView, name='laricaco/'),
]
