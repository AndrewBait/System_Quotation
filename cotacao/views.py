from django.shortcuts import get_object_or_404, render
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .forms import EnviarCotacaoForm
from suppliers.models import Supplier
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




class CotacaoListView(ListView):
    model = Cotacao
    template_name = 'cotacao/cotacao_list.html'
    context_object_name = 'cotacoes'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departamentos'] = Departamento.objects.all().order_by('nome')
        context['usuarios'] = User.objects.all().order_by('username')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        status = self.request.GET.get('status')
        usuario_id = self.request.GET.get('usuario')
        departamento_id = self.request.GET.get('departamento')
        prazo = self.request.GET.get('prazo')

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
        if prazo:
            queryset = queryset.filter(prazo=prazo)

        return queryset
    

class CotacaoDeleteView(DeleteView):
    model = Cotacao
    template_name = 'cotacao/cotacao_confirm_delete.html'
    success_url = reverse_lazy('cotacao:cotacao_list')  # Para onde ir após a exclusão

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Excluir Cotação'
        return context



class CotacaoCreateView( LoginRequiredMixin,CreateView):
    model = Cotacao
    form_class = CotacaoForm
    template_name = 'cotacao/cotacao_create.html'
    success_url = reverse_lazy('cotacao:cotacao_list')  # Ajuste conforme necessário

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
    

class CotacaoUpdateView(UpdateView):
    model = Cotacao
    form_class = CotacaoForm
    template_name = 'cotacao/cotacao_update.html'
    success_url = reverse_lazy('cotacao:cotacao_list')  # ajuste para o nome correto da URL de listagem

    def form_valid(self, form):

        cotacao = form.save(commit=False) 
        cotacao.usuario_criador = self.request.user  # Atribui o usuário logado
        cotacao.save()
        messages.success(self.request, 'Cotação atualizada com sucesso!')
        return super().form_valid(form)


class EnviarCotacaoView(FormView):
    template_name = 'cotacao/enviar_cotacao.html'
    form_class = EnviarCotacaoForm
    success_url = reverse_lazy('cotacao:cotacao_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        cotacao = Cotacao.objects.get(pk=self.kwargs['pk'])
        busca = self.request.GET.get('busca', '')
        departamento_id = self.request.GET.get('departamento', '')

        fornecedores_query = Supplier.objects.all().order_by('name')
        if departamento_id:
            fornecedores_query = fornecedores_query.filter(departments__id=departamento_id)
        if busca:
            fornecedores_query = fornecedores_query.filter(
                Q(name__icontains=busca) | Q(company__icontains=busca)
            )

        paginator = Paginator(fornecedores_query, 6)  # 6 fornecedores por página
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['cotacao'] = cotacao
        context['fornecedores'] = fornecedores_query
        context['departamentos'] = Departamento.objects.all().order_by('nome')
        context['page_obj'] = page_obj
        return context

    def form_valid(self, form):
        fornecedores_selecionados = form.cleaned_data['fornecedores']
        cotacao = Cotacao.objects.get(pk=self.kwargs['pk'])  # Recuperando novamente a cotação
        # Aqui você colocaria o código para processar a cotação e enviar aos fornecedores selecionados
        messages.success(self.request, 'Cotação enviada com sucesso!')
        return super().form_valid(form)


class PesquisaFornecedorAjaxView(View):
    def get(self, request, *args, **kwargs):
        busca = request.GET.get('termo', '')
        departamento_id = request.GET.get('departamento', '')

        fornecedores_query = Supplier.objects.all().order_by('name')
        if departamento_id:
            fornecedores_query = fornecedores_query.filter(departments__id=departamento_id)
        if busca:
            fornecedores_query = fornecedores_query.filter(name__icontains=busca)

        dados = [{
            'id': fornecedor.id,
            'name': fornecedor.name,
            'departments': list(fornecedor.departments.all().values_list('nome', flat=True)),
            'email': fornecedor.email
        } for fornecedor in fornecedores_query]

        return JsonResponse(dados, safe=False)


class ListProductsToAddView(TemplateView):
    template_name = 'cotacao/list_products_to_add.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao = get_object_or_404(Cotacao, pk=self.kwargs['cotacao_id'])
        produtos_ja_adicionados = ItemCotacao.objects.filter(cotacao=cotacao).values_list('produto', flat=True)
        context['form'] = ItemCotacaoForm()
        context['produtos'] = Product.objects.exclude(id__in=produtos_ja_adicionados)
        context['cotacao'] = cotacao
        return context


class ListProductsView(ListView):
    model = Product
    template_name = 'cotacao/list_products_to_add.html'  # Ajuste para o template correto
    context_object_name = 'produtos'
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Product.objects.filter(
                Q(name__icontains=search_query) |
                Q(sku__icontains=search_query) |
                Q(ean__icontains=search_query)
            )
        else:
            return Product.objects.all()
    
    
class AddProductToCotacaoView(CreateView):
    model = ItemCotacao
    form_class = ItemCotacaoForm
    template_name = 'cotacao/add_product_to_cotacao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Certifique-se de que a cotação está sendo passada corretamente
        cotacao = get_object_or_404(Cotacao, id=self.kwargs['cotacao_id'])
        context['cotacao'] = cotacao
        return context

    def form_valid(self, form):
        form.instance.cotacao_id = self.kwargs['cotacao_id']
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cotacao:list_products_to_add', kwargs={'cotacao_id': self.kwargs['cotacao_id']})
    
    
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