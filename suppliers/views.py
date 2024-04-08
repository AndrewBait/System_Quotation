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
class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')

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
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list') 


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
