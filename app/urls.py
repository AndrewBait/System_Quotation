from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from products.views import ProductListView, NewProductCreateView, ProductDetailView, ProductUpdatView, ProductDeleteView
from accounts.views import register_view, login_view, logout_view
from suppliers.views import SupplierCreateView, SupplierListView, SupplierDetailView, SupplierUpdateView, SupplierDeleteView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('products/', ProductListView.as_view(), name='products_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/new/', NewProductCreateView.as_view(), name='new_product'),
    path('product/<int:pk>/update/', ProductUpdatView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('suppliers/new/', SupplierCreateView.as_view(), name='supplier_new'),
    path('', SupplierListView.as_view(), name='supplier_list'),
    path('<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('<int:pk>/update/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
