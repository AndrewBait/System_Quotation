from django.urls import path
from . import views
from .views import (
    ListarPedidosView,
    DetalhesPedidoAgrupadoView,
    EditarPedidoAgrupadoView,
    DeletarPedidoView,
    responder_cotacao,
    cotacao_respondida_view,
    visualizar_cotacoes,
    gerar_pedidos,
    EditarPedidoView,
    DeletarPedidoAgrupadoView,
    exportar_pedidos_csv,
    exportar_pedidos_pdf,
    EnviarPedidoEmailView,
    ConcluirPedidoView, 
    CancelarPedidoView,
    MarcarPedidoPendenteView,
)

app_name = 'respostas'

urlpatterns = [
    path('responder/<uuid:cotacao_uuid>/<int:fornecedor_id>/<uuid:token>/', responder_cotacao, name='responder_cotacao'),
    path('respostas/<uuid:cotacao_uuid>/', visualizar_cotacoes, name='visualizar_cotacoes'),
    path('cotacao/price_history/<int:item_id>/<int:days>/', views.get_price_history, name='get_price_history'),
    path('cotacao_respondida/', cotacao_respondida_view, name='cotacao_respondida'),
    path('gerar-pedidos/', gerar_pedidos, name='gerar_pedidos'),
    path('pedidos/', ListarPedidosView.as_view(), name='listar_pedidos'),
    path('pedidos/detalhes/<int:pk>/', DetalhesPedidoAgrupadoView.as_view(), name='detalhes_pedido_agrupado'),
    path('pedidos/editar/<int:pk>/', EditarPedidoAgrupadoView.as_view(), name='editar_pedido_agrupado'),
    path('pedidos/deletar/<int:pk>/', DeletarPedidoAgrupadoView.as_view(), name='deletar_pedido_agrupado'),
    path('pedido/editar/<int:pk>/', EditarPedidoView.as_view(), name='editar_pedido_individual'),
    path('pedido/deletar/<int:pk>/', DeletarPedidoView.as_view(), name='deletar_pedido_individual'),
    path('exportar-pedidos/', exportar_pedidos_csv, name='exportar_pedidos'),
    path('exportar-pedidos-pdf/', exportar_pedidos_pdf, name='exportar_pedidos_pdf'),
    path('pedidos/enviar/<int:pk>/', EnviarPedidoEmailView.as_view(), name='enviar_pedido'),
    path('pedidos/concluir/<int:pk>/', ConcluirPedidoView.as_view(), name='concluir_pedido'),
    path('pedidos/cancelar/<int:pk>/', CancelarPedidoView.as_view(), name='cancelar_pedido'),
    path('pedidos/pendente/<int:pk>/', MarcarPedidoPendenteView.as_view(), name='marcar_pedido_pendente'),
]
