from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.http import JsonResponse, HttpResponse
from cotacao.models import Cotacao, ItemCotacao
import csv

def gerar_relatorios(request):
    return render(request, 'relatorios/gerar_relatorios.html')

class ManualUsuarioView(TemplateView):
    template_name = 'relatorios/manual_usuario.html'

class ResumoCotacoesView(TemplateView):
    template_name = 'relatorios/resumo_cotacoes.html'

    def get(self, request):
        # Lógica para obter dados do relatório
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio and data_fim:
            cotacoes = Cotacao.objects.filter(data_abertura__gte=data_inicio, data_fechamento__lte=data_fim)
        else:
            cotacoes = Cotacao.objects.all()

        total_cotacoes = cotacoes.count()
        total_itens = ItemCotacao.objects.filter(cotacao__in=cotacoes).count()
        valor_total = ItemCotacao.objects.filter(cotacao__in=cotacoes).aggregate(Sum('produto__preco_de_custo'))['produto__preco_de_custo__sum']

        context = {
            'cotacoes': cotacoes,
            'total_cotacoes': total_cotacoes,
            'total_itens': total_itens,
            'valor_total': valor_total,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # Lógica para exportar o relatório
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        formato = request.POST.get('formato')

        if data_inicio and data_fim:
            cotacoes = Cotacao.objects.filter(data_abertura__gte=data_inicio, data_fechamento__lte=data_fim)
        else:
            cotacoes = Cotacao.objects.all()

        if formato == 'csv':
            return self.exportar_csv(cotacoes)
        elif formato == 'xml':
            return self.exportar_xml(cotacoes)
        elif formato == 'pdf':
            return self.exportar_pdf(cotacoes)
        else:
            return JsonResponse({'erro': 'Formato inválido'})

    def exportar_csv(self, cotacoes):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resumo_cotacoes.csv"'

        writer = csv.writer(response)
        writer.writerow(['Nome', 'Departamento', 'Data Abertura', 'Data Fechamento', 'Status', 'Prazo'])

        for cotacao in cotacoes:
            writer.writerow([cotacao.nome, cotacao.departamento.nome, cotacao.data_abertura, cotacao.data_fechamento, cotacao.status, cotacao.prazo])

        return response

    def exportar_xml(self, cotacoes):
        # Implementar exportação para XML
        pass

    def exportar_pdf(self, cotacoes):
        # Implementar exportação para PDF
        pass

class CotacoesDepartamentoCategoriaView(TemplateView):
    template_name = 'relatorios/cotacoes_departamento_categoria.html'

class ComparativoPrecosFornecedorView(TemplateView):
    template_name = 'relatorios/comparativo_precos_fornecedor.html'

class DesempenhoFornecedoresView(TemplateView):
    template_name = 'relatorios/desempenho_fornecedores.html'

class ProdutosMaisCotadosView(TemplateView):
    template_name = 'relatorios/produtos_mais_cotados.html'

class ProdutosMaiorVariacaoPrecoView(TemplateView):
    template_name = 'relatorios/produtos_maior_variacao_preco.html'

class ProdutosSemFornecedorView(TemplateView):
    template_name = 'relatorios/produtos_sem_fornecedor.html'

class PedidosAgrupadosFornecedorView(TemplateView):
    template_name = 'relatorios/pedidos_agrupados_fornecedor.html'

class HistoricoPedidosAgrupadosView(TemplateView):
    template_name = 'relatorios/historico_pedidos_agrupados.html'
