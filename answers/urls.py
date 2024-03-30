from django.urls import path
from .views import OpenCotacaoListView, CotacaoDetailView, AnswerCreateView, SubmitAnswersView

app_name = 'answers'

urlpatterns = [
    path('cotacoes/', OpenCotacaoListView.as_view(), name='open_cotacao_list'),
    path('cotacoes/<int:pk>/', CotacaoDetailView.as_view(), name='cotacao_detail'),
    path('item/<int:item_cotacao_id>/resposta/', AnswerCreateView.as_view(), name='submit_answer'),
    path('cotacoes/<int:cotacao_id>/submit_answers/', SubmitAnswersView.as_view(), name='submit_answers'),
]