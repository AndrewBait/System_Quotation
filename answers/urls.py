from django.urls import path
from .views import (OpenCotacaoListView, CotacaoDetailView, AnswerCreateView, SubmitAnswersView, 
SubmitAnswerByUUIDView, CotacaoRespostasListView, CotacaoRespostasDetailView, AnswerSuccessView)
from . import views

app_name = 'answers'

urlpatterns = [
    path('cotacoes/', OpenCotacaoListView.as_view(), name='open_cotacao_list'),
    path('cotacoes/<uuid:uuid>/', CotacaoDetailView.as_view(), name='cotacao_detail'),    
    path('cotacoes/<uuid:uuid>/submit_answers/', SubmitAnswersView.as_view(), name='submit_answers'),
    path('responder/<uuid:uuid>/', views.submit_answers_by_uuid, name='submit_answers_by_uuid'),
    path('cotacoes/respondidas/', CotacaoRespostasListView.as_view(), name='cotacao_respostas_list'),
    path('cotacoes/respondidas/<uuid:uuid>/', views.CotacaoRespostasDetailView.as_view(), name='cotacao_respostas_detail'),
    path('resposta/sucesso/', AnswerSuccessView.as_view(), name='answer_success'),  # Adicione esta linha

]