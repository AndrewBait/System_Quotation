import hashlib
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from products.models import Product
from .forms import RespostaCotacaoForm, ItemRespostaForm
from cotacao.models import Cotacao, FornecedorCotacaoToken, ItemCotacao
from suppliers.models import Supplier
from .models import Pedido, RespostaCotacao, ItemRespostaCotacao
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from decimal import Decimal
from datetime import date
import logging
from decimal import Decimal, InvalidOperation
import logging
from django.db import transaction
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import Pedido, PedidoAgrupado
from collections import defaultdict
from django.utils import timezone
import datetime
from django.db.models import Q
from .forms import PedidoFormSet
from cotacao.models import Cotacao 
from products.models import ProductPriceHistory
import re

from respostas import models



def apenas_digitos(cnpj):
    return re.sub(r'\D', '', cnpj)  # Remove tudo que não é dígito

def criar_item_form(item, resposta_existente, post_data=None, file_data=None):
    item_resposta, created = ItemRespostaCotacao.objects.get_or_create(
        resposta_cotacao=resposta_existente, 
        item_cotacao=item,
        defaults={'item_cotacao': item}  # O 'defaults' é utilizado apenas se estiver criando um novo registro
    )
    form_kwargs = {'instance': item_resposta, 'item_cotacao': item}
    if post_data and file_data:
        return ItemRespostaForm(post_data, file_data, prefix=f'item_{item.pk}', **form_kwargs)
    else:
        return ItemRespostaForm(prefix=f'item_{item.pk}', **form_kwargs)

def responder_cotacao(request, cotacao_uuid, fornecedor_id, token):
    cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
    fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)
    token_obj = get_object_or_404(FornecedorCotacaoToken, cotacao=cotacao, fornecedor=fornecedor, token=token)
    
    if cotacao.status == 'inativo':
        return render(request, 'respostas/cotacao_fechada.html', {'message': 'Esta cotação está fechada no momento.'})

    auth_param = request.GET.get('auth')
    if auth_param:
        # Gerar hash do CNPJ truncado
        cnpj_limpo = apenas_digitos(fornecedor.cnpj)
        cnpj_slice = cnpj_limpo[:4]
        hash_object = hashlib.sha256(cnpj_slice.encode())
        cnpj_hash = hash_object.hexdigest()
        
        if auth_param != cnpj_hash:
            return render(request, 'respostas/authenticate.html', {
                'error_message': 'Código de autenticação inválido.',
                'cotacao_uuid': cotacao_uuid,
                'fornecedor_id': fornecedor_id,
                'token': token
            })

    if 'authenticated' not in request.session or request.session['authenticated'] != fornecedor_id:
        if request.method == 'POST' and 'auth_code' in request.POST:
            auth_code = request.POST['auth_code']
            cnpj_limpo = apenas_digitos(fornecedor.cnpj)
            if auth_code == cnpj_limpo[:4]:
                request.session['authenticated'] = fornecedor_id
                return redirect(request.path)
            else:
                return render(request, 'respostas/authenticate.html', {
                    'error_message': 'Código de autenticação inválido.',
                    'cotacao_uuid': cotacao_uuid,
                    'fornecedor_id': fornecedor_id,
                    'token': token
                })
        else:
            return render(request, 'respostas/authenticate.html', {
                'cotacao_uuid': cotacao_uuid,
                'fornecedor_id': fornecedor_id,
                'token': token
            })

    resposta_existente, created = RespostaCotacao.objects.get_or_create(cotacao=cotacao, fornecedor=fornecedor)
    resposta_form = RespostaCotacaoForm(request.POST, request.FILES or None, instance=resposta_existente)
    item_forms = [criar_item_form(item, resposta_existente, request.POST, request.FILES or None) for item in cotacao.itens_cotacao.all()]

    if request.method == 'POST':
        if resposta_form.is_valid() and all(item_form.is_valid() for item_form in item_forms):
            resposta = resposta_form.save(commit=False)
            resposta.cotacao = cotacao
            resposta.fornecedor = fornecedor
            resposta.save()
            for item_form in item_forms:
                item_resposta = item_form.save(commit=False)
                item_resposta.resposta_cotacao = resposta
                item_resposta.save()
            return redirect('respostas:cotacao_respondida')

    context = {
        'form': {'resposta_form': resposta_form, 'item_forms': item_forms},
        'cotacao': cotacao,
        'fornecedor': fornecedor,
        'token': token_obj
    }
    return render(request, 'respostas/responder_cotacao.html', context)


