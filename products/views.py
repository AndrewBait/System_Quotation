from pyexpat.errors import messages
from django.urls import reverse, reverse_lazy
from django.http import Http404 
from products.models import Product
from products.forms import ProductModelForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import Brand, Product, Departamento, Category, Subcategory, ProductLine
import csv
import xml.etree.ElementTree as ET
from .forms import ProductImportForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core import serializers
from dal import autocomplete
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q
import re
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse 

@method_decorator(login_required(login_url=''), name='dispatch')
@permission_required('products.view_product', raise_exception=True)
def products_list(request):
    products = Product.objects.all()  # Inicialmente, obtém todos os produtos
    
    search_query = request.GET.get('search_query', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(ean__icontains=search_query)
        )
    
    return render(request, 'products.html', {
        'products': products,
        'search_query': search_query
    })

# Para download do modelo CSV
@permission_required('products.view_product', raise_exception=True)
def download_csv_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="template.csv"'
    response.write(u'\ufeff'.encode('utf8'))  # BOM (Byte Order Mark) para indicar UTF-8
    csv_template = (
        "ean,sku,name\n"  # Cabeçalho CSV com os campos mencionados
        "1234567890123,SKU123,Exemplo de produto 1\n"  # Exemplo de linha de dados
        "9876543210987,SKU456,Exemplo de produto 2\n"  # Outro exemplo de linha de dados
    )
    response.write(csv_template)
    return response

# Para download do modelo XML
@permission_required('products.view_product', raise_exception=True)
def download_xml_template(request):
    response = HttpResponse(content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="template.xml"'
    xml_template = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<products>\n"
        "    <product>\n"
        "        <ean>1234567890123</ean>\n"
        "        <sku>SKU123</sku>\n"
        "        <name>Exemplo de produto 1</name>\n"
        "    </product>\n"
        "    <product>\n"
        "        <ean>9876543210987</ean>\n"
        "        <sku>SKU456</sku>\n"
        "        <name>Exemplo de produto 2</name>\n"
        "    </product>\n"
        "</products>\n"
    )
    response.write(xml_template)
    return response

@permission_required('products.view_brand', raise_exception=True)
def list_brands(request):
    brands = list(Brand.objects.all().values('id', 'name'))
    return JsonResponse(brands, safe=False)

@require_http_methods(["POST"])
@permission_required('products.add_brand', raise_exception=True)
def add_brand(request):
    brand_name = request.POST.get('name')
    if not brand_name:
        return JsonResponse({'error': 'O nome da marca é obrigatório'}, status=400)
    
    brand, created = Brand.objects.get_or_create(name=brand_name)
    return JsonResponse({'id': brand.id, 'name': brand.name}, status=201 if created else 200)

@permission_required('products.view_brand', raise_exception=True)
def brand_autocomplete(request):
    qs = Brand.objects.all()

    if request.GET.get('term'):
        qs = qs.filter(name__istartswith=request.GET.get('term'))

    brands = list(qs.values('id', 'name'))
    return JsonResponse(brands, safe=False)

class BrandCreateView(PermissionRequiredMixin, CreateView):
    model = Brand
    fields = ['name']
    template_name = 'brands/brand_form.html'
    success_url = reverse_lazy('products:new_product')
    permission_required = 'products.add_brand'

class BrandAutocomplete(PermissionRequiredMixin, autocomplete.Select2QuerySetView):
    permission_required = 'products.view_brand'

    def get_queryset(self):
        qs = Brand.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs[:10]

def validate_query(query):
    # Remova caracteres indesejados ou limite a caracteres alfanuméricos e espaço
    query = re.sub(r'[^a-zA-Z0-9 ]', '', query)
    return query

