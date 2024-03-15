from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import Cotation, CotationProduct
from .forms import CotationForm, CotationProductForm
from django.shortcuts import get_object_or_404, render, redirect


def create_cotation(request):
    CotationProductFormSet = inlineformset_factory(Cotation, CotationProduct, form=CotationProductForm, extra=1)
    if request.method == 'POST':
        form = CotationForm(request.POST)
        formset = CotationProductFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            cotation = form.save()
            formset.instance = cotation
            formset.save()
            # Redirecionar para a lista de cotações ou detalhe da cotação criada
            return redirect('add_products_to_cotation.html')
    else:
        form = CotationForm()
        formset = CotationProductFormSet()
    return render(request, 'quotations/create_cotation.html', {'form': form, 'formset': formset})


def add_products_to_cotation(request, cotation_id):
    cotation = get_object_or_404(Cotation, id=cotation_id)
    CotationProductFormSet = inlineformset_factory(Cotation, CotationProduct, form=CotationProductForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        formset = CotationProductFormSet(request.POST, instance=cotation)
        if formset.is_valid():
            formset.save()
            return redirect('add_products_to_cotation.html')
    else:
        formset = CotationProductFormSet(instance=cotation)
    
    return render(request, 'quotations/add_products_to_cotation.html', {'formset': formset, 'cotation': cotation})