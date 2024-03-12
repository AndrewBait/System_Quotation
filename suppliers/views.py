from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Supplier
from .forms import SupplierForm




# class SupplierListView(ListView):
#     model = Supplier
#     template_name = 'suppliers/supplier_list.html'

@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('supplier_list')  # Substitua 'supplier_list' pela URL que você deseja redirecionar após o cadastro
