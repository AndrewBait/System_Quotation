from django.urls import path
from .views import responder_cotacao

app_name = 'respostas'

urlpatterns = [
    path('responder/<int:pk>/<int:fornecedor_id>/', responder_cotacao, name='responder_cotacao'),
]