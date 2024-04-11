from pyexpat.errors import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .models import Supplier
from .forms import SupplierForm, SupplierFilterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect, render
from .models import Departamento, Supplier
from .forms import SupplierStatusFilterForm
from .models import Category
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator


class SupplierFormMixin:
    def form_valid(self, form):
        self.object = form.save()
        form.save_m2m()
        messages.success(self.request, 'Fornecedor salvo com sucesso!')
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
    form = SupplierFilterForm(request.GET)
    status_form = SupplierStatusFilterForm(request.GET)
    queryset = Supplier.objects.all()

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
    if status != '' and status is not None:
        if status == 'True':
            suppliers = suppliers.filter(active=True)
        elif status == 'False':
            suppliers = suppliers.filter(active=False)
    

    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page')
    suppliers = paginator.get_page(page_number)

    context = {
        'form': form,
        'status_form': status_form,
        'fornecedores': suppliers,
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

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial

    def form_invalid(self, form):
        # Retorna para o template com o formulário preenchido e os erros
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delivery_days_list'] = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        context['departamentos'] = Departamento.objects.all()
        context['selected_days'] = self.object.delivery_days.split(',') if self.object and self.object.delivery_days else []
        return context

    def form_valid(self, form):
        supplier = form.save(commit=False) 
        delivery_days = ','.join(self.request.POST.getlist('delivery_days[]'))
        form.instance.delivery_days = delivery_days
        response = super().form_valid(form)
        supplier.user = self.request.user  # Associa o fornecedor ao usuário atual
        supplier.save()
        form.save_m2m()
        messages.success(self.request, 'Fornecedor salvo com sucesso!')
        return super().form_valid(form)



@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierListView(ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierUpdateView(LoginRequiredMixin, SupplierFormMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delivery_days_list'] = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        if self.kwargs.get('pk'):
            supplier = get_object_or_404(Supplier, pk=self.kwargs['pk'])
            context['selected_days'] = supplier.delivery_days.split(',') if supplier.delivery_days else []
        return context

    def form_valid(self, form):
        supplier = form.save(commit=False)  # Salva o objeto Supplier
        form.instance.delivery_days = ','.join(self.request.POST.getlist('delivery_days[]'))
        supplier.save()                 # Salva o objeto Supplier
        form.save_m2m()        # Salva as relações ManyToMany
        return super().form_valid(form)


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list') 

def create_supplier(request):
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST['email'], password=request.POST['senha'])
        supplier = Supplier(user=user)
        supplier.save()


