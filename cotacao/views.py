from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from .models import Cotacao, ItemCotacao
from .forms import CotacaoForm, ItemCotacaoForm
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect, get_object_or_404


class CotacaoListView(ListView):
    model = Cotacao
    template_name = 'cotacao/cotacao_list.html'
    context_object_name = 'cotacoes'

class CotacaoDetailView(DetailView):
    model = Cotacao
    template_name = 'cotacao/cotacao_detail.html'

class CotacaoCreateView(CreateView):
    model = Cotacao
    form_class = CotacaoForm
    template_name = 'cotacao/cotacao_form.html'
    success_url = reverse_lazy('cotacao:cotacao_list')


class AddItemToCotacaoView(CreateView):
    model = ItemCotacao
    form_class = ItemCotacaoForm
    template_name = 'cotacao/itemcotacao_form.html'

    def get_success_url(self):
        return reverse_lazy('cotacao:cotacao_detail', kwargs={'pk': self.kwargs['cotacao_id']})

    def form_valid(self, form):
        form.instance.cotacao_id = self.kwargs['cotacao_id']
        # Verifica se o item já existe para essa cotação
        if ItemCotacao.objects.filter(cotacao_id=self.kwargs['cotacao_id'], produto=form.instance.produto).exists():
            form.add_error('produto', 'Este produto já foi adicionado à cotação.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cotacao'] = get_object_or_404(Cotacao, pk=self.kwargs['cotacao_id'])
        return context
