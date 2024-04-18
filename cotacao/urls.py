from django.urls import path
from .views import ProdutoAPI, DepartamentoAPI, CategoriaAPI, SubcategoriaAPI, ItensCotacaoAPI, CotacaoCreateView, AddProductToCotacaoView

app_name = 'cotacao'

urlpatterns = [
    path('api/produtos/', ProdutoAPI.as_view(), name='produtos_api'),
    path('api/departamentos/', DepartamentoAPI.as_view(), name='departamentos_api'),
    path('api/categorias/', CategoriaAPI.as_view(), name='categorias_api'),
    path('api/subcategorias/<int:category_id>/', SubcategoriaAPI.as_view(), name='subcategorias_api'),
    path('create/', CotacaoCreateView.as_view(), name='cotacao_create'),
    path('add-product/<int:cotacao_id>/', AddProductToCotacaoView.as_view(), name='add_product_to_cotacao'),
    path('api/itens-cotacao/<int:cotacao_id>/', ItensCotacaoAPI.as_view(), name='itens_cotacao_api'),

]
