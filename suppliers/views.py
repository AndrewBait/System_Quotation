from pyexpat.errors import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import SupplierForm, SupplierFilterForm, SupplierRatingsForm, SupplierStatusFilterForm
from .models import Departamento, Supplier, Category, Subcategory
from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Avg

import logging
logger = logging.getLogger(__name__)

class SupplierFormMixin:
    def form_valid(self, form):
        self.object = form.save()
        form.save_m2m()
        
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


def get_categories(request):
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


def supplier_list(request):
    logger.debug("Dados recebidos: %s", request.GET)
    queryset = Supplier.objects.all()
    print("supplier_list view is called")
    form = SupplierFilterForm(request.GET or None)    
    status_form = SupplierStatusFilterForm(request.GET or None)
    suppliers = Supplier.objects.all().order_by('id')

    
    if form.is_valid():
        if form.cleaned_data['department']:
            queryset = queryset.filter(department=form.cleaned_data['department'])
        if form.cleaned_data['category']:
            queryset = queryset.filter(category=form.cleaned_data['category'])
        if form.cleaned_data['subcategory']:
            queryset = queryset.filter(subcategory=form.cleaned_data['subcategory'])
        if form.cleaned_data['brand']:
            queryset = queryset.filter(brand=form.cleaned_data['brand'])


    status = request.GET.get('status')
    if status == 'True':
        queryset = queryset.filter(active=True)
    elif status == 'False':
        queryset = queryset.filter(active=False)
    

    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page')
    suppliers = paginator.get_page(page_number)

    context = {
        'form': form,
        'status_form': status_form,
        'suppliers': suppliers,  # Adicione a lista de fornecedores ao contexto
    }
    return render(request, 'suppliers/supplier_list.html', context)


def sua_view_para_o_formulário(request):
    departamentos = Departamento.objects.all()
    return render(request, 'seu_template.html', {'departamentos': departamentos})


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierCreateView(LoginRequiredMixin, SupplierFormMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')

    
    def form_invalid(self, form):
        # Retorna para o template com o formulário preenchido e os erros
        return self.render_to_response(self.get_context_data(form=form))

    
    def form_valid(self, form):
        supplier = form.save(commit=False)
        supplier.price_rating = self.request.POST.get('price_rating')
        supplier.reliability_rating = self.request.POST.get('reliability_rating')
        delivery_days = ','.join(self.request.POST.getlist('delivery_days[]'))
        supplier.delivery_days = delivery_days      
        supplier.user = self.request.user  # Associa o fornecedor ao usuário atual
        supplier.save()
        form.save_m2m()
        messages.success(self.request, 'Fornecedor salvo com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delivery_days_list'] = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        if self.object:
            context['selected_days'] = self.object.delivery_days.split(',') if self.object.delivery_days else []
        context['departamentos'] = Departamento.objects.all()
        context['selected_days'] = self.object.delivery_days.split(',') if self.object and self.object.delivery_days else []
        return context


    
    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial




@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SupplierFilterForm(self.request.GET or None)
     

        if form.is_valid():
            department_id = self.request.GET.get('department')
            category_id = self.request.GET.get('category')
            subcategory_id = self.request.GET.get('subcategory')
            brand_id = form.cleaned_data.get('brand')

            if department_id:
                queryset = queryset.filter(departments__id=department_id)
            if category_id:
                queryset = queryset.filter(categories__id=category_id)
            if subcategory_id:
                queryset = queryset.filter(subcategories__id=subcategory_id)
            if brand_id:
                queryset = queryset.filter(brand__id=brand_id)        

        status = self.request.GET.get('status')
        if status == 'True':
            queryset = queryset.filter(active=True)
        elif status == 'False':
            queryset = queryset.filter(active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = context['object_list']  # Adiciona 'suppliers' ao contexto
        context['departments'] = Departamento.objects.all()
        context['categories'] = Category.objects.all()
        context['subcategories'] = Subcategory.objects.all()
        context['form'] = SupplierFilterForm(self.request.GET or None)
        context['status_form'] = SupplierStatusFilterForm(self.request.GET or None)
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    

class RatingsUpdateView(LoginRequiredMixin, View):
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


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierUpdateView(LoginRequiredMixin, SupplierFormMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list') 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'save_ratings' in request.POST:
            ratings_form = SupplierRatingsForm(request.POST, instance=self.object)
            if ratings_form.is_valid():
                ratings_form.save()
                messages.success(request, "Avaliações atualizadas com sucesso.")
                return HttpResponseRedirect(self.get_success_url() + '?success=true')
            else:
                messages.error(request, "Erro ao salvar avaliações. Por favor, verifique os dados fornecidos.")
                return self.form_invalid(ratings_form)
        else:
            return super().post(request, *args, **kwargs)

    def handle_ratings(self, request):
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
        supplier = form.save(commit=False)
        delivery_days = self.request.POST.getlist('delivery_days[]')
        supplier.delivery_days = ','.join(delivery_days)
        supplier.user = self.request.user  # Associa o fornecedor ao usuário atual

        # Processar dados de avaliações somente se o formulário de avaliações for enviado
        if 'save_ratings' in self.request.POST:
            price_rating = self.request.POST.get('price_rating')
            reliability_rating = self.request.POST.get('reliability_rating')
            self.object.price_rating = price_rating
            self.object.reliability_rating = reliability_rating
        supplier.save()
        form.save_m2m()
        self.object.save()
        
        return super().form_valid(form)

    # def form_valid(self, form):
    #     supplier = form.save(commit=False)  # Salva o objeto Supplier 
    #     delivery_days = self.request.POST.getlist('delivery_days[]')
    #     if delivery_days:
    #         supplier.delivery_days = ','.join(delivery_days)
    #     supplier.save()                 # Salva o objeto Supplier com todos os dados atualizados
    #     form.save_m2m()                 # Salva as relações ManyToMany
    #     return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_days'] = self.object.delivery_days.split(',') if self.object.delivery_days else []
        return context
    
    def form_invalid(self, form):
        # Exibir mensagem de erro
        messages.error(self.request, 'Erro ao salvar o fornecedor. Por favor, verifique os dados fornecidos.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('suppliers:supplier_detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')

    def delete(self, request, *args, **kwargs):
        logging.debug("Tentando deletar o fornecedor com ID: %s", self.kwargs.get('pk'))
        return super().delete(request, *args, **kwargs) 

def create_supplier(request):
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST['email'], password=request.POST['senha'])
        supplier = Supplier(user=user)
        supplier.save()


def get_categories(request):
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
    

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = list(Subcategory.objects.filter(category_id=category_id).values('id', 'name'))
    return JsonResponse(subcategories, safe=False)

class TestCategoryView(TestCase):
    def test_get_categories(self):
        response = self.client.get(reverse('ajax_get_categories'), {'department_id': 1})
        self.assertEqual(response.status_code, 200)