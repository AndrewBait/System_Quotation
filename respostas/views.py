from django.shortcuts import render, get_object_or_404, redirect
from .forms import RespostaCotacaoForm
from cotacao.models import Cotacao
from suppliers.models import Supplier
from .forms import ItemRespostaForm, ItemRespostaCotacao
from .models import RespostaCotacao

def responder_cotacao(request, pk, fornecedor_id):
    cotacao = get_object_or_404(Cotacao, pk=pk)
    fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)
    
    # Tenta encontrar uma resposta existente
    try:
        resposta_existente = RespostaCotacao.objects.get(cotacao=cotacao, fornecedor=fornecedor)
        resposta_form = RespostaCotacaoForm(request.POST or None, instance=resposta_existente, cotacao=cotacao)
        item_forms = [
            ItemRespostaForm(
                request.POST or None,
                prefix=f'item_{item.pk}',
                instance=ItemRespostaCotacao.objects.get(resposta_cotacao=resposta_existente, item_cotacao=item),
                item_cotacao=item
            )
            for item in cotacao.itens_cotacao.all()
        ]
    except RespostaCotacao.DoesNotExist:
        resposta_form = RespostaCotacaoForm(request.POST or None, cotacao=cotacao)
        item_forms = [
            ItemRespostaForm(
                request.POST or None,
                prefix=f'item_{item.pk}',
                instance=ItemRespostaCotacao(item_cotacao=item),
                item_cotacao=item
            )
            for item in cotacao.itens_cotacao.all()
        ]

    if request.method == 'POST' and resposta_form.is_valid() and all(item_form.is_valid() for item_form in item_forms):
        resposta = resposta_form.save(commit=False)
        resposta.cotacao = cotacao
        resposta.fornecedor = fornecedor
        resposta.save()

        for item_form in item_forms:
            item_resposta = item_form.save(commit=False)
            item_resposta.resposta_cotacao = resposta
            item_resposta.save()

        return redirect('/')  # Redireciona para a página inicial ou de sucesso

    context = {
        'cotacao': cotacao,
        'form': resposta_form,
        'item_forms': item_forms,
    }
    return render(request, 'respostas/responder_cotacao.html', context)
