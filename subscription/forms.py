import re
import bleach
from django import forms
from media.countries import country
from media.states import states_lookup
from media.cities import cities_by_state
from utlity.location_loader import get_all_code
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'


class CheckoutForm(forms.Form):
    
    country = forms.CharField(max_length=50, min_length=2, required=True)
    state = forms.CharField(max_length=50, min_length=2, required=True)
    city = forms.CharField(max_length=50, min_length=2, required=True)
    pincode = forms.CharField(max_length=6, min_length=6, required=True)
   

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(*args, **kwargs)

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

    def clean_pincode(self):
        code = self.cleaned_data.get("pincode")
        if not re.fullmatch(r"\+?\d{6}", code):
            raise forms.ValidationError("Pin code must be numeric.")
        return bleach.clean(code, tags=[], strip=True)


    def clean(self):
        cleaned_data = super().clean()

        # Sanitize all string fields
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        input_country = cleaned_data.get("country")
        input_state = cleaned_data.get("state")
        input_city = cleaned_data.get("city")

        # Validate country
        if not input_country or input_country not in country:
            self.add_error("country", "Please select a valid country")
            return cleaned_data  # Early return, don't validate state/city without valid country

        # Validate state using the country abbreviation as the key
        if input_country not in states_lookup or not input_state or input_state not in states_lookup[input_country]:
            self.add_error("state", "Please select a valid state")
            return cleaned_data  # Early return, don't validate city without valid state

        # Validate city based on the combined country and state key
        city_key = f"{input_country}_{input_state}"
        if city_key not in cities_by_state or not input_city or input_city not in cities_by_state[city_key]:
            self.add_error("city", "Please select a valid city")

        return cleaned_data
