from products.models import Product
from products.forms import ProductModelForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from .models import Brand, Product, Departamento, Category, Subcategory
import csv
import xml.etree.ElementTree as ET
from .forms import ProductImportForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core import serializers
from dal import autocomplete
from .models import Category, Subcategory
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Brand
from django.core.paginator import Paginator



def list_brands(request):
    brands = list(Brand.objects.all().values('id', 'name'))
    return JsonResponse(brands, safe=False)



@require_http_methods(["POST"])
def add_brand(request):
    brand_name = request.POST.get('name')
    if not brand_name:
        return JsonResponse({'error': 'O nome da marca é obrigatório'}, status=400)
    
    brand, created = Brand.objects.get_or_create(name=brand_name)
    return JsonResponse({'id': brand.id, 'name': brand.name}, status=201 if created else 200)


def brand_autocomplete(request):
    qs = Brand.objects.all()

    if request.GET.get('term'):
        qs = qs.filter(name__istartswith=request.GET.get('term'))

    brands = list(qs.values('id', 'name'))
    return JsonResponse(brands, safe=False)


class BrandCreateView(CreateView):
    model = Brand
    fields = ['name']
    template_name = 'brands/brand_form.html'
    success_url = reverse_lazy('products:new_product')


class BrandAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Brand.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:10]


class ProductListView(ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        queryset = super().get_queryset().order_by('name')
        product_name = self.request.GET.get('product_name', '')
        department_id = self.request.GET.get('department', '')
        category_id = self.request.GET.get('category', '')
        subcategory_id = self.request.GET.get('subcategory', '')
        status = self.request.GET.get('status', '')

        if product_name:
            queryset = queryset.filter(name__icontains=product_name)
        if department_id:
            queryset = queryset.filter(department__id=department_id)
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategory__id=subcategory_id)
        if status:
            queryset = queryset.filter(status=(status.lower() == 'true'))

        return queryset

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object_list = self.get_queryset()
            products_json = serializers.serialize('json', self.object_list)
            return JsonResponse(products_json, safe=False)
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(ProductListView, self).get_context_data(**kwargs)
        department_id = self.request.GET.get('department')
        category_id = self.request.GET.get('category')
        context['departments'] = Departamento.objects.all()
        context['categories'] = Category.objects.filter(department_id=department_id) if department_id else Category.objects.none()
        context['subcategories'] = Subcategory.objects.filter(category_id=category_id) if category_id else Subcategory.objects.none() # Se necessário, ajuste para filtrar com base na categoria selecionada
        # Mantém os filtros atuais para serem selecionados após a recarga da página
        context['current_department'] = department_id
        context['current_category'] = category_id
        context['current_subcategory'] = self.request.GET.get('subcategory', '')
        return context

    

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    

@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class NewProductCreateView(CreateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'new_product.html'
    success_url = reverse_lazy('products:products_list')

    def form_valid(self, form):
        new_brand_name = self.request.POST.get('new_brand')
        if new_brand_name:
            brand, created = Brand.objects.get_or_create(name=new_brand_name.strip())
            form.instance.brand = brand
        return super(NewProductCreateView, self).form_valid(form) 
    

@method_decorator(login_required(login_url='login'), name='dispatch')#decorator
class ProductUpdatView(UpdateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'product_update.html'

    def form_valid(self, form):
        new_brand_name = self.request.POST.get('new_brand')
        if new_brand_name:
            brand, created = Brand.objects.get_or_create(name=new_brand_name.strip())
            form.instance.brand = brand
        return super(ProductUpdatView, self).form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        if self.object.department:
            initial['department'] = self.object.department.id
        if self.object.category:
            initial['category'] = self.object.category.id
        if self.object.subcategory:
            initial['subcategory'] = self.object.subcategory.id
        return initial

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


def get_categories(request):
    department_id = request.GET.get('department_id')
    categories = Category.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse(list(categories), safe=False)


def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        department_id = self.forwarded.get('department', None)
        if department_id:
            queryset = Category.objects.filter(department__id=department_id)
        else:
            queryset = Category.objects.none()
        if self.q:
            queryset = queryset.filter(name__istartswith=self.q)
        return queryset

class SubcategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        category_id = self.forwarded.get('category', None)
        if category_id:
            queryset = Subcategory.objects.filter(category__id=category_id)
        else:
            queryset = Subcategory.objects.none()
        if self.q:
            queryset = queryset.filter(name__istartswith=self.q)
        return queryset