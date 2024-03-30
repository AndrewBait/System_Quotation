from django import forms
from .models import Answer

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['price']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }