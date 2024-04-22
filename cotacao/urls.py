from django.urls import path
from .views import (
    ProdutoAPI, DepartamentoAPI, CategoriaAPI, SubcategoriaAPI, 
    ItensCotacaoAPI, CotacaoCreateView, AddProductToCotacaoView, 
    ProductAutocomplete, ToggleCotacaoStatusView, CotacaoUpdateView, 
    CotacaoDeleteView, CotacaoListView, PesquisaFornecedorAjaxView, 
    EnviarCotacaoView, ListProductsToAddView  
)

app_name = 'cotacao'

urlpatterns = [
    # APIs
    path('api/produtos/', ProdutoAPI.as_view(), name='produtos_api'),
    path('api/departamentos/', DepartamentoAPI.as_view(), name='departamentos_api'),
    path('api/categorias/', CategoriaAPI.as_view(), name='categorias_api'),
    path('api/subcategorias/<int:category_id>/', SubcategoriaAPI.as_view(), name='subcategorias_api'),
    path('api/itens-cotacao/<int:cotacao_id>/', ItensCotacaoAPI.as_view(), name='itens_cotacao_api'),

    # Cotação CRUD
    path('create/', CotacaoCreateView.as_view(), name='cotacao_create'),
    path('list/', CotacaoListView.as_view(), name='cotacao_list'),
    path('edit/<int:pk>/', CotacaoUpdateView.as_view(), name='edit_cotacao'),
    path('delete/<int:pk>/', CotacaoDeleteView.as_view(), name='delete_cotacao'),
    path('enviar-cotacao/<int:pk>/', EnviarCotacaoView.as_view(), name='enviar_cotacao'),
    path('pesquisa-fornecedor/', PesquisaFornecedorAjaxView.as_view(), name='pesquisa-fornecedor-ajax'),

    # Produto handling
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
    path('toggle-status/<int:pk>/', ToggleCotacaoStatusView.as_view(), name='toggle_cotacao_status'),

    # Adicionando produtos
    
    path('add-product/<int:cotacao_id>/', AddProductToCotacaoView.as_view(), name='add_product_to_cotacao'),
    path('cotacao/<int:cotacao_id>/adicionar-produtos/', ListProductsToAddView.as_view(), name='list_products_to_add'),
]
