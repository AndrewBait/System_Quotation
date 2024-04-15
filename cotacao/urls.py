from django.urls import path
from .views import (CotacaoListView, CotacaoDetailView, CotacaoCreateView, 
                    AddItemToCotacaoView, EditItemCotacaoView, DeleteItemCotacaoView, DepartamentoCreateView, 
                    DepartamentoDeleteView, enviar_cotacao_view,CotacaoListCreateView, export_cotacoes_excel, 
                    export_cotacoes_pdf, toggle_status_cotacao, buscar_produtos )
from . import views


app_name = 'cotacao'

urlpatterns = [
    path('', CotacaoListView.as_view(), name='cotacao_list'),
    path('<int:pk>/', CotacaoDetailView.as_view(), name='cotacao_detail'),
    # path('new/', CotacaoCreateView.as_view(), name='cotacao_new'),
    path('<int:cotacao_id>/item/new/', AddItemToCotacaoView.as_view(), name='add_item_to_cotacao'),
    path('<int:cotacao_id>/item/<int:pk>/edit/', EditItemCotacaoView.as_view(), name='edit_item_cotacao'),
    path('<int:cotacao_id>/item/<int:pk>/delete/', DeleteItemCotacaoView.as_view(), name='delete_item_cotacao'),
    path('departamento/new/', DepartamentoCreateView.as_view(), name='departamento_new'),
    path('departamento/<int:pk>/delete/', DepartamentoDeleteView.as_view(), name='departamento_delete'),
    path('cotacao/<int:pk>/enviar/', enviar_cotacao_view, name='enviar_cotacao'),
    path('<int:pk>/delete/', views.CotacaoDeleteView.as_view(), name='cotacao_delete'),
    path('cotacoes/', CotacaoListCreateView.as_view(), name='cotacao_list_create'),
    path('export/excel/', export_cotacoes_excel, name='export_cotacoes_excel'),
    path('export/pdf/', export_cotacoes_pdf, name='export_cotacoes_pdf'),
    path('cotacao/<int:pk>/toggle_status/', toggle_status_cotacao, name='toggle_status'),
    path('buscar-produtos/', buscar_produtos, name='buscar_produtos'),


]
