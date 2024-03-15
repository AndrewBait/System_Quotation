from django.urls import path
from . import views

urlpatterns = [
    # ...outras urls do app...
    path('cotation/new/', views.create_cotation, name='create_cotation'),
    path('cotation/<int:cotation_id>/add_products/', views.add_products_to_cotation, name='add_products_to_cotation'),
    # Você pode adicionar mais URLs aqui conforme desenvolve outras funcionalidades
]
