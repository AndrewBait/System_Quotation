from django.urls import path, re_path
from .views import responder_cotacao, cotacao_respondida_view, visualizar_cotacoes, gerar_pedidos, ListarPedidosView, DetalhesPedidoView, EditarPedidoView, DeletarPedidoView
from . import views




app_name = 'respostas'

urlpatterns = [
    path('responder/<uuid:cotacao_uuid>/<int:fornecedor_id>/<uuid:token>/', responder_cotacao, name='responder_cotacao'),
    path('respostas/<uuid:cotacao_uuid>/', visualizar_cotacoes, name='visualizar_cotacoes'),
    path('cotacao_respondida/', cotacao_respondida_view, name='cotacao_respondida'),
    path('gerar-pedidos/', gerar_pedidos, name='gerar_pedidos'),
    path('pedidos/', ListarPedidosView.as_view(), name='listar_pedidos'),
    path('pedidos/<int:pk>/', DetalhesPedidoView.as_view(), name='detalhes_pedido'),
    path('pedidos/editar/<int:pk>/', EditarPedidoView.as_view(), name='editar_pedido'),
    path('pedidos/deletar/<int:pk>/', DeletarPedidoView.as_view(), name='deletar_pedido'),
]