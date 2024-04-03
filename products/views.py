from products.models import Product
from products.forms import ProductModelForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from .models import Brand, Product
import csv
import xml.etree.ElementTree as ET
from .forms import ProductImportForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers
from dal import autocomplete
from django.db.models import Q
from .models import Category, Subcategory
from cotacao.models import Departamento


class BrandCreateView(CreateView):
    model = Brand
    fields = ['name']
    template_name = 'brands/brand_form.html'
    success_url = reverse_lazy('products:new_product')


class ProductListView(ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object_list = self.get_queryset()
            products_json = serializers.serialize('json', self.object_list)
            return JsonResponse(products_json, safe=False)
        else:
            return super().get(request, *args, **kwargs)

    # def get_queryset(self):
    #     products = super().get_queryset().order_by('name')
    #     search = self.request.GET.get('search')
    #     if search:
    #         products = products.filter(name__icontains=search)
    #     return products
    

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    

@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class NewProductCreateView(CreateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'new_product.html'
    success_url = '/products/'


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class ProductUpdatView(UpdateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'product_update.html'

    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_delete.html'
    success_url = '/products/'


@login_required
def import_products(request):
    if request.method == 'POST':
        form = ProductImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                if str(file).endswith('.csv'):
                    handle_csv_upload(file)
                elif str(file).endswith('.xml'):
                    handle_xml_upload(file)
                messages.success(request, 'Produtos importados com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao importar produtos: {e}')
            return redirect('products:products_list')
    else:
        form = ProductImportForm()
    return render(request, 'import_products.html', {'form': form})


def handle_csv_upload(f):
    reader = csv.DictReader(f.decode('utf-8').splitlines())
    for row in reader:
        # Validação dos campos obrigatórios
        if not row.get('codigoEAN') or not row.get('nomeDoProduto'):
            continue  # Pula para a próxima linha se os campos obrigatórios não estiverem presentes

        # Tratamento da marca (opcional)
        brand = None
        if row.get('marca'):
            brand, _ = Brand.objects.get_or_create(name=row['marca'])

        # Criação do produto
        Product.objects.create(
            ean=row['codigoEAN'],
            name=row['nomeDoProduto'],
            brand=brand,
            photo=row.get('foto')  # Assume que 'foto' é um URL ou caminho válido para a imagem
        )

def handle_xml_upload(f):
    tree = ET.parse(f)
    root = tree.getroot()
    for elem in root.findall('product'):
        # Validação dos campos obrigatórios
        codigoEAN = elem.find('codigoEAN').text if elem.find('codigoEAN') is not None else None
        nomeDoProduto = elem.find('nomeDoProduto').text if elem.find('nomeDoProduto') is not None else None
        if not codigoEAN or not nomeDoProduto:
            continue  # Pula para o próximo elemento se os campos obrigatórios não estiverem presentes

        # Tratamento da marca (opcional)
        brand = None
        if elem.find('marca') is not None:
            brand_name = elem.find('marca').text
            brand, _ = Brand.objects.get_or_create(name=brand_name)

        # Criação do produto
        Product.objects.create(
            ean=codigoEAN,
            name=nomeDoProduto,
            brand=brand,
            photo=elem.find('foto').text if elem.find('foto') is not None else None  # Assume que 'foto' é um URL ou caminho válido para a imagem
        )


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        department_id = self.forwarded.get('department', None)
        if department_id:
            return Category.objects.filter(department_id=department_id)
        else:
            return Category.objects.none()


class SubcategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        category_id = self.forwarded.get('category', None)
        qs = Subcategory.objects.all()

        if category_id:
            qs = qs.filter(category_id=category_id)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs