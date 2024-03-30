from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Departamento, Cotacao, ItemCotacao
from .forms import CotacaoForm, ItemCotacaoForm, DepartamentoForm
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError


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


class EditItemCotacaoView(UpdateView):
    model = ItemCotacao
    form_class = ItemCotacaoForm
    template_name = 'cotacao/itemcotacao_form.html'

    def get_success_url(self):
        return reverse_lazy('cotacao:cotacao_detail', kwargs={'pk': self.object.cotacao.pk})


class DeleteItemCotacaoView(DeleteView):
    model = ItemCotacao
    template_name = 'cotacao/itemcotacao_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('cotacao:cotacao_detail', kwargs={'pk': self.object.cotacao.pk})
    

class DepartamentoCreateView(CreateView):
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'cotacao/departamento_form.html'
    success_url = reverse_lazy('cotacao:departamento_new')

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            departamento_id = request.POST.get("delete")
            departamento = Departamento.objects.get(pk=departamento_id)
            try:
                departamento.delete()
            except ValidationError as e:
                messages.error(request, e.messages[0])
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departamentos'] = Departamento.objects.all().order_by('nome')
        return context


class DepartamentoDeleteView(DeleteView):
    model = Departamento
    success_url = reverse_lazy('cotacao:departamento_new')  
    template_name = 'cotacao/departamento_confirm_delete.html'


