from django.urls import path
from . import views

app_name = 'quotations'

urlpatterns = [
    path('', views.CotationListView.as_view(), name='cotation_list'),
    path('new/', views.CotationCreateView.as_view(), name='cotation_create'),
    path('<int:pk>/', views.CotationDetailView.as_view(), name='cotation_detail'),
    path('<int:pk>/edit/', views.CotationUpdateView.as_view(), name='cotation_edit'),
    path('<int:pk>/delete/', views.CotationDeleteView.as_view(), name='cotation_delete'),
    path('<int:pk>/add_products/', views.CotationAddProductsView.as_view(), name='cotation_add_products'),
]