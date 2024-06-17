from datetime import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url='accounts:login')
def home_view(request):
    return render(request, 'home.html')


@login_required(login_url='accounts:login')
def register_view(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            login(request, new_user) 
            return redirect('home')
    else:
        user_form = UserCreationForm()
    return render(request, 'register.html', {'user_form': user_form})


def login_view(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        login_form = AuthenticationForm()

    return render(request, 'login.html', {'login_form': login_form})



def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# accounts/views.py

from django.shortcuts import render
from django.db.models import Count, Avg, Q
from django.utils import timezone
from products.models import Product, Category, Brand, ProductPriceHistory
from suppliers.models import Supplier
from cotacao.models import Cotacao, ItemCotacao
from respostas.models import RespostaCotacao

def home_view(request):
    # Dados gerais
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_cotacoes = Cotacao.objects.count()
    
    # Média de preços dos produtos
    average_product_price = Product.objects.aggregate(Avg('preco_de_custo'))['preco_de_custo__avg']
    
    # Produtos por categoria
    products_by_category = Category.objects.annotate(num_products=Count('products')).order_by('-num_products')
    
    # Fornecedores por departamento
    suppliers_by_department = Supplier.objects.values('departments__nome').annotate(num_suppliers=Count('id')).order_by('-num_suppliers')
    
    # Cotações por status
    cotacoes_by_status = Cotacao.objects.values('status').annotate(num_cotacoes=Count('id')).order_by('status')

    # Cotações em aberto, respondidas e não respondidas
    cotacoes_abertas = Cotacao.objects.filter(status='ativo').count()
    cotacoes_respondidas = Cotacao.objects.filter(itens_cotacao__isnull=False).distinct().count()
    cotacoes_nao_respondidas = Cotacao.objects.filter(itens_cotacao__isnull=True).distinct().count()

    # Fornecedores perto do prazo de pedidos
    suppliers_near_deadline = Supplier.objects.filter(
        Q(order_response_deadline__lte=timezone.now() + timezone.timedelta(days=3))
    ).count()

    # Histórico de preços dos produtos (agrupados por mês)
    price_history = ProductPriceHistory.objects.extra(select={'month': "strftime('%%Y-%%m', date)"}).values('month').annotate(avg_price=Avg('price')).order_by('month')

    # Cotações por mês (limitar a 12 meses)
    cotacoes_por_mes = Cotacao.objects.extra(select={'month': "strftime('%%Y-%%m', data_abertura)"}).values('month').annotate(total=Count('id')).order_by('-month')[:12]

    # Desempenho dos fornecedores
    suppliers_performance = Supplier.objects.aggregate(
        avg_quality_rating=Avg('quality_rating'),
        avg_delivery_time_rating=Avg('delivery_time_rating'),
        avg_price_rating=Avg('price_rating'),
        avg_reliability_rating=Avg('reliability_rating'),
        avg_flexibility_rating=Avg('flexibility_rating'),
        avg_partnership_rating=Avg('partnership_rating'),
    )
    



    context = {
        'total_products': total_products,
        'total_suppliers': total_suppliers,
        'total_cotacoes': total_cotacoes,
        'average_product_price': average_product_price,
        'products_by_category': products_by_category,
        'suppliers_by_department': suppliers_by_department,
        'cotacoes_by_status': cotacoes_by_status,
        'cotacoes_abertas': cotacoes_abertas,
        'cotacoes_respondidas': cotacoes_respondidas,
        'cotacoes_nao_respondidas': cotacoes_nao_respondidas,
        'suppliers_near_deadline': suppliers_near_deadline,
        'price_history': price_history,
        'cotacoes_por_mes': cotacoes_por_mes,
        'suppliers_performance': suppliers_performance,
    }
    
    return render(request, 'home.html', context)

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification  # Assumindo que você tem um modelo de Notificação


def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.filter(id=notification_id, user=request.user).first()
    if notification:
        notification.read = True
        notification.save()
    return JsonResponse({'success': True})