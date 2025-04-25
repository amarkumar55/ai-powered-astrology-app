import re
import bleach
from django import forms
from datetime import datetime
from .models import UserPanchang 
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'

class PanchangForm(forms.ModelForm):
 
    TIME_PERIOD_CHOICES = [
        ('AM', 'AM'),
        ('PM', 'PM'),
    ]
   
    first_name = forms.CharField(min_length=2, strip=True,max_length=50,required=True)
    last_name = forms.CharField(min_length=2, strip=True,max_length=50,required=True)
    days = forms.IntegerField(min_value=1, max_value=31, required=True)
    months = forms.IntegerField(min_value=1, max_value=12, required=True)
    years = forms.IntegerField(min_value=1954, max_value=datetime.now().year, required=True)
    hours = forms.IntegerField(min_value=0, max_value=23, required=True)
    minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    seconds = forms.IntegerField(min_value=0, max_value=59, required=True)
    time_format = forms.ChoiceField(choices=TIME_PERIOD_CHOICES,required=True)
    place_of_birth = forms.CharField(required=True)
    latitude = forms.FloatField(required=True)
    longitude = forms.FloatField(required=True)
    is_accepted_terms = forms.BooleanField(required=True)
    
    class Meta:
        model = UserPanchang
        fields = ["first_name", "last_name", "place_of_birth"]

    def __init__(self, request=None, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(request=request, *args, **kwargs)

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

    def clean_place_of_birth(self):
        place_of_birth = self.cleaned_data.get("place_of_birth")
        if not re.fullmatch(r"[A-Za-z0-9\s,.-]+", place_of_birth):
            raise forms.ValidationError("Place must contain only alphabets, digits, spaces, commas, periods, and hyphens.")
        return bleach.clean(place_of_birth, tags=[], strip=True)

    def clean_latitude(self):
        latitude = self.cleaned_data.get("latitude")
        if latitude is not None and not (-90 <= latitude <= 90):
            raise forms.ValidationError("Latitude must be between -90 and 90.")
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get("longitude")
        if longitude is not None and not (-180 <= longitude <= 180):
            raise forms.ValidationError("Longitude must be between -180 and 180.")
        return longitude
    

    def convert_to_24_hour(self, hour, time_type):
        """Convert 12-hour time to 24-hour format."""
        if time_type == "AM":
            return 0 if hour == 12 else hour
        elif time_type == "PM":
            return 12 if hour == 12 else hour + 12
        return hour

    def clean(self):
        cleaned_data = super().clean()

        # Sanitize all string fields again (extra protection)
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        try:
            hours = self.convert_to_24_hour(
                cleaned_data.get("hours"), cleaned_data.get("time_format")
            )
            datetime(
                cleaned_data.get("years"),
                cleaned_data.get("months"),
                cleaned_data.get("days"),
                hours,
                cleaned_data.get("minutes"),
                cleaned_data.get("seconds")
            )
        except (TypeError, ValueError):
            raise forms.ValidationError("Invalid birth date/time.")
        
        if cleaned_data.get("is_accepted_terms") != True:
            self.add_error("is_accepted_terms", "Please accept the terms and conditions.")

        return cleaned_data

    