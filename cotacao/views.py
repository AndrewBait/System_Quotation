from turtle import pd
from urllib import request
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, FormView
from .models import Departamento, Cotacao, ItemCotacao
from .forms import CotacaoForm, ItemCotacaoForm, DepartamentoForm
from suppliers.models import Supplier
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.models import Product
from django.db import IntegrityError, DatabaseError
from django.http import JsonResponse
from products.models import Product
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.urls import get_resolver


def debug_urls(request):
    for url in get_resolver().reverse_dict.keys():
        print(url)
    return HttpResponse("Check your console")


def produtos_api(request):
    query = request.GET.get('q', '')  # Recebe o parâmetro de pesquisa da query string
    produtos = Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query) | Q(ean__icontains=query)
    ).values('id', 'name', 'sku', 'ean')[:5]  # Limita a 5 resultados
    produtos_list = list(produtos)
    return JsonResponse(produtos_list, safe=False)


@require_POST
def add_product_to_cotacao(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    volume_type = request.POST.get('volume_type')
    cotacao_id = request.POST.get('cotacao_id')  # Certifique-se que este ID está sendo passado corretamente

    # Log para verificar se estamos recebendo todos os dados
    print(f"Received data: product_id={product_id}, quantity={quantity}, volume_type={volume_type}, cotacao_id={cotacao_id}")

    if not all([product_id, quantity, volume_type, cotacao_id]):
        print("Missing data")
        return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

    try:
        product = get_object_or_404(Product, id=product_id)
        cotacao = get_object_or_404(Cotacao, id=cotacao_id)
        
        item_cotacao = ItemCotacao(product=product, quantity=quantity, volume_type=volume_type, cotacao=cotacao)
        item_cotacao.save()
        
        print("Product added successfully")
        return JsonResponse({'status': 'success', 'message': 'Produto adicionado à cotação'})
    except Exception as e:
        # Log do erro
        print(f"Error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


    print("Unexpected path in function")
    return JsonResponse({'status': 'error', 'message': 'Unexpected error occurred'}, status=500)

@require_POST
def add_product_to_cotacao(request):
    print("Recebido: ", request.POST)  


class CotacaoListView(ListView):
    model = Cotacao
    template_name = 'cotacao/cotacao_list.html'
    context_object_name = 'cotacoes'    
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['show_cotacao_tabs'] = True 
        context['departamentos'] = Departamento.objects.all()
        total_abertas = Cotacao.objects.filter(status='ativo').count()
        total_fechadas = Cotacao.objects.filter(status='inativo').count()
        context['total_abertas'] = total_abertas
        context['total_fechadas'] = total_fechadas
        context['total_cotacoes'] = total_abertas + total_fechadas
        cotacoes_list = Cotacao.objects.all()
        paginator = Paginator(cotacoes_list, self.paginate_by)
        
        
        
        page = self.request.GET.get('page')
        try:
            cotacoes = paginator.page(page)
        except PageNotAnInteger:
            cotacoes = paginator.page(1)
        except EmptyPage:
            cotacoes = paginator.page(paginator.num_pages)

        context['cotacoes'] = cotacoes
        return context


class CotacaoDetailView(DetailView):
    model = Cotacao
    template_name = 'cotacao/cotacao_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_cotacao_tabs'] = True
        return context


class CotacaoCreateView(CreateView):
    model = Cotacao
    form_class = CotacaoForm
    template_name = 'cotacao/cotacao_form_list.html'
    success_url = reverse_lazy('cotacao:cotacao_list_create')
    
    def form_valid(self, form):
        try:
            # Salva a nova cotação
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, 'Houve um problema ao salvar a cotação, talvez devido a dados duplicados.')
            return self.form_invalid(form)
        except DatabaseError:
            form.add_error(None, 'Erro de conexão com o banco de dados. Tente novamente mais tarde.')
            return self.form_invalid(form)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_cotacao_tabs'] = True
        return context

class CotacaoListCreateView(FormView):
    template_name = 'cotacao/cotacao_form_list.html'
    form_class = CotacaoForm
    success_url = reverse_lazy('cotacao:cotacao_list_create')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Este método será chamado quando a requisição for POST, ou seja, ao salvar uma nova cotação
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(CotacaoListCreateView, self).get_context_data(**kwargs)
        context['cotacoes'] = Cotacao.objects.all()
        context['departamentos'] = Departamento.objects.all()
        context['show_cotacao_tabs'] = True  # Se você precisa controlar a visibilidade das abas
        return context

    def form_valid(self, form):
        # Salva a nova cotação
        form.save()
        return super(CotacaoListCreateView, self).form_valid(form)
    
    def get_success_url(self):
        if self.request.GET.get('from_sidebar'):
            return reverse_lazy('cotacao:cotacao_list') + '?from_sidebar=1'
        else:
            return reverse_lazy('cotacao:cotacao_list')

class CotacaoDeleteView(DeleteView):
    model = Cotacao
    
    def get_success_url(self):
        if self.request.GET.get('from_sidebar'):
            return reverse_lazy('cotacao:cotacao_list') + '?from_sidebar=1'
        else:
            return reverse_lazy('cotacao:cotacao_list')


