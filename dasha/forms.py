
from django import forms
from .models import DashaEffect

class DashaEffectForm(forms.ModelForm):
    class Meta:
        model = DashaEffect
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'mahadasha_effect': forms.Textarea(attrs={'rows': 3}),
            'antardasha_effect': forms.Textarea(attrs={'rows': 3}),
            'combined_effect': forms.Textarea(attrs={'rows': 4}),
        }