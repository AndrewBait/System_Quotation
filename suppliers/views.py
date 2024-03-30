from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Supplier
from .forms import SupplierForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User


class SupplierCreateView(UserPassesTestMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = reverse_lazy('suppliers:supplier_list')
    template_name = 'suppliers/supplier_form.html'

    def test_func(self):
        return self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = User.objects.create_user(username=form.instance.email, email=form.instance.email, password='senha_inicial')
        form.instance.user = user
        form.instance.save()
        return super().form_valid(form)  



@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class SupplierListView(ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'



class SupplierUpdateView(UserPassesTestMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list') 

    def test_func(self):
        return self.request.user.is_superuser



class SupplierDeleteView(UserPassesTestMixin, DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list') 

    def test_func(self):
        return self.request.user.is_superuser
