from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cotation, CotationProduct
from .forms import CotationForm, CotationProductForm

class CotationListView(LoginRequiredMixin, ListView):
    model = Cotation
    template_name = 'quotations/cotation_list.html'
    context_object_name = 'cotation_list'
    login_url = '/accounts/login/'

class CotationCreateView(LoginRequiredMixin, CreateView):
    model = Cotation
    form_class = CotationForm
    template_name = 'quotations/create_cotation.html'
    success_url = reverse_lazy('quotations:cotation_list')
    login_url = '/accounts/login/'

class CotationDetailView(LoginRequiredMixin, DetailView):
    model = Cotation
    template_name = 'quotations/cotation_detail.html'
    context_object_name = 'cotation'
    login_url = '/accounts/login/'

class CotationUpdateView(LoginRequiredMixin, UpdateView):
    model = Cotation
    form_class = CotationForm
    template_name = 'quotations/cotation_edit.html'
    success_url = reverse_lazy('quotations:cotation_list')
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            data['cotationproducts'] = inlineformset_factory(Cotation, CotationProduct, form=CotationProductForm, extra=1)(self.request.POST)
        else:
            data['cotationproducts'] = inlineformset_factory(Cotation, CotationProduct, form=CotationProductForm, extra=1)()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        cotationproducts = context['cotationproducts']
        if cotationproducts.is_valid():
            self.object = form.save()
            cotationproducts.instance = self.object
            cotationproducts.save()
        return super().form_valid(form)

class CotationDeleteView(LoginRequiredMixin, DeleteView):
    model = Cotation
    template_name = 'quotations/cotation_confirm_delete.html'
    success_url = reverse_lazy('quotations:cotation_list')
    login_url = '/accounts/login/'

class CotationAddProductsView(LoginRequiredMixin, UpdateView):
    model = Cotation
    fields = []
    template_name = 'quotations/cotation_add_products.html'
    success_url = reverse_lazy('quotations:cotation_list')
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        CotationProductFormSet = inlineformset_factory(Cotation, CotationProduct, form=CotationProductForm, extra=1, can_delete=True)
        if self.request.method == 'POST':
            data['products_formset'] = CotationProductFormSet(self.request.POST, instance=self.object)
        else:
            data['products_formset'] = CotationProductFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        products_formset = context['products_formset']
        if products_formset.is_valid():
            products_formset.save()
        return super().form_valid(form)
