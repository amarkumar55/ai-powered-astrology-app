import re
import bleach
from django import forms
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'

class NameNumberForm(forms.Form):  

    first_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)
    last_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(*args, **kwargs)

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)
            
    def clean(self):
        cleaned_data = super().clean()

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        # sanitize only if value exists
        if first_name:
            cleaned_first_name = bleach.clean(first_name, tags=[], strip=True)
            if not cleaned_first_name:
                self.add_error('first_name', "First name is invalid after sanitization.")
            elif not re.fullmatch(r"^[A-Za-z]+$", cleaned_first_name):
                self.add_error("first_name", "First name must contain only alphabets.")
            else:
                cleaned_data['first_name'] = cleaned_first_name

        if last_name:
            cleaned_last_name = bleach.clean(last_name, tags=[], strip=True)
            if not cleaned_last_name:
                self.add_error('last_name', "Last name is invalid after sanitization.")
            elif not re.fullmatch(r"^[A-Za-z]+$", cleaned_last_name):
                self.add_error("last_name", "Last name must contain only alphabets.")
            else:
                cleaned_data['last_name'] = cleaned_last_name

        return cleaned_data