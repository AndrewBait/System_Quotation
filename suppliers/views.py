from django.urls import reverse_lazy, reverse  # Corrigido para importar reverse
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import SupplierForm, SupplierFilterForm, SupplierRatingsForm, SupplierStatusFilterForm
from .models import Departamento, Supplier, Category, Subcategory
from django.db.models import Avg
import logging
import csv
import xml.etree.ElementTree as ET
from django.test import TestCase


logger = logging.getLogger(__name__) # Cria um logger com o nome do módulo

class SupplierFormMixin: # Mixin para adicionar funcionalidades ao formulário de fornecedor
    def form_valid(self, form):
        self.object = form.save(commit=False)
        delivery_days = form.cleaned_data.get('delivery_days')
        if delivery_days:
            self.object.delivery_days = delivery_days  # Já está formatado como string separada por vírgulas
        self.object.save()
        form.save_m2m()
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)




def get_categories(request): # Função para retornar as categorias de um departamento
    department_id = request.GET.get('department_id')
    if department_id:  # Verifica se department_id não está vazio
        try:
            department_id = int(department_id)  # Tenta converter department_id para inteiro
            categories = Category.objects.filter(department_id=department_id).values('id', 'name')
        except ValueError:  # Caso department_id não seja um inteiro válido
            categories = []
    else:
        categories = []  # Se department_id estiver vazio, define categories como uma lista vazia
    
    return JsonResponse(list(categories), safe=False)




@method_decorator(login_required(login_url=''), name='dispatch') 
def sua_view_para_o_formulário(request): # Função para exibir o formulário
    departamentos = Departamento.objects.all()
    return render(request, 'seu_template.html', {'departamentos': departamentos})




@method_decorator(login_required, name='dispatch')
class SupplierCreateView(PermissionRequiredMixin, SupplierFormMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    permission_required = 'suppliers.add_supplier'
    
    def form_valid(self, form): # Método para lidar com formulários válidos
        supplier = form.save(commit=False) # Salva o objeto Supplier
        supplier.price_rating = self.request.POST.get('price_rating') # Salva a avaliação de preço
        supplier.reliability_rating = self.request.POST.get('reliability_rating') # Salva a avaliação de confiabilidade
        delivery_days = ','.join(self.request.POST.getlist('delivery_days[]')) # Obtém os dias de entrega selecionados
        supplier.delivery_days = delivery_days    # Salva os dias de entrega   
        supplier.user = self.request.user  # Associa o fornecedor ao usuário atual
        supplier.save() # Salva o objeto Supplier com todos os dados atualizados
        form.save_m2m() # Salva as relações ManyToMany
        messages.success(self.request, 'Fornecedor cadastrado com sucesso!')
        return redirect('suppliers:supplier_new')

    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)                   
    

    
    def get_context_data(self, **kwargs): # Adiciona os dias de entrega ao contexto
        context = super().get_context_data(**kwargs)
        context['delivery_days_list'] = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        if self.object: # Se o objeto existir
            context['selected_days'] = self.object.delivery_days.split(',') if self.object.delivery_days else []
        context['departamentos'] = Departamento.objects.all() # Adiciona os departamentos ao contexto
        context['selected_days'] = self.object.delivery_days.split(',') if self.object and self.object.delivery_days else []
        return context
    
    def get_initial(self): # Adiciona o usuário atual ao campo user
        initial = super().get_initial() # Chama o método get_initial da classe pai
        initial['user'] = self.request.user # Adiciona o usuário atual ao campo user
        return initial




@method_decorator(login_required, name='dispatch')
class SupplierListView(PermissionRequiredMixin, ListView):  # View para listar fornecedores
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 6
    permission_required = 'suppliers.view_supplier'

    def get_queryset(self): # Método para filtrar os fornecedores
        queryset = super().get_queryset()
        department_id = self.request.GET.get('department')
        category_id = self.request.GET.get('category')
        subcategory_id = self.request.GET.get('subcategory')
        status = self.request.GET.get('status')

        if department_id: # Se department_id não estiver vazio
            queryset = queryset.filter(departments__id=department_id) # Filtra os fornecedores pelo departamento
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategories__id=subcategory_id)
        if status:
            queryset = queryset.filter(active=status == 'True')

        return queryset

    def get_context_data(self, **kwargs): # Adiciona os departamentos ao contexto
        context = super().get_context_data(**kwargs)
        context['suppliers'] = context['object_list']  # Adiciona 'suppliers' ao contexto
        context['departments'] = Departamento.objects.all()
        context['categories'] = Category.objects.all()
        context['subcategories'] = Subcategory.objects.all()
        context['form'] = SupplierFilterForm(self.request.GET or None)
        context['status_form'] = SupplierStatusFilterForm(self.request.GET or None)
        return context


