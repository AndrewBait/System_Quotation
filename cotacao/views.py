from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from .models import Departamento, Cotacao, ItemCotacao
from .forms import CotacaoForm, ItemCotacaoForm, DepartamentoForm
from suppliers.models import Supplier
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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


class CotacaoDeleteView(DeleteView):
    model = Cotacao
    success_url = reverse_lazy('cotacao:cotacao_list')  # Redirect to the list after deletion


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


def enviar_cotacao_view(request, pk):
    # Busca a cotação pelo pk, isso permanece porque a função é chamada com pk
    cotacao = get_object_or_404(Cotacao, pk=pk)
    fornecedores = Supplier.objects.all()

    # Você constrói o link de resposta aqui para o e-mail, usando 'uuid'
    # Isso está correto e pode permanecer assim


    if request.method == 'POST':
        selected_fornecedores = request.POST.getlist('fornecedores')
        for fornecedor_id in selected_fornecedores:
            fornecedor = get_object_or_404(Supplier, pk=fornecedor_id)

            link_resposta = request.build_absolute_uri(
                reverse('answers:submit_answers_by_uuid', kwargs={'uuid': cotacao.uuid})
            )            
            
            # Criação do contexto para o template de e-mail
            context = {
                'fornecedor': fornecedor,
                'cotacao': cotacao,
                'link_resposta': link_resposta  # Aqui usamos o link que já construímos anteriormente
            }
            
            # Renderiza o conteúdo do e-mail
            html_content = render_to_string('emails/enviar_cotacao.html', context)
            text_content = strip_tags(html_content)
            
            # Envia o e-mail
            send_mail(
                subject='Nova Cotação Disponível',
                message=text_content,
                from_email='seuemail@example.com',
                recipient_list=[fornecedor.email],
                html_message=html_content,
                fail_silently=False,
            )

        # Após enviar os e-mails, redireciona para a lista de cotações
        # A função de redirect aqui está correta e não precisa ser mudada
        return redirect('cotacao:cotacao_list')

    # Renderiza a página para enviar as cotações caso o método não seja POST
    return render(request, 'cotacao/enviar_cotacao.html', {'cotacao': cotacao, 'fornecedores': fornecedores})
