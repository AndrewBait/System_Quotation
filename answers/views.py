from django.contrib import messages
from .forms import AnswerForm, NonAuthenticatedAnswerForm
from django.views.generic import ListView, DetailView, CreateView, FormView, TemplateView
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from cotacao.models import Cotacao, ItemCotacao
from .models import Answer
from .forms import AnswerForm
from suppliers.models import Supplier  
from django.views import View
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect



class OpenCotacaoListView(ListView):
    model = Cotacao
    template_name = 'answers/open_cotacao_list.html'

    def get_queryset(self):
        current_supplier = self.request.user.supplier
        return Cotacao.objects.filter(
            data_fechamento__gte=timezone.now(),
            fornecedores_convidados=current_supplier
        )


class CotacaoDetailView(DetailView):
    model = Cotacao
    template_name = 'answers/cotacao_detail.html'


    def get_object(self):
        uuid = self.kwargs.get('uuid')
        return get_object_or_404(Cotacao, uuid=uuid)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao = context['object']
        item_forms = [(item, AnswerForm(prefix=str(item.id))) for item in cotacao.itens_cotacao.all()]
        context['item_forms'] = item_forms
        context['fornecedor_uuid'] = self.request.GET.get('fornecedor_uuid', None)
        return context


class AnswerCreateView(LoginRequiredMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'answers/submit_answer.html'


    def form_valid(self, form):
        item_cotacao_id = self.kwargs.get('item_cotacao_id')
        item_cotacao = get_object_or_404(ItemCotacao, id=item_cotacao_id)
        form.instance.supplier = get_object_or_404(Supplier, user=self.request.user)
        form.instance.item_cotacao = item_cotacao
        return super().form_valid(form)
    
    def get_success_url(self):
        cotacao_id = self.kwargs.get('cotacao_id')
        return reverse_lazy('answers:cotacao_detail', kwargs={'pk': cotacao_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cotacao_id'] = self.kwargs.get('cotacao_id')
        return context    


class SubmitAnswersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cotacao = get_object_or_404(Cotacao, uuid=kwargs['uuid'])
        AnswerFormSet = modelformset_factory(Answer, form=AnswerForm, extra=cotacao.itens_cotacao.count())
        formset = AnswerFormSet(queryset=Answer.objects.none())

        return render(request, 'answers/submit_answer_by_uuid.html', {'cotacao': cotacao, 'formset': formset})

    def post(self, request, *args, **kwargs):
        cotacao = get_object_or_404(Cotacao, uuid=kwargs['uuid'])
        AnswerFormSet = modelformset_factory(Answer, form=AnswerForm, extra=0)
        formset = AnswerFormSet(request.POST)

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.supplier = request.user.supplier
                instance.save()
            return redirect(reverse_lazy('answers:answer_success'))
        return render(request, 'answers/submit_answer_by_uuid.html', {'cotacao': cotacao, 'formset': formset})
        

@login_required
def submit_answers_by_uuid(request, uuid):
    cotacao = get_object_or_404(Cotacao, uuid=uuid)
    fornecedor = request.user.supplier

    if request.method == 'POST':
        for item in cotacao.itens_cotacao.all():
            price_input_name = f'price_{item.id}'
            price = request.POST.get(price_input_name)
            if price:
                Answer.objects.create(
                    item_cotacao=item,
                    supplier=fornecedor,
                    price=price
                )
        return HttpResponseRedirect(reverse('answers:answer_success')) 
    else:
        return render(request, 'answers/submit_answer_by_uuid.html', {'cotacao': cotacao})
       

@login_required
class SubmitAnswerByUUIDView(FormView):
    template_name = 'answers/submit_answer_by_uuid.html'
    form_class = NonAuthenticatedAnswerForm

    def form_valid(self, form):
        cotacao_uuid = self.kwargs.get('uuid')
        cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
        fornecedor_email = form.cleaned_data['fornecedor_email']
        fornecedor = get_object_or_404(Supplier, email=fornecedor_email)

        for item in cotacao.itens_cotacao.all():
            price = form.cleaned_data[f'price_{item.id}']
            Answer.objects.create(  
                item_cotacao=item,
                supplier=fornecedor,
                price=price,
            )
        return redirect('answers:answer_success') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao_uuid = self.kwargs.get('uuid')
        cotacao = get_object_or_404(Cotacao, uuid=cotacao_uuid)
        context['cotacao'] = cotacao
        return context
    

class CotacaoRespostasListView(ListView):
    model = Cotacao
    template_name = 'answers/cotacao_respostas_list.html'
    context_object_name = 'cotacoes'

    def get_queryset(self):
        return Cotacao.objects.prefetch_related(
            Prefetch('itens_cotacao__answers', queryset=Answer.objects.select_related('supplier'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacoes = context['cotacoes']
        cotacoes_respostas = []

        for cotacao in cotacoes:
            itens_respostas = []
            for item in cotacao.itens_cotacao.all():
                respostas = item.answers.all()
                itens_respostas.append((item, respostas))
            cotacoes_respostas.append((cotacao, itens_respostas))

        context['cotacoes_respostas'] = cotacoes_respostas
        return context


class CotacaoRespostasDetailView(DetailView):
    model = Cotacao
    template_name = 'answers/cotacao_respostas_detail.html'
    context_object_name = 'cotacao'

    def get_object(self, queryset=None):
        return get_object_or_404(Cotacao, uuid=self.kwargs['uuid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cotacao = context['cotacao']
        itens_respostas = []

        for item in cotacao.itens_cotacao.all():
            respostas = item.answers.select_related('supplier').all()
            itens_respostas.append((item, respostas))

        context['itens_respostas'] = itens_respostas
        return context


class AnswerSuccessView(TemplateView):
    template_name = 'answers/answer_success.html'