@method_decorator(login_required(login_url=''), name='dispatch')
class ProductListView(PermissionRequiredMixin, ListView):
    model = Product
    template_name = 'products.html'
    context_object_name = 'products'
    paginate_by = 10
    permission_required = 'products.view_product'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        search_query = self.request.GET.get('search_query', '').strip()
        query = self.request.GET.get('query', '')
        product_name = self.request.GET.get('product_name', '')
        department_id = self.request.GET.get('department', '')
        category_id = self.request.GET.get('category', '')
        subcategory_id = self.request.GET.get('subcategory', '')
        brand_id = self.request.GET.get('brand', '')  # Adicione esta linha
        product_line_id = self.request.GET.get('product_line', '')  # E esta linha
        status = self.request.GET.get('status', '')
        search_query = validate_query(search_query)
        search_query = ' '.join(search_query.split())

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(sku__icontains=search_query) | 
                Q(ean__icontains=search_query)
            )

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(sku__icontains=query) | Q(ean__icontains=query)
            )
        if product_name:
            queryset = queryset.filter(name__icontains=product_name)
        if department_id:
            queryset = queryset.filter(department__id=department_id)
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategory__id=subcategory_id)
        if brand_id:  # Adicione esta condição
            queryset = queryset.filter(brand__id=brand_id)
        if product_line_id:  # E esta condição
            queryset = queryset.filter(product_line__id=product_line_id)
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
        # Remove a primeira chamada de super().get_context_data(**kwargs)
        department_id = self.request.GET.get('department')
        category_id = self.request.GET.get('category')
        context = super().get_context_data(**kwargs)  # Mantém essa chamada
        context['departments'] = Departamento.objects.all()
        context['categories'] = Category.objects.filter(department_id=department_id) if department_id else Category.objects.none()
        context['subcategories'] = Subcategory.objects.filter(category_id=category_id) if category_id else Subcategory.objects.none()
        context['current_department'] = department_id
        context['current_category'] = category_id
        context['current_subcategory'] = self.request.GET.get('subcategory', '')
        context['brands'] = Brand.objects.all()
        context['product_lines'] = ProductLine.objects.all()

        items_per_page = self.request.GET.get('items_per_page', 10)  
        self.paginate_by = int(items_per_page)
        context['current_items_per_page'] = items_per_page
        return context

@method_decorator(login_required(login_url=''), name='dispatch')
class ProductDetailView(PermissionRequiredMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    permission_required = 'products.view_product'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            messages.error(self.request, 'Produto não encontrado ou já excluído.')
            return redirect('products:products_list')

@method_decorator(login_required(login_url=''), name='dispatch')
class NewProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'new_product.html'
    success_url = reverse_lazy('products:new_product')
    permission_required = 'products.add_product'

    def form_valid(self, form):
        new_brand_name = self.request.POST.get('new_brand')
        if new_brand_name:
            brand, created = Brand.objects.get_or_create(name=new_brand_name.strip())
            form.instance.brand = brand
        response = super(NewProductCreateView, self).form_valid(form)
        messages.success(self.request, 'Produto cadastrado com sucesso!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao cadastrar o produto. Por favor, verifique os campos e tente novamente.')
        return super().form_invalid(form)

@method_decorator(login_required(login_url=''), name='dispatch')
class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductModelForm
    template_name = 'product_update.html'
    permission_required = 'products.change_product'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            messages.error(self.request, 'Produto não encontrado ou já excluído.')
            return redirect('products:products_list')

    def form_valid(self, form):
        new_brand_name = self.request.POST.get('new_brand')
        if new_brand_name:
            brand, created = Brand.objects.get_or_create(name=new_brand_name.strip())
            form.instance.brand = brand
        response = super(ProductUpdateView, self).form_valid(form)
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar o produto. Por favor, verifique os campos e tente novamente.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('products:product_update', kwargs={'pk': self.object.pk})

@method_decorator(login_required(login_url=''), name='dispatch')
class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_delete.html'
    success_url = reverse_lazy('products:products_list')
    permission_required = 'products.delete_product'

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Http404:
            messages.error(request, 'Produto não encontrado ou já excluído.')
            return redirect(self.success_url)

@method_decorator(login_required(login_url=''), name='dispatch')
@permission_required('products.add_product', raise_exception=True)
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
            except Exception as e:
                messages.error(request, f'Erro ao importar produtos: {e}')
            return redirect('products:products_list')
    else:
        form = ProductImportForm()
    return render(request, 'import_products.html', {'form': form})

@permission_required('products.add_product', raise_exception=True)
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

@permission_required('products.add_product', raise_exception=True)
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

@permission_required('products.view_category', raise_exception=True)
def get_categories(request):
    department_id = request.GET.get('department_id')
    categories = Category.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse(list(categories), safe=False)

@permission_required('products.view_subcategory', raise_exception=True)
def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)

class CategoryAutocomplete(PermissionRequiredMixin, autocomplete.Select2QuerySetView):
    permission_required = 'products.view_category'

    def get_queryset(self):
        department_id = self.forwarded.get('department', None)
        if department_id:
            queryset = Category.objects.filter(department__id=department_id)
        else:
            queryset = Category.objects.none()
        if self.q:
            queryset = queryset.filter(name__icontains=self.q)
        return queryset

class SubcategoryAutocomplete(PermissionRequiredMixin, autocomplete.Select2QuerySetView):
    permission_required = 'products.view_subcategory'

    def get_queryset(self):
        category_id = self.forwarded.get('category', None)
        if category_id:
            queryset = Subcategory.objects.filter(category__id=category_id)
        else:
            queryset = Subcategory.objects.none()
        if self.q:
            queryset = queryset.filter(name__istartswith=self.q)
        return queryset
