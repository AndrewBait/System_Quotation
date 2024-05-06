from django.shortcuts import render, get_object_or_404, redirect
from .forms import RespostaCotacaoForm, ItemRespostaForm
from cotacao.models import Cotacao, FornecedorCotacaoToken
from suppliers.models import Supplier
from .models import RespostaCotacao, ItemRespostaCotacao


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
        respostas = item.itemrespostacotacao_set.all().order_by('preco')
        respostas_data = [{
            'preco': resposta.preco,
            'fornecedor_nome': resposta.resposta_cotacao.fornecedor.name, 
            'observacao': resposta.observacao,
            'imagem_url': resposta.imagem.url if resposta.imagem else None,
            'is_top3': idx < 3  # Marca as três primeiras respostas como parte do Top 3
        } for idx, resposta in enumerate(respostas)]

        item_data = {
            'produto_nome': item.produto.name,
            'quantidade': item.quantidade,
            'tipo_volume': item.get_tipo_volume_display(),
            'respostas': respostas_data
        }
        itens_data.append(item_data)

    return render(request, 'respostas/visualizar_respostas.html', {'cotacao': cotacao, 'itens_data': itens_data})


