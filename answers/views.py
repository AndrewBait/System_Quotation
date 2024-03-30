# Em answers/views.py

from django.views.generic import ListView, DetailView, CreateView
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from cotacao.models import Cotacao, ItemCotacao
from .models import Answer
from .forms import AnswerForm
from suppliers.models import Supplier  # Se você estiver associando respostas a um modelo de fornecedor
from django.views import View


class OpenCotacaoListView(ListView):
    model = Cotacao
    template_name = 'answers/open_cotacao_list.html'

    def get_queryset(self):
        # Filtre aqui as cotações que estão abertas
        return Cotacao.objects.filter(data_fechamento__gte=timezone.now())


class CotacaoDetailView(DetailView):
    model = Cotacao
    template_name = 'answers/cotacao_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao = context['object']
        item_forms = [(item, AnswerForm(prefix=str(item.id))) for item in cotacao.itens_cotacao.all()]
        context['item_forms'] = item_forms
        return context


class AnswerCreateView(LoginRequiredMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'answers/submit_answer.html'
    # Supondo que você tenha uma maneira de determinar o item de cotação e o fornecedor (por exemplo, através do usuário autenticado)

    def form_valid(self, form):
        item_cotacao_id = self.kwargs.get('item_cotacao_id')
        item_cotacao = get_object_or_404(ItemCotacao, id=item_cotacao_id)
        # Configure o fornecedor com base no usuário autenticado, ajuste conforme necessário
        # Aqui estamos assumindo que seu modelo Supplier tem uma relação com o User
        form.instance.supplier = get_object_or_404(Supplier, user=self.request.user)
        form.instance.item_cotacao = item_cotacao
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redireciona para a página detalhada da cotação após a submissão bem-sucedida da resposta
        cotacao_id = self.kwargs.get('cotacao_id')
        return reverse_lazy('answers:cotacao_detail', kwargs={'pk': cotacao_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cotacao_id'] = self.kwargs.get('cotacao_id')  # Passa o ID da cotação para o template
        return context


class SubmitAnswersView(View):
    def post(self, request, *args, **kwargs):
        cotacao_id = kwargs.get('cotacao_id')
        cotacao = get_object_or_404(Cotacao, id=cotacao_id)

        # Encontra o fornecedor pelo email do usuário autenticado
        # Isso presume que o email usado no modelo User é o mesmo que no modelo Supplier
        supplier = get_object_or_404(Supplier, email=request.user.email)

        # Processa cada item de cotação e salva a resposta
        for item in cotacao.itens_cotacao.all():
            form = AnswerForm(request.POST, prefix=str(item.id))
            if form.is_valid():
                answer = form.save(commit=False)
                answer.item_cotacao = item
                answer.supplier = supplier
                answer.save()

        return redirect('answers:cotacao_detail', pk=cotacao_id)