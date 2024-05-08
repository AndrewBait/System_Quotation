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


def criar_item_form(item, resposta_existente, post_data=None, file_data=None):
    item_resposta, created = ItemRespostaCotacao.objects.get_or_create(
        resposta_cotacao=resposta_existente, 
        item_cotacao=item,
        defaults={'item_cotacao': item}  # O 'defaults' é utilizado apenas se estiver criando um novo registro
    )
    # Ajuste aqui para passar file_data junto com post_data
    return ItemRespostaForm(post_data, file_data, prefix=f'item_{item.pk}', instance=item_resposta)


def responder_cotacao(request, cotacao_uuid, fornecedor_id, token):
    cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
    fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)
    get_object_or_404(FornecedorCotacaoToken, cotacao=cotacao, fornecedor=fornecedor, token=token)

    if cotacao.status == 'inativo':
        # Aqui você pode redirecionar para uma página específica ou renderizar uma template com a mensagem
        return render(request, 'respostas/cotacao_fechada.html', {
            'message': 'Esta cotação está fechada no momento. Para mais informações, entre em contato pelo email: contato@empresa.com.'
        })

    resposta_existente, _ = RespostaCotacao.objects.get_or_create(
        cotacao=cotacao, 
        fornecedor=fornecedor
    )
    
    resposta_form = RespostaCotacaoForm(request.POST or None, request.FILES or None, instance=resposta_existente, cotacao=cotacao)
    item_forms = [criar_item_form(item, resposta_existente, request.POST or None, request.FILES or None) for item in cotacao.itens_cotacao.all()]

    if request.method == 'POST' and resposta_form.is_valid() and all(item_form.is_valid() for item_form in item_forms):
        resposta = resposta_form.save(commit=False)
        resposta.cotacao = cotacao
        resposta.fornecedor = fornecedor
        resposta.save()

        for item_form in item_forms:
            item_resposta = item_form.save(commit=False)
            item_resposta.resposta_cotacao = resposta
            item_resposta.save()

        return redirect('respostas:cotacao_respondida')  # Substitua 'home' pelo nome da rota desejada configurada no urls.py

    context = {
        'cotacao': cotacao,
        'form': resposta_form,
        'item_forms': item_forms,
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
            'is_top3': idx < 3  # Marca as três primeiras respostas como parte do Top 3
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
    

class EditarPedidoAgrupadoView(UpdateView):
    model = PedidoAgrupado
    fields = []
    template_name = 'respostas/editar_pedido.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        PedidoFormSet = inlineformset_factory(PedidoAgrupado, Pedido, fields=('quantidade', 'preco', 'produto'), extra=0)
        if self.request.POST:
            context['formset'] = PedidoFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = PedidoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            formset.save()
            return redirect('respostas:listar_pedidos')
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    

class DeletarPedidoView(DeleteView):
    model = Pedido
    template_name = 'respostas/deletar_pedido.html'
    success_url = reverse_lazy('respostas:listar_pedidos')
