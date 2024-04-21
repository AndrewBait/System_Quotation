from django.views import View
from django.http import Http404, JsonResponse
from django.db.models import Q
from products.models import Product, Departamento, Category, Subcategory
from django.views.generic import View, RedirectView
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Cotacao
from .forms import CotacaoForm
from django.contrib import messages
from .models import ItemCotacao
from django.urls import get_resolver
from .forms import ItemCotacaoForm
from dal import autocomplete
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin



class CotacaoMainView(TemplateView):
    template_name = 'cotacao/cotacoes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao_form = CotacaoForm()
        cotacoes = Cotacao.objects.all()  # Assumindo que você tem uma instância inicial aqui
        context['cotacao_form'] = cotacao_form
        context['cotacoes'] = cotacoes
        context['usuarios'] = User.objects.all()
        context['departamentos'] = Departamento.objects.all()
        context['active_tab'] = self.request.GET.get('tab', 'default_tab_name')
        # Adicionar qualquer outra variável necessária

        return context

class CotacaoCreateView( LoginRequiredMixin,CreateView):
    model = Cotacao
    form_class = CotacaoForm
    template_name = 'cotacao/cotacao_list.html'
    success_url = reverse_lazy('cotacao:cotacoes')  # Ajuste conforme necessário

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        return context

    def form_valid(self, form):        
        response = super().form_valid(form)
        cotacao = form.save(commit=False)  # Não salva o formulário imediatamente
        cotacao.usuario_criador = self.request.user  # Atribui o usuário logado
        cotacao.save()
        messages.success(self.request, "Cotação criada com sucesso!", extra_tags='success')
        return response
    
class CotacaoListView(ListView):
    model = Cotacao
    template_name = 'cotacao/cotacao_list.html'  # Template específico para listagem
    context_object_name = 'cotacoes'
    

    def get_queryset(self):
        queryset = super().get_queryset()
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        status = self.request.GET.get('status')
        usuario_id = self.request.GET.get('usuario')
        departamento_id = self.request.GET.get('departamento')

        # Aplicar filtros
        if data_inicio:
            queryset = queryset.filter(data_abertura__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_fechamento__lte=data_fim)
        if status:
            queryset = queryset.filter(status=status)
        if usuario_id:
            queryset = queryset.filter(usuario_criador_id=usuario_id)
        if departamento_id:
            queryset = queryset.filter(departamento_id=departamento_id)

        print("Cotações encontradas:", queryset.count())
        print("Data de início:", data_inicio)
        print("Data de fim:", data_fim)
        print("Status:", status)
        print("Usuário:", usuario_id)
        print("Departamento:", departamento_id)
        print("Queryset:", queryset)
        print("Queryset após aplicar todos os filtros:", queryset.query)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuarios'] = User.objects.all()
        context['departamentos'] = Departamento.objects.all()
        # Adicionar qualquer outra variável necessária
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cotacoes = self.get_queryset()
            data = [{'id': cotacao.id, 'nome': cotacao.nome, 'status': cotacao.get_status_display(), 'usuario': cotacao.usuario_criador.username, 'departamento': cotacao.departamento.nome, 'data_abertura': cotacao.data_abertura, 'data_fechamento': cotacao.data_fechamento} for cotacao in cotacoes]
            return JsonResponse(data, safe=False)
        return super().get(request, *args, **kwargs)


    
    
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


class ToggleCotacaoStatusView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            cotacao = Cotacao.objects.get(pk=kwargs['pk'])
        except Cotacao.DoesNotExist:
            raise Http404("Cotação não encontrada")

        cotacao.status = 'inativo' if cotacao.status == 'ativo' else 'ativo'
        cotacao.save()
        return reverse('cotacao:cotacao_list')


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
  
    
class CotacaoUpdateView(UpdateView):
    model = Cotacao
    form_class = CotacaoForm
    template_name = 'cotacao/add_product_to_cotacao.html'
    success_url = reverse_lazy('cotacao:cotacao_create')  # ajuste para o nome correto da URL de listagem

    def form_valid(self, form):
        messages.success(self.request, 'Cotação atualizada com sucesso!')
        return super().form_valid(form)
    

class CotacaoDeleteView(DeleteView):
    model = Cotacao
    success_url = reverse_lazy('cotacao:cotacoes')  # Redireciona para a lista após exclusão

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


