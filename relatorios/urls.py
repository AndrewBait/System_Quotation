from django.urls import path
from .views import (
    gerar_relatorios, ManualUsuarioView, ResumoCotacoesView, CotacoesDepartamentoCategoriaView,
    ComparativoPrecosFornecedorView, DesempenhoFornecedoresView, ProdutosMaisCotadosView,
    ProdutosMaiorVariacaoPrecoView, ProdutosSemFornecedorView, PedidosAgrupadosFornecedorView,
    HistoricoPedidosAgrupadosView
)

app_name = 'relatorios'

urlpatterns = [
    path('gerar/', gerar_relatorios, name='gerar_relatorios'),
    path('manual/', ManualUsuarioView.as_view(), name='manual_usuario'),
    path('resumo-cotacoes/', ResumoCotacoesView.as_view(), name='resumo_cotacoes'),
    path('cotacoes-departamento-categoria/', CotacoesDepartamentoCategoriaView.as_view(), name='cotacoes_departamento_categoria'),
    path('comparativo-precos-fornecedor/', ComparativoPrecosFornecedorView.as_view(), name='comparativo_precos_fornecedor'),
    path('desempenho-fornecedores/', DesempenhoFornecedoresView.as_view(), name='desempenho_fornecedores'),
    path('produtos-mais-cotados/', ProdutosMaisCotadosView.as_view(), name='produtos_mais_cotados'),
    path('produtos-maior-variacao-preco/', ProdutosMaiorVariacaoPrecoView.as_view(), name='produtos_maior_variacao_preco'),
    path('produtos-sem-fornecedor/', ProdutosSemFornecedorView.as_view(), name='produtos_sem_fornecedor'),
    path('pedidos-agrupados-fornecedor/', PedidosAgrupadosFornecedorView.as_view(), name='pedidos_agrupados_fornecedor'),
    path('historico-pedidos-agrupados/', HistoricoPedidosAgrupadosView.as_view(), name='historico_pedidos_agrupados'),
]