class AddItemToCotacaoView(CreateView):
    model = ItemCotacao
    form_class = ItemCotacaoForm
    template_name = 'cotacao/itemcotacao_form.html'

    def get_success_url(self):
        return reverse_lazy('cotacao:cotacao_detail', kwargs={'pk': self.kwargs['cotacao_id']})

    def form_valid(self, form):
        form.instance.cotacao_id = self.kwargs['cotacao_id']
        # Verifica se o item já existe para essa cotação
        if ItemCotacao.objects.filter(cotacao_id=self.kwargs['cotacao_id'], produto=form.instance.produto).exists():
            form.add_error('produto', 'Este produto já foi adicionado à cotação.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cotacao'] = get_object_or_404(Cotacao, pk=self.kwargs['cotacao_id'])
        return context
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            form = self.form_class(request.POST)
            if form.is_valid():
                # Cria o item de cotação
                item_cotacao = form.save(commit=False)
                item_cotacao.cotacao_id = self.kwargs['cotacao_id']
                item_cotacao.save()
                return JsonResponse({'status': 'success', 'msg': 'Item adicionado com sucesso!'})
            else:
                return JsonResponse({'status': 'error', 'msg': 'Erro ao adicionar item.'})
        else:
            # Continue com a lógica normal para requisições não AJAX
            return super().post(request, *args, **kwargs)


class EditItemCotacaoView(UpdateView):
    model = ItemCotacao
    form_class = ItemCotacaoForm
    template_name = 'cotacao/itemcotacao_form.html'

    def get_success_url(self):
        return reverse_lazy('cotacao:cotacao_detail', kwargs={'pk': self.object.cotacao.pk})


class DeleteItemCotacaoView(DeleteView):
    model = ItemCotacao
    template_name = 'cotacao/itemcotacao_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('cotacao:cotacao_detail', kwargs={'pk': self.object.cotacao.pk})
    

class DepartamentoCreateView(CreateView):
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'cotacao/departamento_form.html'
    success_url = reverse_lazy('cotacao:departamento_new')

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            departamento_id = request.POST.get("delete")
            departamento = Departamento.objects.get(pk=departamento_id)
            try:
                departamento.delete()
            except ValidationError as e:
                messages.error(request, e.messages[0])
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departamentos'] = Departamento.objects.all().order_by('nome')
        return context


class DepartamentoDeleteView(DeleteView):
    model = Departamento
    success_url = reverse_lazy('cotacao:departamento_new')  
    template_name = 'cotacao/departamento_confirm_delete.html'


def enviar_cotacao_view(request, pk):
    # Busca a cotação pelo pk
    cotacao = get_object_or_404(Cotacao, pk=pk)
    fornecedores = Supplier.objects.all()

    if request.method == 'POST':
        selected_fornecedores = request.POST.getlist('fornecedores')
        for fornecedor_id in selected_fornecedores:
            fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)

            link_resposta = request.build_absolute_uri(
                reverse('answers:submit_answers_by_uuid', kwargs={'uuid': cotacao.uuid})
            )           
            # Criação do contexto para o template de e-mail
            context = {
                'fornecedor': fornecedor,
                'cotacao': cotacao,
                'link_resposta': link_resposta 
            }            
            # Renderiza o conteúdo do e-mail
            html_content = render_to_string('emails/enviar_cotacao.html', context)
            text_content = strip_tags(html_content)
            
            # Envia o e-mail
            send_mail(
                subject='Nova Cotação Disponível',
                message=text_content,
                from_email='seuemail@example.com',
                recipient_list=[fornecedor.email],
                html_message=html_content,
                fail_silently=False,
            )
        return redirect('cotacao:cotacao_list')
    # Renderiza a página para enviar as cotações caso o método não seja POST
    return render(request, 'cotacao/enviar_cotacao.html', {'cotacao': cotacao, 'fornecedores': fornecedores})


def export_cotacoes_excel(request):
    # Pegar cotações do banco de dados
    data = Cotacao.objects.all().values()
    df = pd.DataFrame(data)
    
    # Criar um arquivo Excel
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="cotacoes.xlsx"'
    with pd.ExcelWriter(response) as writer:
        df.to_excel(writer, index=False)

    return HttpResponse("Exportação para Excel não implementada.")


def export_cotacoes_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cotacoes.pdf"'

    p = canvas.Canvas(response)
    y = 800  # Inicializar coordenada y
    cotacoes = Cotacao.objects.all()
    for cotacao in cotacoes:
        p.drawString(100, y, f"Cotação: {cotacao.nome}")
        y -= 40

    p.showPage()
    p.save()
    return HttpResponse("Exportação para PDF não implementada.")

def toggle_status_cotacao(request, pk):
    cotacao = get_object_or_404(Cotacao, pk=pk)
    if cotacao.status == 'ativo':
        cotacao.status = 'inativo'
    else:
        cotacao.status = 'ativo'
    cotacao.save()
    
    # Calcule o total de cotações abertas e fechadas
    total_abertas = Cotacao.objects.filter(status='ativo').count()
    total_fechadas = Cotacao.objects.filter(status='inativo').count()
    total_cotacoes = Cotacao.objects.count()
    
    # Retorna os dados como JSON
    return JsonResponse({
        'total_abertas': total_abertas,
        'total_fechadas': total_fechadas,
        'total_cotacoes': total_cotacoes,
    })

