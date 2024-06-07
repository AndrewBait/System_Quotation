# relatorios/urls.py
from django.urls import path
from .views import ManualUsuarioView
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('gerar/', views.gerar_relatorios, name='gerar_relatorios'),
    path('manual/', ManualUsuarioView.as_view(), name='manual_usuario'),
]
