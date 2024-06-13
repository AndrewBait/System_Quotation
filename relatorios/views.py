import io
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Avg
from django.http import FileResponse, JsonResponse, HttpResponse
from cotacao.models import Cotacao, ItemCotacao
import csv
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
        valor_medio_itens = ItemCotacao.objects.filter(cotacao__in=cotacoes).aggregate(Avg('produto__preco_de_custo'))['produto__preco_de_custo__avg']
        numero_fornecedores = cotacoes.values('departamento').distinct().count()
        itens_mais_cotados = ItemCotacao.objects.filter(cotacao__in=cotacoes).values('produto__name').annotate(total=Count('produto')).order_by('-total')[:5]

        context = {
            'cotacoes': cotacoes,
            'total_cotacoes': total_cotacoes,
            'total_itens': total_itens,
            'valor_total': valor_total,
            'valor_medio_itens': valor_medio_itens,
            'numero_fornecedores': numero_fornecedores,
            'itens_mais_cotados': itens_mais_cotados,
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
        response = HttpResponse(content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="resumo_cotacoes.xml"'

        root = ET.Element('Cotacoes')
        for cotacao in cotacoes:
            cotacao_element = ET.SubElement(root, 'Cotacao')
            ET.SubElement(cotacao_element, 'Nome').text = cotacao.nome
            ET.SubElement(cotacao_element, 'Departamento').text = cotacao.departamento.nome
            ET.SubElement(cotacao_element, 'DataAbertura').text = str(cotacao.data_abertura)
            ET.SubElement(cotacao_element, 'DataFechamento').text = str(cotacao.data_fechamento)
            ET.SubElement(cotacao_element, 'Status').text = cotacao.status
            ET.SubElement(cotacao_element, 'Prazo').text = str(cotacao.prazo)

        tree = ET.ElementTree(root)
        tree.write(response, encoding='utf-8', xml_declaration=True)

        return response

    def exportar_pdf(self, cotacoes):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        subtitle_style = ParagraphStyle(name='Subtitle', fontSize=12, spaceAfter=10)

        title = "Resumo de Cotações"
        subtitle = f"Período: {self.request.POST.get('data_inicio')} a {self.request.POST.get('data_fim')}"
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Spacer(1, 12))

        data = [['Nome', 'Departamento', 'Data Abertura', 'Data Fechamento', 'Status', 'Prazo']]
        for cotacao in cotacoes:
            data.append([cotacao.nome, cotacao.departamento.nome, cotacao.data_abertura, cotacao.data_fechamento, cotacao.status, f"{cotacao.prazo} dias"])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_page_number)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='resumo_cotacoes.pdf')

    def add_page_number(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200*mm, 20*mm, text)
        
        
    
class CotacoesDepartamentoCategoriaView(TemplateView):
    template_name = 'relatorios/cotacoes_departamento_categoria.html'

    def get(self, request):
        # Lógica para obter dados do relatório
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio and data_fim:
            cotacoes = Cotacao.objects.filter(data_abertura__gte=data_inicio, data_fechamento__lte=data_fim)
        else:
            cotacoes = Cotacao.objects.all()

        cotacoes_por_departamento = cotacoes.values('departamento__nome').annotate(
            total_cotacoes=Count('id'),
            total_itens=Sum('itens_cotacao__quantidade'),
            valor_total=Sum('itens_cotacao__produto__preco_de_custo')
        ).order_by('departamento__nome')

        context = {
            'cotacoes_por_departamento': cotacoes_por_departamento,
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

        cotacoes_por_departamento = cotacoes.values('departamento__nome').annotate(
            total_cotacoes=Count('id'),
            total_itens=Sum('itens_cotacao__quantidade'),
            valor_total=Sum('itens_cotacao__produto__preco_de_custo')
        ).order_by('departamento__nome')

        if formato == 'csv':
            return self.exportar_csv(cotacoes_por_departamento)
        elif formato == 'xml':
            return self.exportar_xml(cotacoes_por_departamento)
        elif formato == 'pdf':
            return self.exportar_pdf(cotacoes_por_departamento)
        else:
            return JsonResponse({'erro': 'Formato inválido'})

    def exportar_csv(self, cotacoes_por_departamento):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cotacoes_departamento_categoria.csv"'

        writer = csv.writer(response)
        writer.writerow(['Departamento', 'Total de Cotações', 'Total de Itens', 'Valor Total'])

        for item in cotacoes_por_departamento:
            writer.writerow([item['departamento__nome'], item['total_cotacoes'], item['total_itens'], item['valor_total']])

        return response

    def exportar_xml(self, cotacoes_por_departamento):
        response = HttpResponse(content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="cotacoes_departamento_categoria.xml"'

        root = ET.Element('CotacoesPorDepartamento')
        for item in cotacoes_por_departamento:
            departamento_element = ET.SubElement(root, 'Departamento')
            ET.SubElement(departamento_element, 'Nome').text = item['departamento__nome']
            ET.SubElement(departamento_element, 'TotalCotacoes').text = str(item['total_cotacoes'])
            ET.SubElement(departamento_element, 'TotalItens').text = str(item['total_itens'])
            ET.SubElement(departamento_element, 'ValorTotal').text = str(item['valor_total'])

        tree = ET.ElementTree(root)
        tree.write(response, encoding='utf-8', xml_declaration=True)

        return response

    def exportar_pdf(self, cotacoes_por_departamento):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        subtitle_style = ParagraphStyle(name='Subtitle', fontSize=12, spaceAfter=10)

        title = "Cotações por Departamento e Categoria"
        subtitle = f"Período: {self.request.POST.get('data_inicio')} a {self.request.POST.get('data_fim')}"
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Spacer(1, 12))

        data = [['Departamento', 'Total de Cotações', 'Total de Itens', 'Valor Total']]
        for item in cotacoes_por_departamento:
            data.append([item['departamento__nome'], item['total_cotacoes'], item['total_itens'], item['valor_total']])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_page_number)

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='cotacoes_departamento_categoria.pdf')

    def add_page_number(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200*mm, 20*mm, text)

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
