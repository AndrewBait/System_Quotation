from django.urls import path
from . import views

urlpatterns = [
    # ...outras urls do app...
    path('cotation/new/', views.create_cotation, name='create_cotation'),
    # Você pode adicionar mais URLs aqui conforme desenvolve outras funcionalidades
]
