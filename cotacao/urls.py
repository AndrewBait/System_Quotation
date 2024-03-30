from django.urls import path
from .views import (CotacaoListView, CotacaoDetailView, CotacaoCreateView, 
                    AddItemToCotacaoView, EditItemCotacaoView, DeleteItemCotacaoView, DepartamentoCreateView, 
                    DepartamentoDeleteView)
from . import views


app_name = 'cotacao'

urlpatterns = [
    path('', CotacaoListView.as_view(), name='cotacao_list'),
    path('<int:pk>/', CotacaoDetailView.as_view(), name='cotacao_detail'),
    path('new/', CotacaoCreateView.as_view(), name='cotacao_new'),
    path('<int:cotacao_id>/item/new/', AddItemToCotacaoView.as_view(), name='add_item_to_cotacao'),
    path('<int:cotacao_id>/item/<int:pk>/edit/', EditItemCotacaoView.as_view(), name='edit_item_cotacao'),
    path('<int:cotacao_id>/item/<int:pk>/delete/', DeleteItemCotacaoView.as_view(), name='delete_item_cotacao'),
    path('departamento/new/', DepartamentoCreateView.as_view(), name='departamento_new'),
    path('departamento/<int:pk>/delete/', DepartamentoDeleteView.as_view(), name='departamento_delete'),
]
