from django.shortcuts import redirect
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from products.models import Product, Departamento, Category, Subcategory
from django.views.generic import View, UpdateView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Cotacao
from .forms import CotacaoForm
from django.contrib import messages
from .models import ItemCotacao
from django.urls import get_resolver
from .forms import ItemCotacaoForm
from dal import autocomplete



class CotacaoCreateView(CreateView):
    model = Cotacao
    form_class = CotacaoForm
    template_name = 'cotacao/cotacao_create.html'
    success_url = reverse_lazy('cotacao:cotacao_create') 
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cotação criada com sucesso!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cotacoes'] = Cotacao.objects.all()  # Adiciona todas as cotações ao contexto
        return context

    
    
class AddProductToCotacaoView(CreateView):
    model = ItemCotacao
    form_class = ItemCotacaoForm
    template_name = 'cotacao/add_product_to_cotacao.html'

    def form_valid(self, form):
        form.instance.cotacao_id = self.kwargs['cotacao_id']
        return super().form_valid(form)

    def get_success_url(self):
        # Redireciona para a página da cotação após adicionar o produto
        return reverse_lazy('cotacao:cotacao_create', kwargs={'pk': self.kwargs['cotacao_id']})
    
    
class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(sku__icontains=self.q) | Q(ean__icontains=self.q))
        return qs


class ToggleCotacaoStatusView(UpdateView):
    model = Cotacao
    fields = ['status']  # Aqui você especificaria quais campos são editáveis, se necessário
    template_name = 'cotacao/cotacao_create.html'

    def post(self, request, *args, **kwargs):
        cotacao = self.get_object()
        cotacao.status = 'ativo' if cotacao.status == 'inativo' else 'inativo'
        cotacao.save()
        return redirect('cotacao:cotacao_create')  # Redireciona de volta à lista após a mudança


class ProdutoAPI(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        departamento_id = request.GET.get('departamento_id')
        categoria_id = request.GET.get('categoria_id')
        subcategoria_id = request.GET.get('subcategoria_id')


        produtos = Product.objects.all()
        if q:
            produtos = produtos.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(ean__icontains=q))
        if departamento_id:
            produtos = produtos.filter(departamento_id=departamento_id)
        if categoria_id:
            produtos = produtos.filter(categoria_id=categoria_id)
        if subcategoria_id:
            produtos = produtos.filter(subcategoria_id=subcategoria_id)

        print("Produtos encontrados:", produtos.count())

        data = [{'id': p.id, 'nome': p.name, 'sku': p.sku, 'ean': p.ean} for p in produtos]
        return JsonResponse(data, safe=False)


class DepartamentoAPI(View):
    def get(self, request, *args, **kwargs):
        departamentos = Departamento.objects.all().values('id', 'nome')  # Alterado de 'name' para 'nome'
        print(get_resolver().url_patterns)
        return JsonResponse(list(departamentos), safe=False)
    
class CategoriaAPI(View):
    def get(self, request, *args, **kwargs):
        categorias = Category.objects.all().values('id', 'name')
        return JsonResponse(list(categorias), safe=False)
    
class SubcategoriaAPI(View):
    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')
        subcategorias = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategorias), safe=False) 
    
    
class ItensCotacaoAPI(View):
    def get(self, request, *args, **kwargs):
        cotacao_id = kwargs.get('cotacao_id')
        itens = ItemCotacao.objects.filter(cotacao_id=cotacao_id).select_related('produto').values(
            'produto__name', 'quantidade', 'tipo_volume', 'observacao', 'produto__id')
        return JsonResponse(list(itens), safe=False)
  
    



