from django.urls import path
from .views import ProdutoAPI, DepartamentoAPI, CategoriaAPI, SubcategoriaAPI





app_name = 'cotacao'

urlpatterns = [
    path('api/produtos/', ProdutoAPI.as_view(), name='produtos_api'),
    path('api/departamentos/', DepartamentoAPI.as_view(), name='departamentos_api'),
    path('api/categorias/', CategoriaAPI.as_view(), name='categorias_api'),
    path('api/subcategorias/<int:category_id>/', SubcategoriaAPI.as_view(), name='subcategorias_api'),
    
    
]