def cotacao_respondida_view(request):
    return render(request, 'respostas/cotacao_respondida.html')


def visualizar_cotacoes(request, cotacao_uuid):
    cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
    itens_data = []   
    
        
    for item in cotacao.itens_cotacao.all():
        respostas = item.itemrespostacotacao_set.all().select_related('resposta_cotacao__fornecedor').order_by('preco')
        respostas_data = [{
            'preco': resposta.preco,
            'fornecedor_nome': resposta.resposta_cotacao.fornecedor.name,
            'fornecedor_id': resposta.resposta_cotacao.fornecedor.pk,
            'observacao': resposta.observacao,
            'imagem_url': resposta.imagem.url if resposta.imagem else None,
            'is_top3': idx < 3  
        } for idx, resposta in enumerate(respostas)]

        item_data = {
            'id': item.pk,
            'produto_nome': item.produto.name,
            'quantidade': item.quantidade,
            'tipo_volume': item.get_tipo_volume_display(),
            'respostas': respostas_data
        }
        itens_data.append(item_data)

    return render(request, 'respostas/visualizar_respostas.html', {'cotacao': cotacao, 'itens_data': itens_data})


def gerar_pedidos(request):
    cotacao_uuid = request.POST.get('cotacao_uuid', '')
    cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
    usuario = request.user  # Assumindo que você está usando a autenticação padrão do Django

    if request.method == 'POST':
        has_errors = False
        pedido_agrupado_dict = {}

        try:
            with transaction.atomic():
                selecao_keys = [key for key in request.POST if key.startswith('selecao_')]
                for key in selecao_keys:
                    item_id = int(key.split('_', 1)[1])
                    fornecedor_id, preco = request.POST[key].split('_')
                    fornecedor_id = int(fornecedor_id.strip())
                    preco_decimal = Decimal(preco.replace(',', '.').strip())

                    item_cotacao = ItemCotacao.objects.get(pk=item_id)
                    fornecedor = Supplier.objects.get(pk=fornecedor_id)

                    if fornecedor not in pedido_agrupado_dict:
                        pedido_agrupado = PedidoAgrupado.objects.create(
                            fornecedor=fornecedor,
                            cotacao=cotacao,
                            data_requisicao=date.today(),
                            status='pendente',
                            usuario_criador=usuario
                        )
                        pedido_agrupado_dict[fornecedor] = pedido_agrupado
                    else:
                        pedido_agrupado = pedido_agrupado_dict[fornecedor]

                    Pedido.objects.create(
                        produto=item_cotacao.produto,
                        quantidade=item_cotacao.quantidade,
                        tipo_volume=item_cotacao.tipo_volume,
                        preco=preco_decimal,
                        pedido_agrupado=pedido_agrupado
                    )
        except Exception as e:
            messages.error(request, f'Erro geral ao gerar pedidos: {str(e)}')
            has_errors = True

        if not has_errors:
            messages.success(request, 'Pedidos gerados com sucesso!')

    return redirect(reverse('respostas:visualizar_cotacoes', args=[cotacao_uuid]))


