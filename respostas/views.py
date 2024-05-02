from django.shortcuts import render, get_object_or_404, redirect
from .forms import RespostaCotacaoForm, ItemRespostaForm
from cotacao.models import Cotacao
from suppliers.models import Supplier
from .models import RespostaCotacao, ItemRespostaCotacao

def criar_item_form(item, resposta_existente, data):
    item_resposta, created = ItemRespostaCotacao.objects.get_or_create(
        resposta_cotacao=resposta_existente, 
        item_cotacao=item,
        defaults={'item_cotacao': item}  # O 'defaults' é utilizado apenas se estiver criando um novo registro
    )
    return ItemRespostaForm(data or None, prefix=f'item_{item.pk}', instance=item_resposta)

def responder_cotacao(request, pk, fornecedor_id):
    cotacao = get_object_or_404(Cotacao, pk=pk)
    fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)
    resposta_existente, _ = RespostaCotacao.objects.get_or_create(
        cotacao=cotacao, 
        fornecedor=fornecedor
    )
    
    resposta_form = RespostaCotacaoForm(request.POST or None, instance=resposta_existente, cotacao=cotacao)
    item_forms = [criar_item_form(item, resposta_existente, request.POST or None) for item in cotacao.itens_cotacao.all()]

    if request.method == 'POST' and resposta_form.is_valid() and all(item_form.is_valid() for item_form in item_forms):
        resposta = resposta_form.save(commit=False)
        resposta.cotacao = cotacao
        resposta.fornecedor = fornecedor
        resposta.save()

        for item_form in item_forms:
            item_resposta = item_form.save(commit=False)
            item_resposta.resposta_cotacao = resposta
            item_resposta.save()

        return redirect('home')  # Substitua 'home' pelo nome da rota desejada configurada no urls.py

    context = {
        'cotacao': cotacao,
        'form': resposta_form,
        'item_forms': item_forms,
    }
    return render(request, 'respostas/responder_cotacao.html', context)
