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
from django.shortcuts import redirect, render
from .models import Departamento, Supplier
from .forms import SupplierStatusFilterForm
from .models import Category
from django.http import JsonResponse
from django.contrib import messages

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
    queryset = Supplier.objects.all()

    if request.GET.get('active') != '' and request.GET.get('active') is not None:
        queryset = queryset.filter(active=request.GET.get('active'))

    if request.GET.get('department'):
        queryset = queryset.filter(department=request.GET.get('department'))

    if request.GET.get('category'):
        queryset = queryset.filter(category=request.GET.get('category'))

    if request.GET.get('brand'):
        queryset = queryset.filter(brand=request.GET.get('brand'))

    context = {
        'form': form,
        'object_list': queryset,
    }
    return render(request, 'your_template.html', context)


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
        context['departamentos'] = Departamento.objects.all()
        return context

    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        if not user:
            # Criação do usuário, se necessário
            user = User.objects.create_user(username=form.cleaned_data['email'],
                                            email=form.cleaned_data['email'],
                                            password=form.cleaned_data['resposta']) # Ajuste conforme sua lógica
        supplier = form.save(commit=False)
        supplier.user = user
        supplier.save()
        form.save_m2m()  # Não esqueça de salvar ManyToMany fields se houver
        return redirect(self.get_success_url())



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

    def form_valid(self, form):
        supplier = form.save(commit=False)  # Salva o objeto Supplier
        supplier.save()                 # Salva o objeto Supplier
        form.save_m2m()        # Salva as relações ManyToMany
        return redirect(self.get_success_url())


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


def supplier_list(request):
    form = SupplierStatusFilterForm(request.GET)
    suppliers = Supplier.objects.all()

    status = request.GET.get('status')
    if status != '' and status is not None:
        if status == 'True':
            suppliers = suppliers.filter(active=True)
        elif status == 'False':
            suppliers = suppliers.filter(active=False)

    return render(request, 'your_template_name.html', {
        'object_list': suppliers,
        'form': form,
    })