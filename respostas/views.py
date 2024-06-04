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
            prazo_alternativo = request.POST.get('prazo_alternativo')
            if prazo_alternativo:
                resposta.prazo_alternativo = int(prazo_alternativo)
            resposta.save()
            for item_form in item_forms:
                item_resposta = item_form.save(commit=False)
                item_resposta.resposta_cotacao = resposta
                item_resposta.prazo = cotacao.prazo
                item_resposta.prazo_alternativo = resposta.prazo_alternativo
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

    # Definimos o intervalo padrão de 3 meses
    default_interval_days = 90
    default_start_date = timezone.now() - timezone.timedelta(days=default_interval_days)


    for item in cotacao.itens_cotacao.all():
        # Filtrar respostas válidas (preço maior que 0 e não None)
        respostas_validas = list(filter(lambda r: r.preco is not None and r.preco > 0, item.itemrespostacotacao_set.select_related('resposta_cotacao__fornecedor').order_by('preco')))
        respostas_data = [{
            'preco': round(resposta.preco, 3),
            'preco_prazo_alternativo': round(resposta.preco_prazo_alternativo, 3) if resposta.preco_prazo_alternativo else None,
            'prazo_alternativo': resposta.prazo_alternativo,
            'fornecedor_nome': resposta.resposta_cotacao.fornecedor.company or resposta.resposta_cotacao.fornecedor.name,
            'fornecedor_id': resposta.resposta_cotacao.fornecedor.pk,
            'observacao': resposta.observacao,
            'imagem_url': resposta.imagem.url if resposta.imagem else None,
            'billing_deadline': resposta.resposta_cotacao.fornecedor.billing_deadline_display,
            'delivery_days': resposta.resposta_cotacao.fornecedor.delivery_days_display,
        } for resposta in respostas_validas]
        
        produto = item.produto
        ultimo_preco = produto.price_history.order_by('-date').first()

        # Filtra os registros de histórico de preços para os últimos 3 meses por padrão
        price_history_records = produto.price_history.filter(date__gte=default_start_date, price__gt=0).annotate(month=TruncMonth('date')).order_by('-date')

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
        } for month, data in price_history_list[:default_interval_days//30] if data['min_price'] != float('inf') or data['max_price'] != float('-inf')]

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


from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from .models import Cotacao, ItemCotacao, PedidoAgrupado, Pedido, Supplier
from datetime import date
from django.db.models import Sum

def gerar_pedidos(request):
    cotacao_uuid = request.POST.get('cotacao_uuid', '')
    cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
    usuario = request.user  # Assumindo que você está usando a autenticação padrão do Django

    if request.method == 'POST':
        has_errors = False
        pedido_agrupado_dict = {}  # Dicionário para rastrear pedidos agrupados por fornecedor e prazo

        try:
            with transaction.atomic():
                selecao_keys = [key for key in request.POST if key.startswith('selecao_')]
                for key in selecao_keys:
                    item_id = int(key.split('_', 1)[1])
                    fornecedor_id, preco, *alt_flag = request.POST[key].split('_')
                    fornecedor_id = int(fornecedor_id.strip())
                    preco_decimal = Decimal(preco.replace(',', '.').strip())
                    is_alternative = bool(alt_flag)

                    item_cotacao = ItemCotacao.objects.get(pk=item_id)
                    fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)

                    # Obtendo o prazo alternativo correto do formulário
                    prazo_alternativo_key = f'prazo_alternativo_{item_id}'
                    prazo_alternativo = request.POST.get(prazo_alternativo_key, None)
                    if prazo_alternativo is not None:
                        prazo_alternativo = int(prazo_alternativo)

                    pedido_agrupado_key = (fornecedor_id, is_alternative)

                    if pedido_agrupado_key not in pedido_agrupado_dict:
                        pedido_agrupado = PedidoAgrupado.objects.create(
                            fornecedor=fornecedor,
                            cotacao=cotacao,
                            data_requisicao=date.today(),
                            status='pendente',
                            usuario_criador=usuario
                        )
                        pedido_agrupado_dict[pedido_agrupado_key] = pedido_agrupado
                    else:
                        pedido_agrupado = pedido_agrupado_dict[pedido_agrupado_key]

                    item_resposta_cotacao = ItemRespostaCotacao.objects.get(
                        resposta_cotacao__cotacao=cotacao,
                        resposta_cotacao__fornecedor=fornecedor,
                        item_cotacao=item_cotacao
                    )

                    quantidade_unitaria = item_cotacao.produto.quantidade_por_volume or 1
                    quantidade_total = item_cotacao.quantidade
                    if item_cotacao.tipo_volume in ['Cx', 'Dp', 'Fd', 'Pct', 'Tp']:
                        quantidade_total *= quantidade_unitaria

                    Pedido.objects.create(
                        produto=item_cotacao.produto,
                        quantidade=quantidade_total,
                        tipo_volume=item_cotacao.tipo_volume,
                        preco=preco_decimal,
                        pedido_agrupado=pedido_agrupado,
                        observacoes="Preço alternativo selecionado" if is_alternative else "",
                        prazo_alternativo_selecionado=is_alternative,
                        prazo_alternativo=item_resposta_cotacao.prazo_alternativo if is_alternative else None 
                    )

                # Verificação do valor mínimo do pedido
                for fornecedor_id, pedido_agrupado in pedido_agrupado_dict.items():
                    valor_total_pedido = pedido_agrupado.pedidos.aggregate(total=Sum('preco'))['total']
                    fornecedor = Supplier.objects.get(id=fornecedor_id[0])
                    if fornecedor.minimum_order_value and valor_total_pedido < fornecedor.minimum_order_value:
                        messages.error(request, f'O valor total do pedido para o fornecedor {fornecedor.name} é menor que o pedido mínimo de R$ {fornecedor.minimum_order_value}.')
                        pedido_agrupado.delete()  # Removendo o pedido agrupado se não atender ao valor mínimo
                        has_errors = True

        except Exception as e:
            messages.error(request, f'Erro geral ao gerar pedidos: {str(e)}')
            has_errors = True

        if not has_errors:
            messages.success(request, 'Pedidos gerados com sucesso!')

    return redirect(reverse('respostas:visualizar_cotacoes', args=[cotacao_uuid]))


