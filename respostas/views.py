import decimal
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
        if request.method != 'POST':
            return redirect('cotacao:cotacao_list')

        print(request.POST)
        cotacao_uuid = request.POST.get('cotacao_uuid')
        cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
        has_errors = False

        try:
            with transaction.atomic():
                selecao_keys = [key for key in request.POST if key.startswith('selecao_')]
                for key in selecao_keys:
                    valor = request.POST[key]
                    print(f"key: {key}, valor: {valor}")
                    # Extração e validação do item_id
                    try:
                        item_id = int(key.split('_', 1)[1])
                    except ValueError:
                        messages.error(request, 'ID do item deve ser um número válido.')
                        has_errors = True
                        continue
                    
                    parts = valor.split('_')
                    if len(parts) != 2:
                        messages.error(request, 'Fornecedor ID ou preço incompleto ou inválido.')
                        continue
                    
                    fornecedor_id, preco = map(str.strip, parts)
                    try:
                        fornecedor_id = int(fornecedor_id)
                        preco_decimal = Decimal(preco.replace(',', '.'))
                        item_cotacao = ItemCotacao.objects.get(pk=item_id)
                        fornecedor = Supplier.objects.get(pk=fornecedor_id)
                        
                        Pedido.objects.create(
                            produto=item_cotacao.produto,
                            quantidade=item_cotacao.quantidade,
                            tipo_volume=item_cotacao.tipo_volume,
                            fornecedor=fornecedor,
                            preco=preco_decimal,
                            data_requisicao=date.today(),
                            status='pendente'
                        )
                    except Exception as e:
                        messages.error(request, f'Erro ao processar pedido: {e}')
                        has_errors = True

        except Exception as e:
            messages.error(request, f'Erro geral ao gerar pedidos: {e}')
            has_errors = True

        if not has_errors:
            messages.success(request, 'Pedidos gerados com sucesso!')
        return redirect('cotacao:cotacao_list')
# {% url 'respostas:visualizar_cotacoes' cotacao.uuid %}

# def gerar_pedidos(request):
#     if request.method == 'POST':
#         # sua lógica de criação de pedidos...
#         messages.success(request, 'Pedidos gerados com sucesso!')
#         return render(request, 'cotacao/cotacao_list.html')
#     return render(request, 'cotacao/cotacao_list.html')


# logger = logging.getLogger(__name__)

# class ProcessarRespostaCotacaoView(View):
#     def post(self, request, cotacao_id):
#         if request.method != 'POST':
#             return HttpResponse("Acesso inválido. Este método requer POST.", status=405)

#         with transaction.atomic():
#             try:
#                 cotacao = get_object_or_404(Cotacao, pk=cotacao_id)
#                 if cotacao.status == 'fechado':
#                     logger.warning(f"Cotação {cotacao_id} já está fechada.")
#                     return HttpResponse("Esta cotação já está fechada.", status=403)

#                 selected_items = {}
#                 for key, value in request.POST.items():
#                     if key.startswith('selecao_') and value:
#                         item_id = key.split('_')[1]
#                         preco_str = request.POST.get(f'preco_{item_id}_{value}', '0').replace(',', '.')
#                         preco = Decimal(preco_str)
#                         selected_items[item_id] = (value, preco)

#                 for item_id, (fornecedor_id, preco) in selected_items.items():
#                     item_resposta = ItemRespostaCotacao.objects.filter(
#                         resposta_cotacao__cotacao_id=cotacao_id,
#                         resposta_cotacao__fornecedor_id=fornecedor_id,
#                         item_cotacao_id=item_id,
#                         preco=preco
#                     ).first()

#                     if item_resposta:
#                         pedido, created = Pedido.objects.update_or_create(
#                             produto=item_resposta.item_cotacao.produto,
#                             defaults={
#                                 'quantidade': item_resposta.item_cotacao.quantidade,
#                                 'tipo_volume': item_resposta.item_cotacao.tipo_volume,
#                                 'fornecedor_id': fornecedor_id,
#                                 'preco': preco,
#                                 'data_requisicao': date.today(),
#                                 'status': 'pendente'
#                             }
#                         )
#                         logger.info(f"Pedido {'criado' if created else 'atualizado'} com sucesso: {pedido}")
#                     else:
#                         logger.error(f"Item resposta não encontrado: item_id={item_id}, fornecedor_id={fornecedor_id}, preco={preco}")
#                         raise ValidationError(f"Preço ou fornecedor inválido para o item {item_id}.")

#                 return redirect('cotacao:cotacao_list')
#             except ValidationError as e:
#                 logger.error(f"Erro de validação: {e}")
#                 return HttpResponse(f"Erro de validação: {e}", status=400)
#             except Exception as e:
#                 logger.error(f"Erro inesperado: {e}")
#                 return HttpResponse(f"Erro inesperado ao processar a requisição: {str(e)}", status=500)