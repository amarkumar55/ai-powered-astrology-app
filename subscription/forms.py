import re
import bleach
from django import forms
from media import countries, states, cities
from utlity.location_loader import get_all_code
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'


class CheckoutForm(forms.Form):
    name = forms.CharField(min_length=3, strip=True, max_length=50, required=True)
    email = forms.EmailField(min_length=10, max_length=50, required=True)
    country = forms.CharField(max_length=50, min_length=3, required=True)
    state = forms.CharField(max_length=50, min_length=2, required=True)
    city = forms.CharField(max_length=50, min_length=2, required=True)
    phone_code = forms.CharField(max_length=3, min_length=1, required=True)
    phone_number = forms.CharField(max_length=12, required=True)

    def __init__(self, request=None, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(request=request, *args, **kwargs)

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not re.fullmatch(r"[A-Za-z\s]+", name):
            raise forms.ValidationError("Name must contain only letters and spaces.")
        return bleach.clean(name, tags=[], strip=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.fullmatch(pattern, email):
            raise forms.ValidationError("Please enter a valid email address.")
        return bleach.clean(email, tags=[], strip=True)

    def clean_country(self):
        country = self.cleaned_data.get("country")
        if not re.fullmatch(r"[A-Za-z\s]+", country):
            raise forms.ValidationError("Country must contain only letters and spaces.")
        return bleach.clean(country, tags=[], strip=True)

    def clean_state(self):
        state = self.cleaned_data.get("state")
        if not re.fullmatch(r"[A-Za-z\s]+", state):
            raise forms.ValidationError("State must contain only letters and spaces.")
        return bleach.clean(state, tags=[], strip=True)

    def clean_city(self):
        city = self.cleaned_data.get("city")
        if not re.fullmatch(r"[A-Za-z\s]+", city):
            raise forms.ValidationError("City must contain only letters and spaces.")
        return bleach.clean(city, tags=[], strip=True)

    def clean_phone_code(self):
        code = self.cleaned_data.get("phone_code")
        if not re.fullmatch(r"\+?\d{1,3}", code):
            raise forms.ValidationError("Phone code must be numeric and can start with '+'.")
        return bleach.clean(code, tags=[], strip=True)

    def clean_phone_number(self):
        number = self.cleaned_data.get("phone_number")
        if not re.fullmatch(r"\d{7,12}", number):
            raise forms.ValidationError("Phone number must be between 7 to 12 digits.")
        return bleach.clean(number, tags=[], strip=True)

    def clean(self):
        cleaned_data = super().clean()

        # Extra sanitization pass (even though each field is cleaned individually)
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        input_country =  cleaned_data.get("country")
        input_state = cleaned_data.get("state")
        input_city = cleaned_data.get("city")
        phone_code = cleaned_data.get("phone_code")

        if not input_country or input_country not in countries:
            self.add_error("country", "Please select a valid country")
       
        if not input_state or not states[input_country][input_state]:
            self.add_error("state", "Please select a valid state")

        if not input_city or not input_city in cities[f"{input_country}_{input_state}"]:
            self.add_error("city", "Please select a valid city")
        
        if not phone_code or not phone_code in get_all_code:
            self.add_error("phone_code", "Please select a phone code")

 
        return cleaned_data