class ListarPedidosView(ListView):
    model = PedidoAgrupado
    template_name = 'respostas/listar_pedidos.html'
    context_object_name = 'pedidos_agrupados'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if query:
            queryset = queryset.filter(
                Q(cotacao__nome__icontains=query) |
                Q(fornecedor__name__icontains=query) |
                Q(fornecedor__company__name__icontains=query)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        if start_date and end_date:
            start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
            queryset = queryset.filter(data_requisicao__range=(start_date, end_date))

        return queryset  
    
    

class EditarPedidoView(UpdateView):
    model = Pedido
    fields = ['quantidade', 'preco', 'produto']  # ajuste os campos conforme necessário
    template_name = 'respostas/editar_pedido.html'
    success_url = reverse_lazy('respostas:listar_pedidos')


class DetalhesPedidoAgrupadoView(DetailView):
    model = PedidoAgrupado
    template_name = 'respostas/detalhes_pedido.html'
    context_object_name = 'pedido_agrupado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        PedidoFormSet = inlineformset_factory(PedidoAgrupado, Pedido, fields=('quantidade', 'preco'), extra=0)
        if self.request.method == 'POST':
            context['formset'] = PedidoFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = PedidoFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            formset.save()
            return redirect('respostas:listar_pedidos')
        else:
            return self.render_to_response(self.get_context_data(form=formset))
    

logger = logging.getLogger(__name__)

class EditarPedidoAgrupadoView(UpdateView):
    model = PedidoAgrupado
    fields = []
    template_name = 'respostas/editar_pedido.html'

    def get_context_data(self, **kwargs):
        logger.debug('Entrando em get_context_data')
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PedidoFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = PedidoFormSet(instance=self.object)
        logger.debug('Contexto preparado: %s', context)
        return context

    def form_valid(self, form):
        logger.debug('Formulário principal válido')
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            logger.debug('Formset válido')
            formset.save()
            logger.debug('Formset salvo com sucesso')
            return redirect('respostas:listar_pedidos')
        else:
            logger.debug('Formset inválido: %s', formset.errors)
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        logger.debug('Formulário principal inválido')
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    
logger = logging.getLogger(__name__)

class DeletarPedidoAgrupadoView(DeleteView):
    model = PedidoAgrupado
    template_name = 'respostas/deletar_pedido_agrupado.html'
    success_url = reverse_lazy('respostas:listar_pedidos')

    def get_object(self):
        pk = self.kwargs.get('pk')
        logger.debug(f"Tentando deletar PedidoAgrupado com pk={pk}")
        return get_object_or_404(PedidoAgrupado, pk=pk)
    
class DeletarPedidoView(DeleteView):
    model = Pedido
    template_name = 'respostas/deletar_pedido.html'
    success_url = reverse_lazy('respostas:listar_pedidos')
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        logger.debug(f"Tentando deletar Pedido com pk={pk}")
        return get_object_or_404(Pedido, pk=pk)


    
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncMonth
from django.db.models import Min, Max
from collections import defaultdict
import json
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from products.models import Product, ProductPriceHistory
from suppliers.models import Supplier
from cotacao.models import Cotacao, ItemCotacao

def visualizar_cotacoes(request, cotacao_uuid):
    cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
    itens_data = []

    # Definimos o intervalo padrão de 3 meses
    default_interval_days = 90
    default_start_date = timezone.now() - timezone.timedelta(days=default_interval_days)

    for item in cotacao.itens_cotacao.all():
        respostas = item.itemrespostacotacao_set.all().select_related('resposta_cotacao__fornecedor').order_by('preco')
        respostas_data = [{
            'preco': round(resposta.preco, 3) if resposta.preco is not None else None,
            'fornecedor_nome': resposta.resposta_cotacao.fornecedor.company if resposta.resposta_cotacao.fornecedor.company else resposta.resposta_cotacao.fornecedor.name,
            'fornecedor_id': resposta.resposta_cotacao.fornecedor.pk,
            'observacao': resposta.observacao,
            'imagem_url': resposta.imagem.url if resposta.imagem else None,
            'is_top3': idx < 3
        } for idx, resposta in enumerate(respostas)]

        produto = item.produto
        ultimo_preco = produto.price_history.order_by('-date').first()

        # Filtra os registros de histórico de preços para os últimos 3 meses por padrão
        price_history_records = produto.price_history.filter(date__gte=default_start_date).annotate(month=TruncMonth('date')).order_by('-date')

        price_history = defaultdict(lambda: {
            'min_price': float('inf'),
            'min_price_date': None,
            'min_supplier': None,
            'max_price': float('-inf'),
            'max_price_date': None,
            'max_supplier': None
        })

        for record in price_history_records:
            month = record.date.strftime('%Y-%m')
            if record.price < price_history[month]['min_price']:
                price_history[month]['min_price'] = record.price
                price_history[month]['min_price_date'] = record.date
                price_history[month]['min_supplier'] = record.supplier.company if record.supplier else None
            if record.price > price_history[month]['max_price']:
                price_history[month]['max_price'] = record.price
                price_history[month]['max_price_date'] = record.date
                price_history[month]['max_supplier'] = record.supplier.company if record.supplier else None

        # Converte o defaultdict para uma lista, ordenada pelo mês e limitando ao número de meses padrão
        price_history_list = sorted(price_history.items(), key=lambda x: x[0], reverse=True)
        price_history_formatted = [{
            'month': month,
            'min_price': round(data['min_price'], 3) if data['min_price'] != float('inf') else None,
            'min_price_date': data['min_price_date'].strftime('%d/%m/%Y') if data['min_price_date'] else None,
            'min_supplier': data['min_supplier'],
            'max_price': round(data['max_price'], 3) if data['max_price'] != float('-inf') else None,
            'max_price_date': data['max_price_date'].strftime('%d/%m/%Y') if data['max_price_date'] else None,
            'max_supplier': data['max_supplier']
        } for month, data in price_history_list[:default_interval_days//30]]

        item_data = {
            'id': item.pk,
            'produto_nome': produto.name,
            'quantidade': item.quantidade,
            'tipo_volume': item.get_tipo_volume_display(),
            'ultimo_preco': round(ultimo_preco.price, 3) if ultimo_preco and ultimo_preco.price is not None else None,
            'data_ultimo_preco': ultimo_preco.date if ultimo_preco else None,
            'price_history': price_history_formatted,
            'respostas': respostas_data
        }
        itens_data.append(item_data)

    return render(request, 'respostas/visualizar_respostas.html', {
        'cotacao': cotacao,
        'itens_data': itens_data,
        'prazo': cotacao.prazo  # Incluindo o prazo no contexto
    })




from django.http import JsonResponse
from django.utils import timezone
from django.db.models.functions import TruncMonth
from collections import defaultdict
from django.shortcuts import get_object_or_404
from cotacao.models import ItemCotacao

def get_price_history(request, item_id, days):
    print(f'Item ID: {item_id}, Days: {days}')  # Adicionar log para verificar a chamada
    item = get_object_or_404(ItemCotacao, pk=item_id)
    produto = item.produto
    interval = int(days)
    start_date = timezone.now() - timezone.timedelta(days=interval)

    price_history_records = produto.price_history.filter(date__gte=start_date).annotate(month=TruncMonth('date')).order_by('-date')

    price_history = defaultdict(lambda: {
        'min_price': float('inf'),
        'min_price_date': None,
        'min_supplier': None,
        'max_price': float('-inf'),
        'max_price_date': None,
        'max_supplier': None
    })

    for record in price_history_records:
        month = record.date.strftime('%Y-%m')
        if record.price < price_history[month]['min_price']:
            price_history[month]['min_price'] = record.price
            price_history[month]['min_price_date'] = record.date
            price_history[month]['min_supplier'] = record.supplier.company if record.supplier else None
        if record.price > price_history[month]['max_price']:
            price_history[month]['max_price'] = record.price
            price_history[month]['max_price_date'] = record.date
            price_history[month]['max_supplier'] = record.supplier.company if record.supplier else None

    price_history_list = sorted(price_history.items(), key=lambda x: x[0], reverse=True)
    price_history_formatted = [{
        'month': month,
        'min_price': round(data['min_price'], 3) if data['min_price'] != float('inf') else None,
        'min_price_date': data['min_price_date'].strftime('%d/%m/%Y') if data['min_price_date'] else None,
        'min_supplier': data['min_supplier'],
        'max_price': round(data['max_price'], 3) if data['max_price'] != float('-inf') else None,
        'max_price_date': data['max_price_date'].strftime('%d/%m/%Y') if data['max_price_date'] else None,
        'max_supplier': data['max_supplier']
    } for month, data in price_history_list[:days//30]]

    return JsonResponse({'price_history': price_history_formatted})