from django.utils import timezone
from datetime import datetime, timedelta
from django.views.generic import ListView
from django.db.models import Q
from .models import PedidoAgrupado, Supplier


class ListarPedidosView(ListView):
    model = PedidoAgrupado
    template_name = 'respostas/listar_pedidos.html'
    context_object_name = 'pedidos_agrupados'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')
        fornecedor_id = self.request.GET.get('fornecedor')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        prazo = self.request.GET.get('prazo')

        if query:
            queryset = queryset.filter(
                Q(cotacao__nome__icontains=query) |
                Q(fornecedor__name__icontains=query) |
                Q(fornecedor__company__icontains=query) |
                Q(usuario_criador__username__icontains=query)
            )

        if status:
            queryset = queryset.filter(status=status)

        if fornecedor_id:
            queryset = queryset.filter(fornecedor_id=fornecedor_id)

        if start_date and end_date:
            start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
            queryset = queryset.filter(data_requisicao__range=(start_date, end_date))

        if prazo:
            if prazo == "0":
                queryset = queryset.filter(
                    Q(pedidos__prazo_alternativo_selecionado=True, pedidos__prazo_alternativo=0) |
                    Q(pedidos__prazo_alternativo_selecionado=False, cotacao__prazo=0)
                )
            else:
                prazo_int = int(prazo)
                queryset = queryset.filter(
                    Q(pedidos__prazo_alternativo_selecionado=True, pedidos__prazo_alternativo=prazo_int) |
                    Q(pedidos__prazo_alternativo_selecionado=False, cotacao__prazo=prazo_int)
                )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fornecedores'] = Supplier.objects.all()
        return context
    
    

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

# def visualizar_cotacoes(request, cotacao_uuid):
#     cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
#     itens_data = []

#     # Definimos o intervalo padrão de 3 meses
#     default_interval_days = 90
#     default_start_date = timezone.now() - timezone.timedelta(days=default_interval_days)

#     for item in cotacao.itens_cotacao.all():
#         respostas = item.itemrespostacotacao_set.all().select_related('resposta_cotacao__fornecedor').order_by('preco')
#         respostas_data = [{
#             'preco': round(resposta.preco, 3) if resposta.preco is not None else None,
#             'fornecedor_nome': resposta.resposta_cotacao.fornecedor.company if resposta.resposta_cotacao.fornecedor.company else resposta.resposta_cotacao.fornecedor.name,
#             'fornecedor_id': resposta.resposta_cotacao.fornecedor.pk,
#             'observacao': resposta.observacao,
#             'imagem_url': resposta.imagem.url if resposta.imagem else None,
#             'is_top3': idx < 3
#         } for idx, resposta in enumerate(respostas)]

#         produto = item.produto
#         ultimo_preco = produto.price_history.order_by('-date').first()

#         # Filtra os registros de histórico de preços para os últimos 3 meses por padrão
#         price_history_records = produto.price_history.filter(date__gte=default_start_date).annotate(month=TruncMonth('date')).order_by('-date')

#         price_history = defaultdict(lambda: {
#             'min_price': float('inf'),
#             'min_price_date': None,
#             'min_supplier': None,
#             'max_price': float('-inf'),
#             'max_price_date': None,
#             'max_supplier': None
#         })

#         for record in price_history_records:
#             month = record.date.strftime('%Y-%m')
#             if record.price < price_history[month]['min_price']:
#                 price_history[month]['min_price'] = record.price
#                 price_history[month]['min_price_date'] = record.date
#                 price_history[month]['min_supplier'] = record.supplier.company if record.supplier else None
#             if record.price > price_history[month]['max_price']:
#                 price_history[month]['max_price'] = record.price
#                 price_history[month]['max_price_date'] = record.date
#                 price_history[month]['max_supplier'] = record.supplier.company if record.supplier else None