@method_decorator(login_required, name='dispatch')
class SupplierDetailView(PermissionRequiredMixin, DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    permission_required = 'suppliers.view_supplier'
    
    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            messages.error(self.request, 'Fornecedor não encontrado ou já excluído.')
            return redirect('suppliers:supplier_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.get_object()
        context['delivery_days_list'] = supplier.delivery_days.split(',') if supplier.delivery_days else []
        return context



class RatingsUpdateView(LoginRequiredMixin, View): # View para atualizar as avaliações de um fornecedor
    def post(self, request, *args, **kwargs):
        supplier = get_object_or_404(Supplier, pk=kwargs.get('pk'))
        supplier.update_ratings(
            quality=request.POST.get('quality_rating'),
            delivery_time=request.POST.get('delivery_time_rating'),
            price=request.POST.get('price_rating'),
            reliability=request.POST.get('reliability_rating'),
            flexibility=request.POST.get('flexibility_rating'),
            partnership=request.POST.get('partnership_rating'),
            comments=request.POST.get('comments')
        )
        return HttpResponseRedirect(reverse('suppliers:supplier_detail', kwargs={'pk': supplier.pk}))
    


@method_decorator(login_required, name='dispatch')
class SupplierUpdateView(PermissionRequiredMixin, SupplierFormMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    permission_required = 'suppliers.change_supplier'
    
    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            messages.error(self.request, 'Fornecedor não encontrado ou já excluído.')
            return redirect('suppliers:supplier_list')

    def post(self, request, *args, **kwargs): # Método para lidar com requisições POST
        self.object = self.get_object()
        if 'save_ratings' in request.POST:
            ratings_form = SupplierRatingsForm(request.POST, instance=self.object)
            if ratings_form.is_valid():
                ratings_form.save()
                return HttpResponseRedirect(self.get_success_url() + '?success=true')
            else:
                return self.form_invalid(ratings_form)
        else:
            return super().post(request, *args, **kwargs)

    def handle_ratings(self, request): # Método para lidar com as avaliações
        form = self.get_form_class()(instance=self.object, data=request.POST)
        if form.is_valid():
            return self.form_valid_ratings(form)
        else:
            return self.form_invalid(form)   
        
    def form_valid_ratings(self, form):
        # Aqui você salva apenas os dados relacionados às avaliações e comentários
        form.instance.save_ratings_only()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Assegure que self.object está disponível e possui a propriedade delivery_days
        if self.object and self.object.delivery_days:
            context['selected_days'] = self.object.delivery_days.split(',')
        else:
            context['selected_days'] = []
        context['delivery_days_list'] = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        return context
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        delivery_days = form.cleaned_data.get('delivery_days')
        self.object.delivery_days = ','.join(delivery_days) if delivery_days else ''
        self.object.save()
        form.save_m2m()
        return super().form_valid(form)

        # # Processar dados de avaliações somente se o formulário de avaliações for enviado
        # if 'save_ratings' in self.request.POST:
        #     price_rating = self.request.POST.get('price_rating')
        #     reliability_rating = self.request.POST.get('reliability_rating')
        #     self.object.price_rating = price_rating
        #     self.object.reliability_rating = reliability_rating
        # supplier.save()
        # form.save_m2m()
        # self.object.save()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delivery_days_list'] = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        context['selected_days'] = self.object.delivery_days.split(',') if self.object.delivery_days else []
        return context
        
        

    # def form_valid(self, form):
    #     supplier = form.save(commit=False)  # Salva o objeto Supplier 
    #     delivery_days = self.request.POST.getlist('delivery_days[]')
    #     if delivery_days:
    #         supplier.delivery_days = ','.join(delivery_days)
    #     supplier.save()                 # Salva o objeto Supplier com todos os dados atualizados
    #     form.save_m2m()                 # Salva as relações ManyToMany
    #     return super().form_valid(form)
    def get_context_data(self, **kwargs): # Adiciona os dias de entrega ao contexto
        context = super().get_context_data(**kwargs)
        context['selected_days'] = self.object.delivery_days.split(',') if self.object.delivery_days else []
        return context
    
    def form_invalid(self, form):  
        # Exibir mensagem de erro
        return super().form_invalid(form)

    def get_success_url(self): # Método para obter a URL de sucesso
        return reverse_lazy('suppliers:supplier_detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class SupplierDeleteView(PermissionRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    permission_required = 'suppliers.delete_supplier'

    def delete(self, request, *args, **kwargs):
        logging.debug("Tentando deletar o fornecedor com ID: %s", self.kwargs.get('pk'))
        try:
            return super().delete(request, *args, **kwargs)
        except Http404:
            messages.error(request, 'Fornecedor não encontrado ou já excluído.')
            return redirect(self.success_url)


@method_decorator(login_required(login_url=''), name='dispatch')
def create_supplier(request): # Função para criar um fornecedor
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST['email'], password=request.POST['senha'])
        supplier = Supplier(user=user)
        supplier.save()



def get_categories(request): # Função para retornar as categorias de um departamento
    department_id = request.GET.get('department_id')
    if department_id:
        try:
            department_id = int(department_id)  # Certifique-se que é um inteiro
            categories = Category.objects.filter(department_id=department_id).values('id', 'name')
            return JsonResponse(list(categories), safe=False)
        except ValueError:
            # Lidar com a conversão falha
            return JsonResponse({'error': 'Invalid department ID'}, status=400)
    else:
        return JsonResponse({'error': 'Department ID is missing'}, status=400)
    


def get_subcategories(request): # Função para retornar as subcategorias de uma categoria
    category_id = request.GET.get('category_id')
    subcategories = list(Subcategory.objects.filter(category_id=category_id).values('id', 'name'))
    return JsonResponse(subcategories, safe=False)



class TestCategoryView(TestCase): # Classe de teste para a view de categorias
    def test_get_categories(self):
        response = self.client.get(reverse('ajax_get_categories'), {'department_id': 1})
        self.assertEqual(response.status_code, 200)