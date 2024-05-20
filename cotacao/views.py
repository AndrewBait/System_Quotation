import hashlib
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from products.models import Product, Departamento, Category, Subcategory
from django.views.generic import View, RedirectView
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import CotacaoForm
from django.contrib import messages
from .models import ItemCotacao, FornecedorCotacaoToken
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
from django.core.mail import send_mail
from .models import Cotacao
from django.db.transaction import atomic
from django.db import transaction



class CotacaoListView(ListView):
    model = Cotacao
    template_name = 'cotacao/cotacao_list.html'
    context_object_name = 'cotacoes'
    paginate_by = 6


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departamentos'] = Departamento.objects.all().order_by('nome')
        context['usuarios'] = User.objects.all().order_by('username')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        status = self.request.GET.get('status', 'ativo')
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
    success_url = reverse_lazy('cotacao:cotacao_create')  # Ajuste conforme necessário

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
    
    def get_success_url(self):
        return reverse('cotacao:enviar_cotacao', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao_id = self.kwargs['pk']
        cotacao = Cotacao.objects.get(pk=cotacao_id)
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
        context['fornecedores'] = page_obj  # Passar page_obj em vez de fornecedores_query para respeitar a paginação
        context['departamentos'] = Departamento.objects.all().order_by('nome')
        context['page_obj'] = page_obj
        return context

    def form_valid(self, form):
        cotacao = Cotacao.objects.get(pk=self.kwargs['pk'])
        fornecedores_selecionados = form.cleaned_data['fornecedores']
        emails_enviados = 0
        for fornecedor in fornecedores_selecionados:
            token = FornecedorCotacaoToken.objects.create(
                cotacao=cotacao,
                fornecedor=fornecedor
            )
            cnpj_slice = str(fornecedor.cnpj)[:4]
            # Gerar hash do CNPJ truncado
            hash_object = hashlib.sha256(cnpj_slice.encode())
            cnpj_hash = hash_object.hexdigest()
            link = self.request.build_absolute_uri(
                reverse("respostas:responder_cotacao", kwargs={
                    "cotacao_uuid": cotacao.uuid,
                    "fornecedor_id": fornecedor.id,
                    "token": token.token
                }) + f"?auth={cnpj_hash}"
            )
            try:
                send_mail(
                    'Nova Cotação Disponível',
                    f'Olá {fornecedor.name}, uma nova cotação está disponível. Por favor, acesse o link para responder: {link}',
                    'andrewsilva811@gmail.com',
                    [fornecedor.email],
                    fail_silently=False,
                )
                emails_enviados += 1
            except Exception as e:
                messages.error(self.request, f'Erro ao enviar email para {fornecedor.email}: {str(e)}')
                continue
        if emails_enviados > 0:
            messages.success(self.request, f'Cotação enviada com sucesso para {emails_enviados} fornecedore(s)!')
        else:
            messages.error(self.request, 'Não foi possível enviar a cotação para nenhum fornecedor.')

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
    



# class ResponderCotacaoView(UpdateView):
#     model = RespostaCotacao
#     form_class = RespostaCotacaoForm
#     template_name = 'cotacao/responder_cotacao.html'

#     def get_success_url(self):
#         messages.success(self.request, "Resposta enviada com sucesso!")
#         return reverse('cotacao:cotacao_success')

#     def get_object(self, queryset=None):
#         cotacao_pk = self.kwargs.get('pk')
#         fornecedor_pk = self.kwargs.get('fornecedor_id')
#         # Utiliza get_or_create para assegurar que apenas uma instância é manipulada
#         obj, created = RespostaCotacao.objects.get_or_create(
#             cotacao_id=cotacao_pk, 
#             fornecedor_id=fornecedor_pk,
#             defaults={'cotacao_id': cotacao_pk, 'fornecedor_id': fornecedor_pk}
#         )
#         return obj

#     def form_valid(self, form):
#         # Quando o formulário é válido
#         form.save()
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, "Erro no formulário. Por favor, verifique os dados inseridos.")
#         return super().form_invalid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['itens_cotacao'] = self.object.cotacao.itens_cotacao.all()
#         return context
    


# class SuccessView(TemplateView):
#     template_name = 'cotacao/success_page.html'


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

class UpdateItemCotacaoView(UpdateView):
    model = ItemCotacao
    fields = ['quantidade', 'tipo_volume', 'observacao']
    template_name = 'cotacao/update_item_cotacao.html'
     

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Item atualizado com sucesso!")
        return response
    
    def get_success_url(self):
        cotacao_id = self.object.cotacao.id  # Obtém o ID da cotação do item atualizado
        return reverse('cotacao:add_product_to_cotacao', kwargs={'cotacao_id': cotacao_id})

class DeleteItemCotacaoView(DeleteView):
    model = ItemCotacao
    success_url = reverse_lazy('cotacao:cotacao_list')  # ajuste para o nome correto da URL de listagem

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Item removido com sucesso!")
        return response
    
    
  
class AddProductToCotacaoView(CreateView):
    model = ItemCotacao
    form_class = ItemCotacaoForm
    template_name = 'cotacao/add_product_to_cotacao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao = get_object_or_404(Cotacao, id=self.kwargs['cotacao_id'])
        context['cotacao'] = cotacao
        return context

    def form_valid(self, form):
        cotacao_id = self.kwargs['cotacao_id']
        produto_id = form.cleaned_data['produto'].id
        # Verificar se o produto já está na cotação
        if ItemCotacao.objects.filter(cotacao_id=cotacao_id, produto_id=produto_id).exists():
            messages.error(self.request, "Este produto já foi adicionado à cotação.") # Mensagem de erro
            return super().form_valid(form)
        form.instance.cotacao_id = cotacao_id
        form.save()
        messages.success(self.request, "Produto adicionado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cotacao:list_products_to_add', kwargs={'cotacao_id': self.kwargs['cotacao_id']})
    
    
    def post(self, request, cotacao_id):
        produto_id = request.POST.get('produto_id')
        quantidade = request.POST.get('quantidade')
        tipo_volume = request.POST.get('tipo_volume')
        observacao = request.POST.get('observacao')

        cotacao = get_object_or_404(Cotacao, id=cotacao_id)
        item = ItemCotacao(
            cotacao=cotacao,
            produto_id=produto_id,
            quantidade=quantidade,
            tipo_volume=tipo_volume,
            observacao=observacao
        )
        item.save()

        return JsonResponse({"message": "Produto adicionado com sucesso!"}, status=200)
    
    
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