#         # Converte o defaultdict para uma lista, ordenada pelo mês e limitando ao número de meses padrão
#         price_history_list = sorted(price_history.items(), key=lambda x: x[0], reverse=True)
#         price_history_formatted = [{
#             'month': month,
#             'min_price': round(data['min_price'], 3) if data['min_price'] != float('inf') else None,
#             'min_price_date': data['min_price_date'].strftime('%d/%m/%Y') if data['min_price_date'] else None,
#             'min_supplier': data['min_supplier'],
#             'max_price': round(data['max_price'], 3) if data['max_price'] != float('-inf') else None,
#             'max_price_date': data['max_price_date'].strftime('%d/%m/%Y') if data['max_price_date'] else None,
#             'max_supplier': data['max_supplier']
#         } for month, data in price_history_list[:default_interval_days//30]]

#         item_data = {
#             'id': item.pk,
#             'produto_nome': produto.name,
#             'quantidade': item.quantidade,
#             'tipo_volume': item.get_tipo_volume_display(),
#             'ultimo_preco': round(ultimo_preco.price, 3) if ultimo_preco and ultimo_preco.price is not None else None,
#             'data_ultimo_preco': ultimo_preco.date if ultimo_preco else None,
#             'price_history': price_history_formatted,
#             'respostas': respostas_data
#         }
#         itens_data.append(item_data)

#     return render(request, 'respostas/visualizar_respostas.html', {
#         'cotacao': cotacao,
#         'itens_data': itens_data,
#         'prazo': cotacao.prazo  # Incluindo o prazo no contexto
#     })




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




import csv
from django.http import HttpResponse
from .models import PedidoAgrupado, Pedido
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def exportar_pedidos_csv(request):
    pedidos = PedidoAgrupado.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pedidos.csv"'

    writer = csv.writer(response)
    writer.writerow(['Cotação', 'Fornecedor', 'Data da Requisição', 'Vendedor', 'Total de Itens', 'Preço Total', 'Prazo', 'Status'])

    for pedido_agrupado in pedidos:
        prazo = pedido_agrupado.pedidos.first().prazo_alternativo if pedido_agrupado.pedidos.first().prazo_alternativo_selecionado else pedido_agrupado.cotacao.prazo
        writer.writerow([
            pedido_agrupado.cotacao.nome,
            pedido_agrupado.fornecedor.company,
            pedido_agrupado.data_requisicao,
            pedido_agrupado.fornecedor.name,
            pedido_agrupado.total_itens,
            '{:.3f}'.format(pedido_agrupado.preco_total),
            prazo,
            pedido_agrupado.status
        ])

    return response

from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas

def exportar_pedidos_pdf(request):
    # Aplicar os mesmos filtros usados na view ListarPedidosView
    queryset = PedidoAgrupado.objects.all()
    query = request.GET.get('q')
    status = request.GET.get('status')
    fornecedor_id = request.GET.get('fornecedor')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    prazo = request.GET.get('prazo')

    if query:
        queryset = queryset.filter(
            Q(cotacao__nome__icontains=query) |
            Q(fornecedor__name__icontains=query) |
            Q(fornecedor__company__icontains=query) |
            Q(usuario_criador__username__icontains=query)
        )

    if status:
        queryset = queryset.filter(status=status)

    if fornecedor_id:
        queryset = queryset.filter(fornecedor_id=fornecedor_id)

    if start_date and end_date:
        start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1))
        queryset = queryset.filter(data_requisicao__range=(start_date, end_date))

    if prazo:
        prazo = int(prazo)
        queryset = queryset.filter(
            Q(pedidos__prazo_alternativo=prazo) |
            Q(cotacao__prazo=prazo)
        ).distinct()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pedidos.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    y = height - 40
    p.drawString(30, y, 'Pedidos Gerados')
    y -= 30

    headers = ['Cotação', 'Fornecedor', 'Data da Requisição', 'Vendedor', 'Total de Itens', 'Preço Total', 'Prazo', 'Status']
    x_positions = [30, 150, 270, 390, 450, 520, 600, 680]
    for i, header in enumerate(headers):
        p.drawString(x_positions[i], y, header)
    y -= 20

    for pedido_agrupado in queryset:
        if y < 40:  # Check if there's enough space to add more data
            p.showPage()
            y = height - 40

        primeiro_pedido = pedido_agrupado.pedidos.first()
        if primeiro_pedido.prazo_alternativo_selecionado:
            prazo_display = primeiro_pedido.prazo_alternativo
        else:
            prazo_display = pedido_agrupado.cotacao.prazo

        data = [
            pedido_agrupado.cotacao.nome,
            pedido_agrupado.fornecedor.company,
            pedido_agrupado.data_requisicao.strftime('%Y-%m-%d'),
            pedido_agrupado.fornecedor.name,
            str(pedido_agrupado.total_itens),
            'R$ {:.3f}'.format(pedido_agrupado.preco_total),
            str(prazo_display) + ' dias',
            pedido_agrupado.status
        ]
        for i, item in enumerate(data):
            p.drawString(x_positions[i], y, item)
        y -= 20

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response