from django.shortcuts import render, get_object_or_404, redirect
from .forms import RespostaCotacaoForm
from cotacao.models import Cotacao
from suppliers.models import Supplier
from .forms import ItemRespostaForm, ItemRespostaCotacao

def responder_cotacao(request, pk, fornecedor_id):
    cotacao = get_object_or_404(Cotacao, pk=pk)
    fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)
    
    if request.method == 'POST':
        form = RespostaCotacaoForm(request.POST, cotacao=cotacao)
        item_forms = [ItemRespostaForm(request.POST, prefix=f'item_{item.pk}', instance=ItemRespostaCotacao(item_cotacao=item), item_cotacao=item) for item in cotacao.itens_cotacao.all()]

        if form.is_valid() and all(item_form.is_valid() for item_form in item_forms):
            resposta = form.save(commit=False)
            resposta.cotacao = cotacao
            resposta.fornecedor = fornecedor
            resposta.save()

            for item_form in item_forms:
                item_resposta = item_form.save(commit=False)
                item_resposta.resposta_cotacao = resposta
                item_resposta.save()

            return redirect('/')  # Redireciona para a página inicial ou de sucesso
    else:
        form = RespostaCotacaoForm(cotacao=cotacao)
        item_forms = [ItemRespostaForm(prefix=f'item_{item.pk}', instance=ItemRespostaCotacao(item_cotacao=item), item_cotacao=item) for item in cotacao.itens_cotacao.all()]

    context = {
        'cotacao': cotacao,
        'form': form,
        'item_forms': item_forms,  # Adicione isso para garantir que os formulários de itens sejam acessíveis no template
    }
    return render(request, 'respostas/responder_cotacao.html', context)
