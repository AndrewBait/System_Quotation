from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import Cotation, CotationProduct
from .forms import CotationForm

def create_cotation(request):
    CotationProductFormSet = inlineformset_factory(Cotation, CotationProduct, fields=('product', 'quantidade', 'tipo_volume'), extra=1)
    if request.method == 'POST':
        form = CotationForm(request.POST)
        formset = CotationProductFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            cotation = form.save()
            formset.instance = cotation
            formset.save()
            # Redirecionar para a lista de cotações ou detalhe da cotação criada
            return redirect('alguma_url')
    else:
        form = CotationForm()
        formset = CotationProductFormSet()
    return render(request, 'quotations/create_cotation.html', {'form': form, 'formset': formset})
