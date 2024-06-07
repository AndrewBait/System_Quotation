from django.shortcuts import render
from django.views.generic import TemplateView

def gerar_relatorios(request):
    return render(request, 'relatorios/gerar_relatorios.html')




class ManualUsuarioView(TemplateView):
    template_name = 'relatorios/manual_usuario.html'
