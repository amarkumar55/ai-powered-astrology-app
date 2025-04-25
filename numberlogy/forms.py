import re
import bleach
from django import forms
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'

class NameNumberForm(forms.Form):  

    first_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)
    last_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)

    def __init__(self, request=None, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(request=request, *args, **kwargs)

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)
            
    def clean(self):
        cleaned_data = super().clean()

        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        if not re.fullmatch(r"^[A-Za-z]+$", cleaned_data['first_name']):
           self.add_error("first_name", "First name must contain only alphabets.")

        if not re.fullmatch(r"^[A-Za-z]+$", cleaned_data['last_name']):
           self.add_error("last_name", "Last name must contain only alphabets.")

    
        return cleaned_data