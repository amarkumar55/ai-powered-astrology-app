import re
import bleach
from django import forms
from django.utils import timezone 
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'

class LoShuGridForm(forms.Form):

    first_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)
    last_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)
    birth_date= forms.DateField(required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(*args, **kwargs)

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)
            
            
    def clean_first_name(self):
        name = self.cleaned_data.get("first_name")
        if not re.fullmatch(r"[A-Za-z]+", name):
            raise forms.ValidationError("First name can only contain letters.")
        return bleach.clean(name, tags=[], strip=True)

    def clean_last_name(self):
        name = self.cleaned_data.get("last_name")
        if not re.fullmatch(r"[A-Za-z]+", name):
            raise forms.ValidationError("Last name can only contain letters.")
        return bleach.clean(name, tags=[], strip=True)


    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        birth_date = cleaned_data.get("birth_date")

        if not birth_date:
           self.add_error("birth_date", "Birth date is required.")

        if birth_date and birth_date > timezone.now().date():
            self.add_error("birth_date", "Birth date cannot be a future date.")

        return cleaned_data
    
   

     
       
