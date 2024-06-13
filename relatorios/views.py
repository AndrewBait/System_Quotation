from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Avg
from django.http import FileResponse, JsonResponse, HttpResponse
from cotacao.models import Cotacao, ItemCotacao
from suppliers.models import Supplier
from respostas.models import RespostaCotacao, ItemRespostaCotacao
from django.template.loader import render_to_string
import csv
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io


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

    def get(self, request):
        # Lógica para obter dados do relatório
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio and data_fim:
            respostas = RespostaCotacao.objects.filter(cotacao__data_abertura__gte=data_inicio, cotacao__data_fechamento__lte=data_fim)
        else:
            respostas = RespostaCotacao.objects.all()

        comparativo_precos = respostas.values('fornecedor__name').annotate(
            media_preco=Avg('itemrespostacotacao__preco'),
            total_itens=Sum('itemrespostacotacao__item_cotacao__quantidade'),
        ).order_by('fornecedor__name')

        context = {
            'comparativo_precos': comparativo_precos,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # Lógica para exportar o relatório
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        formato = request.POST.get('formato')

        if data_inicio and data_fim:
            respostas = RespostaCotacao.objects.filter(cotacao__data_abertura__gte=data_inicio, cotacao__data_fechamento__lte=data_fim)
        else:
            respostas = RespostaCotacao.objects.all()

        comparativo_precos = respostas.values('fornecedor__name').annotate(
            media_preco=Avg('itemrespostacotacao__preco'),
            total_itens=Sum('itemrespostacotacao__item_cotacao__quantidade'),
        ).order_by('fornecedor__name')

        if formato == 'csv':
            return self.exportar_csv(comparativo_precos)
        elif formato == 'xml':
            return self.exportar_xml(comparativo_precos)
        elif formato == 'pdf':
            return self.exportar_pdf(comparativo_precos)
        else:
            return JsonResponse({'erro': 'Formato inválido'})

    def exportar_csv(self, comparativo_precos):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="comparativo_precos_fornecedor.csv"'

        writer = csv.writer(response)
        writer.writerow(['Fornecedor', 'Média de Preço', 'Total de Itens'])

        for item in comparativo_precos:
            writer.writerow([item['fornecedor__name'], item['media_preco'], item['total_itens']])

        return response

    def exportar_xml(self, comparativo_precos):
        response = HttpResponse(content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="comparativo_precos_fornecedor.xml"'

        root = ET.Element('ComparativoPrecos')
        for item in comparativo_precos:
            item_element = ET.SubElement(root, 'Item')
            ET.SubElement(item_element, 'Fornecedor').text = item['fornecedor__name']
            ET.SubElement(item_element, 'MediaPreco').text = str(item['media_preco'])
            ET.SubElement(item_element, 'TotalItens').text = str(item['total_itens'])

        tree = ET.ElementTree(root)
        tree.write(response, encoding='utf-8', xml_declaration=True)

        return response

    def exportar_pdf(self, comparativo_precos):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        subtitle_style = ParagraphStyle(name='Subtitle', fontSize=12, spaceAfter=10)

        title = "Comparativo de Preços por Fornecedor"
        subtitle = f"Período: {self.request.POST.get('data_inicio')} a {self.request.POST.get('data_fim')}"
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Spacer(1, 12))

        data = [['Fornecedor', 'Média de Preço', 'Total de Itens']]
        for item in comparativo_precos:
            data.append([item['fornecedor__name'], f"R$ {item['media_preco']:.2f}", item['total_itens']])

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
        return FileResponse(buffer, as_attachment=True, filename='comparativo_precos_fornecedor.pdf')

    def add_page_number(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200*mm, 20*mm, text)

class DesempenhoFornecedoresView(TemplateView):
    template_name = 'relatorios/desempenho_fornecedores.html'

    def get(self, request):
        # Lógica para obter dados do relatório
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio and data_fim:
            fornecedores = Supplier.objects.filter(created_at__gte=data_inicio, updated_at__lte=data_fim)
        else:
            fornecedores = Supplier.objects.all()

        desempenho_fornecedores = fornecedores.annotate(
            qualidade_media=Avg('quality_rating'),
            prazo_entrega_medio=Avg('delivery_time_rating'),
            preco_medio=Avg('price_rating'),
            confiabilidade_media=Avg('reliability_rating'),
            flexibilidade_media=Avg('flexibility_rating'),
            parceria_media=Avg('partnership_rating')
        ).order_by('name')

        context = {
            'desempenho_fornecedores': desempenho_fornecedores,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # Lógica para exportar o relatório
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        formato = request.POST.get('formato')

        if data_inicio and data_fim:
            fornecedores = Supplier.objects.filter(created_at__gte=data_inicio, updated_at__lte=data_fim)
        else:
            fornecedores = Supplier.objects.all()

        desempenho_fornecedores = fornecedores.annotate(
            qualidade_media=Avg('quality_rating'),
            prazo_entrega_medio=Avg('delivery_time_rating'),
            preco_medio=Avg('price_rating'),
            confiabilidade_media=Avg('reliability_rating'),
            flexibilidade_media=Avg('flexibility_rating'),
            parceria_media=Avg('partnership_rating')
        ).order_by('name')

        if formato == 'csv':
            return self.exportar_csv(desempenho_fornecedores)
        elif formato == 'xml':
            return self.exportar_xml(desempenho_fornecedores)
        elif formato == 'pdf':
            return self.exportar_pdf(desempenho_fornecedores)
        else:
            return JsonResponse({'erro': 'Formato inválido'})

    def exportar_csv(self, desempenho_fornecedores):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="desempenho_fornecedores.csv"'

        writer = csv.writer(response)
        writer.writerow(['Fornecedor', 'Qualidade Média', 'Prazo de Entrega Médio', 'Preço Médio', 'Confiabilidade Média', 'Flexibilidade Média', 'Parceria Média'])

        for fornecedor in desempenho_fornecedores:
            writer.writerow([
                fornecedor.name,
                fornecedor.qualidade_media,
                fornecedor.prazo_entrega_medio,
                fornecedor.preco_medio,
                fornecedor.confiabilidade_media,
                fornecedor.flexibilidade_media,
                fornecedor.parceria_media
            ])

        return response

    def exportar_xml(self, desempenho_fornecedores):
        response = HttpResponse(content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="desempenho_fornecedores.xml"'

        root = ET.Element('Fornecedores')
        for fornecedor in desempenho_fornecedores:
            fornecedor_element = ET.SubElement(root, 'Fornecedor')
            ET.SubElement(fornecedor_element, 'Nome').text = fornecedor.name
            ET.SubElement(fornecedor_element, 'QualidadeMedia').text = str(fornecedor.qualidade_media)
            ET.SubElement(fornecedor_element, 'PrazoEntregaMedio').text = str(fornecedor.prazo_entrega_medio)
            ET.SubElement(fornecedor_element, 'PrecoMedio').text = str(fornecedor.preco_medio)
            ET.SubElement(fornecedor_element, 'ConfiabilidadeMedia').text = str(fornecedor.confiabilidade_media)
            ET.SubElement(fornecedor_element, 'FlexibilidadeMedia').text = str(fornecedor.flexibilidade_media)
            ET.SubElement(fornecedor_element, 'ParceriaMedia').text = str(fornecedor.parceria_media)

        tree = ET.ElementTree(root)
        tree.write(response, encoding='utf-8', xml_declaration=True)

        return response

    def exportar_pdf(self, desempenho_fornecedores):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        subtitle_style = ParagraphStyle(name='Subtitle', fontSize=12, spaceAfter=10)

        title = "Desempenho de Fornecedores"
        subtitle = f"Período: {self.request.POST.get('data_inicio')} a {self.request.POST.get('data_fim')}"
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Spacer(1, 12))

        data = [['Fornecedor', 'Qualidade Média', 'Prazo de Entrega Médio', 'Preço Médio', 'Confiabilidade Média', 'Flexibilidade Média', 'Parceria Média']]
        for fornecedor in desempenho_fornecedores:
            data.append([
                fornecedor.name,
                f"{fornecedor.qualidade_media:.2f}",
                f"{fornecedor.prazo_entrega_medio:.2f}",
                f"{fornecedor.preco_medio:.2f}",
                f"{fornecedor.confiabilidade_media:.2f}",
                f"{fornecedor.flexibilidade_media:.2f}",
                f"{fornecedor.parceria_media:.2f}"
            ])

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
        return FileResponse(buffer, as_attachment=True, filename='desempenho_fornecedores.pdf')

    def add_page_number(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200*mm, 20*mm, text)

class ProdutosMaisCotadosView(TemplateView):
    template_name = 'relatorios/produtos_mais_cotados.html'

    def get(self, request):
        # Lógica para obter dados do relatório
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if data_inicio and data_fim:
            itens_cotacao = ItemCotacao.objects.filter(cotacao__data_abertura__gte=data_inicio, cotacao__data_fechamento__lte=data_fim)
        else:
            itens_cotacao = ItemCotacao.objects.all()

        produtos_mais_cotados = itens_cotacao.values('produto__name').annotate(total=Count('produto')).order_by('-total')[:10]

        context = {
            'produtos_mais_cotados': produtos_mais_cotados,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # Lógica para exportar o relatório
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        formato = request.POST.get('formato')

        if data_inicio and data_fim:
            itens_cotacao = ItemCotacao.objects.filter(cotacao__data_abertura__gte=data_inicio, cotacao__data_fechamento__lte=data_fim)
        else:
            itens_cotacao = ItemCotacao.objects.all()

        produtos_mais_cotados = itens_cotacao.values('produto__name').annotate(total=Count('produto')).order_by('-total')[:10]

        if formato == 'csv':
            return self.exportar_csv(produtos_mais_cotados)
        elif formato == 'xml':
            return self.exportar_xml(produtos_mais_cotados)
        elif formato == 'pdf':
            return self.exportar_pdf(produtos_mais_cotados)
        else:
            return JsonResponse({'erro': 'Formato inválido'})

    def exportar_csv(self, produtos_mais_cotados):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="produtos_mais_cotados.csv"'

        writer = csv.writer(response)
        writer.writerow(['Produto', 'Quantidade de Cotações'])

        for produto in produtos_mais_cotados:
            writer.writerow([produto['produto__name'], produto['total']])

        return response

    def exportar_xml(self, produtos_mais_cotados):
        response = HttpResponse(content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="produtos_mais_cotados.xml"'

        root = ET.Element('ProdutosMaisCotados')
        for produto in produtos_mais_cotados:
            produto_element = ET.SubElement(root, 'Produto')
            ET.SubElement(produto_element, 'Nome').text = produto['produto__name']
            ET.SubElement(produto_element, 'TotalCotacoes').text = str(produto['total'])

        tree = ET.ElementTree(root)
        tree.write(response, encoding='utf-8', xml_declaration=True)

        return response

    def exportar_pdf(self, produtos_mais_cotados):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        subtitle_style = ParagraphStyle(name='Subtitle', fontSize=12, spaceAfter=10)

        title = "Produtos Mais Cotados"
        subtitle = f"Período: {self.request.POST.get('data_inicio')} a {self.request.POST.get('data_fim')}"
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Spacer(1, 12))

        data = [['Produto', 'Quantidade de Cotações']]
        for produto in produtos_mais_cotados:
            data.append([produto['produto__name'], produto['total']])

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
        return FileResponse(buffer, as_attachment=True, filename='produtos_mais_cotados.pdf')

    def add_page_number(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(200 * mm, 20 * mm, text)

class ProdutosMaiorVariacaoPrecoView(TemplateView):
    template_name = 'relatorios/produtos_maior_variacao_preco.html'

class ProdutosSemFornecedorView(TemplateView):
    template_name = 'relatorios/produtos_sem_fornecedor.html'

class PedidosAgrupadosFornecedorView(TemplateView):
    template_name = 'relatorios/pedidos_agrupados_fornecedor.html'

class HistoricoPedidosAgrupadosView(TemplateView):
    template_name = 'relatorios/historico_pedidos_agrupados.html'
