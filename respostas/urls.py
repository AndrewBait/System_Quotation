from django.urls import path, re_path
from .views import responder_cotacao

app_name = 'respostas'

urlpatterns = [
    re_path(r'responder/(?P<cotacao_uuid>[0-9a-f-]+)/(?P<fornecedor_id>\d+)/', responder_cotacao, name='responder_cotacao'),
]