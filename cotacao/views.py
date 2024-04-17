from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from products.models import Product
from products.models import Departamento, Category, Subcategory


class ProdutoAPI(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        departamento_id = request.GET.get('departamento_id')
        categoria_id = request.GET.get('categoria_id')
        subcategoria_id = request.GET.get('subcategoria_id')

        produtos = Product.objects.all()
        if q:
            produtos = produtos.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(ean__icontains=q))
        if departamento_id:
            produtos = produtos.filter(departamento_id=departamento_id)
        if categoria_id:
            produtos = produtos.filter(categoria_id=categoria_id)
        if subcategoria_id:
            produtos = produtos.filter(subcategoria_id=subcategoria_id)

        data = [{'id': p.id, 'nome': p.name, 'sku': p.sku, 'ean': p.ean} for p in produtos]
        return JsonResponse(data, safe=False)


class DepartamentoAPI(View):
    def get(self, request, *args, **kwargs):
        departamentos = Departamento.objects.all().values('id', 'name')
        return JsonResponse(list(departamentos), safe=False)
    
class CategoriaAPI(View):
    def get(self, request, *args, **kwargs):
        categorias = Category.objects.all().values('id', 'name')
        return JsonResponse(list(categorias), safe=False)
    
class SubcategoriaAPI(View):
    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')
        subcategorias = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategorias), safe=False)