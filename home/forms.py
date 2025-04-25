import re
import bleach
from django import forms
from .models import ContactQuery
from captcha.fields import CaptchaField, CaptchaTextInput

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'

class ContactForm(forms.ModelForm):
    captcha = CaptchaField(widget=CustomCaptchaTextInput)
    full_name = forms.CharField(
        min_length=2,
        strip=True,
        max_length=30,
        required=True,
        error_messages={"required": "Full name is required."}
    )
    email = forms.EmailField(
        min_length=5,
        max_length=100,
        required=True,
        error_messages={"required": "Email is required."}
    )
    message = forms.CharField(
        min_length=25,
        required=True,
        widget=forms.Textarea,
        error_messages={"required": "Message is required."}
    )

    class Meta:
        model = ContactQuery
        fields = ["full_name", "email", "message"]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Strong regex for email
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Block known disposable email domains
        disposable_domains = {"mailinator.com", "10minutemail.com", "tempmail.com"}
        domain = email.split('@')[-1].lower()
        if domain in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return email

    def clean(self):
        cleaned_data = super().clean()

        # Sanitize all user inputs
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value.strip(), tags=[], strip=True)

        full_name = cleaned_data.get('full_name')
        message = cleaned_data.get('message')

        # Full name: only alphabets and spaces
        if full_name and not re.fullmatch(r"^[A-Za-z\s]+$", full_name):
            self.add_error("full_name", "Full name must contain only alphabets and spaces.")

        # Message: limit to readable input (optional: loosen if supporting full messages)
        if message and not re.fullmatch(r"^[A-Za-z0-9\s.,!?'\"]+$", message):
            self.add_error("message", "Message must contain only letters, numbers, spaces, and basic punctuation.")

        return cleaned_data
