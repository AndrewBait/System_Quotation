from products.models import Product
from products.forms import ProductModelForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView


class ProductListView(ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'

    def get_queryset(self):
        products = super().get_queryset().order_by('name')
        search = self.request.GET.get('search')
        if search:
            products = products.filter(name__icontains=search)
        return products
    

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    

@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class NewProductCreateView(CreateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'new_product.html'
    success_url = '/products_list/'


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class ProductUpdatView(UpdateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'product_update.html'

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_delete.html'
    success_url = '/products/'