from django.urls import path, re_path
from .views import responder_cotacao, cotacao_respondida_view

app_name = 'respostas'

urlpatterns = [
    path('responder/<uuid:cotacao_uuid>/<int:fornecedor_id>/<uuid:token>/', responder_cotacao, name='responder_cotacao'),
    path('cotacao_respondida/', cotacao_respondida_view, name='cotacao_respondida'),  
]