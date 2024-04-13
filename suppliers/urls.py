from django.urls import path
from .views import SupplierCreateView, SupplierListView, SupplierDetailView, SupplierUpdateView, SupplierDeleteView
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('new/', SupplierCreateView.as_view(), name='supplier_new'),
    path('', SupplierListView.as_view(), name='supplier_list'),
    path('<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('<int:pk>/update/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('supplier/<int:pk>/update-ratings/', SupplierUpdateView.as_view(), name='supplier_update_ratings'),
    path('<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),
    path('products/get-categories/', views.get_categories, name='get-categories'),
    path('products/get-subcategories/', views.get_subcategories, name='get-subcategories'),
]
