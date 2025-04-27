import re
import bleach
from django import forms
from datetime import datetime
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'

class CompatibilityForm(forms.Form):
    TIME_PERIOD_CHOICES = [('AM', 'AM'), ('PM', 'PM')]

    # Boy fields
    boy_full_name = forms.CharField(max_length=40, required=True)
    boy_days = forms.IntegerField(min_value=1, max_value=31, required=True)
    boy_months = forms.IntegerField(min_value=1, max_value=12, required=True)
    boy_years = forms.IntegerField(min_value=1954, max_value=datetime.now().year, required=True)
    boy_hours = forms.IntegerField(min_value=1, max_value=12, required=True)  # 12-hour format
    boy_minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    boy_seconds = forms.IntegerField(min_value=0, max_value=59, required=True)
    boy_time_type = forms.ChoiceField(choices=TIME_PERIOD_CHOICES, required=True)
    boy_latitude = forms.FloatField(required=False)
    boy_longitude = forms.FloatField(required=False)
    boy_place = forms.CharField(max_length=255, required=True)

    # Girl fields
    girl_full_name = forms.CharField(max_length=40, required=True)
    girl_days = forms.IntegerField(min_value=1, max_value=31, required=True)
    girl_months = forms.IntegerField(min_value=1, max_value=12, required=True)
    girl_years = forms.IntegerField(min_value=1954, max_value=datetime.now().year, required=True)
    girl_hours = forms.IntegerField(min_value=1, max_value=12, required=True)  # 12-hour format
    girl_minutes = forms.IntegerField(min_value=0, max_value=59, required=True)
    girl_seconds = forms.IntegerField(min_value=0, max_value=59, required=True)
    girl_time_type = forms.ChoiceField(choices=TIME_PERIOD_CHOICES, required=True)
    girl_latitude = forms.FloatField(required=False)
    girl_longitude = forms.FloatField(required=False)
    girl_place = forms.CharField(max_length=255, required=True)

    is_accepted_terms = forms.BooleanField(required=True)

    def __init__(self, request=None, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(*args, **kwargs)
        self.request = request  

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)

    def clean_boy_full_name(self):
        name = self.cleaned_data.get("boy_full_name", "")
        if not re.fullmatch(r"^[A-Za-z\s]+$", name):
            raise forms.ValidationError("Boy's full name must contain only alphabets and spaces.")
        return bleach.clean(name, tags=[], strip=True)

    def clean_girl_full_name(self):
        name = self.cleaned_data.get("girl_full_name", "")
        if not re.fullmatch(r"^[A-Za-z\s]+$", name):
            raise forms.ValidationError("Girl's full name must contain only alphabets and spaces.")
        return bleach.clean(name, tags=[], strip=True)

    def clean_boy_place(self):
        place = self.cleaned_data.get("boy_place", "")
        if not re.fullmatch(r"^[A-Za-z0-9\s]+$", place):
            raise forms.ValidationError("Place can contain only alphabets, numbers, and spaces.")
        return bleach.clean(place, tags=[], strip=True)

    def clean_girl_place(self):
        place = self.cleaned_data.get("girl_place", "")
        if not re.fullmatch(r"^[A-Za-z0-9\s]+$", place):
            raise forms.ValidationError("Place can contain only alphabets, numbers, and spaces.")
        return bleach.clean(place, tags=[], strip=True)

    def convert_to_24_hour(self, hour, time_type):
        """Convert 12-hour time to 24-hour format."""
        if time_type == "AM":
            return 0 if hour == 12 else hour
        elif time_type == "PM":
            return 12 if hour == 12 else hour + 12
        return hour

    def clean_boy_latitude(self):
        lat = self.cleaned_data.get('boy_latitude')
        if lat is not None:
            if not (-90 <= lat <= 90):
                raise forms.ValidationError("Latitude must be between -90 and 90.")
        return lat

    def clean_boy_longitude(self):
        lon = self.cleaned_data.get('boy_longitude')
        if lon is not None:
            if not (-180 <= lon <= 180):
                raise forms.ValidationError("Longitude must be between -180 and 180.")
        return lon

    def clean_girl_latitude(self):
        lat = self.cleaned_data.get('girl_latitude')
        if lat is not None:
            if not (-90 <= lat <= 90):
                raise forms.ValidationError("Latitude must be between -90 and 90.")
        return lat

    def clean_girl_longitude(self):
        lon = self.cleaned_data.get('girl_longitude')
        if lon is not None:
            if not (-180 <= lon <= 180):
                raise forms.ValidationError("Longitude must be between -180 and 180.")
        return lon
   
   
    def clean(self):
        cleaned_data = super().clean()

        # Clean remaining string fields
        for field, value in cleaned_data.items():
            if isinstance(value, str) and field not in [
                'boy_full_name', 'girl_full_name', 'boy_birth_place', 'girl_birth_place'
            ]:
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        # Convert to 24-hour format for validation
        try:
            boy_hour_24 = self.convert_to_24_hour(
                cleaned_data.get("boy_hours"), cleaned_data.get("boy_time_type")
            )
            datetime(
                cleaned_data.get("boy_years"),
                cleaned_data.get("boy_months"),
                cleaned_data.get("boy_days"),
                boy_hour_24,
                cleaned_data.get("boy_minutes"),
                cleaned_data.get("boy_seconds")
            )
        except (TypeError, ValueError):
            raise forms.ValidationError("Invalid birth date/time for boy.")

        try:
            girl_hour_24 = self.convert_to_24_hour(
                cleaned_data.get("girl_hours"), cleaned_data.get("girl_time_type")
            )
            datetime(
                cleaned_data.get("girl_years"),
                cleaned_data.get("girl_months"),
                cleaned_data.get("girl_days"),
                girl_hour_24,
                cleaned_data.get("girl_minutes"),
                cleaned_data.get("girl_seconds")
            )
        except (TypeError, ValueError):
            raise forms.ValidationError("Invalid birth date/time for girl.")

        if cleaned_data.get("is_accepted_terms") != True:
            self.add_error("is_accepted_terms", "Please accept the terms and conditions.")

        return cleaned_data
