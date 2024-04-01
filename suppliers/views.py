from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .models import Supplier
from .forms import SupplierForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect


@method_decorator(login_required(login_url='login'), name='dispatch')
class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')

    def form_valid(self, form):
        # Crie primeiro o usuário
        user = User.objects.create(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            password=make_password('resposta')  # Use uma senha segura
        )
        # Agora, salve o fornecedor com esse usuário
        supplier = form.save(commit=False)
        supplier.user = user
        supplier.save()
        return redirect('suppliers:supplier_list')  # Substitua pela sua URL de sucesso

@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class SupplierListView(ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list') 


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list') 


def create_supplier(request):
    if request.method == 'POST':
        # Crie o usuário baseado nos dados recebidos
        user = User.objects.create_user(username=request.POST['email'], password=request.POST['senha'])
        # Crie o fornecedor e associe ao usuário
        supplier = Supplier(user=user)
        supplier.save()
        # Redirecione ou retorne uma resposta adequada