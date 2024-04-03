from django.urls import path
from .views import (ProductListView, NewProductCreateView, ProductDetailView, ProductUpdatView,
                     ProductDeleteView, BrandCreateView, import_products, CategoryAutocomplete, SubcategoryAutocomplete,                    
                      get_categories, get_subcategories )
from . import views


app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='products_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'), 
    path('new/', NewProductCreateView.as_view(), name='new_product'),
    path('<int:pk>/update/', ProductUpdatView.as_view(), name='product_update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('brands/new/', BrandCreateView.as_view(), name='brand_new'),
    path('import/', import_products, name='import_products'),
    path('category-autocomplete/', CategoryAutocomplete.as_view(), name='category-autocomplete'),
    path('subcategory-autocomplete/', SubcategoryAutocomplete.as_view(), name='subcategory-autocomplete'),  
    path('get-categories/', views.get_categories, name='get-categories'),
    path('get-subcategories/', views.get_subcategories, name='get-subcategories'),
]