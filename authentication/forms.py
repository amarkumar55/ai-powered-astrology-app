import re
import bleach
from django import forms
from django.utils import timezone 
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm
from captcha.fields import CaptchaField, CaptchaTextInput
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'includes/captcha_custom.html'


class RegisterForm(forms.ModelForm):
    
    GENDER_CHOICES =( 
        ("Male", "Male"), 
        ("Female", "Female"), 
        ("Other", "Other"), 
    ) 
  
    first_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)
    last_name = forms.CharField(min_length=2, strip=True, max_length=30 , required=True)
    email = forms.EmailField(min_length=5,  max_length=100, required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    birth_date= forms.DateField(required=True)
    password = forms.CharField(
        min_length=8,
        error_messages={
            "min_length": "Password must be at least 8 characters long.",
        }
    )
    confirm_password = forms.CharField()
    is_accepted_terms=forms.CheckboxInput(check_test=True)
    captcha = CaptchaField(widget=CustomCaptchaTextInput)
    
    class Meta:
        model = User
        fields = ["email", "password", "confirm_password","birth_date", "first_name", "last_name","gender","is_accepted_terms"]

    
    def clean_email(self):
        email = self.cleaned_data.get("email")

        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Optional: prevent disposable email services
        disposable_domains = ["mailinator.com", "10minutemail.com", "tempmail.com"]
        domain = email.split('@')[-1]
        if domain.lower() in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return email

    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

        # If password doesn't match the pattern
        if not re.match(pattern, password):
            raise ValidationError(
                "Password must be at least 8 characters long, contain one uppercase, one lowercase, one number, and one special character."
            )

        return password
    

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get("confirm_password")
        
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

        # If password doesn't match the pattern
        if not re.match(pattern, confirm_password):
            raise ValidationError(
                "Password must be at least 8 characters long, contain one uppercase, one lowercase, one number, and one special character."
            )

        return confirm_password
        
    def clean(self):
        
        cleaned_data = super().clean()

        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        birth_date = cleaned_data.get("birth_date")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        is_accepted_terms = cleaned_data.get("is_accepted_terms")
       

        if not birth_date:
           self.add_error("birth_date", "Birth date is required.")

        if not re.fullmatch(r"^[A-Za-z]+$", first_name):
           self.add_error("first_name", "First name must contain only alphabets.")
           
        if not re.fullmatch(r"^[A-Za-z]+$", last_name):
           self.add_error("last_name", "Last name must contain only alphabets.")
    
        if password and confirm_password and password != confirm_password:
            self.add_error("password", "Password and confirm password not matched.")
        
        if birth_date and birth_date > timezone.now().date():
            self.add_error("birth_date", "Birth date cannot be a future date.")

        if is_accepted_terms and is_accepted_terms != True:
            self.add_error("is_accepted_terms", "Please accept term's and conditions.")

        return cleaned_data


class VerifyLoginOtp(forms.Form):
    otp = forms.CharField(required=True)

    def __init__(self, *args, request=None, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(*args, **kwargs)
        self.request = request  # Store request if needed

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)

    def clean(self):
        cleaned_data = super().clean()

        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)

        otp = cleaned_data.get('otp')

        if not otp:
            self.add_error("otp", "OTP is required.")
        else:
            if not re.match(r'^\d{6}$', otp):
                self.add_error("otp", "OTP must be a 6-digit number.")

        return cleaned_data

class VerifyOtpForm(forms.Form):
    email = forms.EmailField(min_length=5, max_length=100, required=True)
    otp = forms.CharField(required=True)

    def __init__(self, request=None, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(request=request, *args, **kwargs)

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.fullmatch(email):
            raise forms.ValidationError("Please enter a valid email address.")

        # Optional: prevent disposable email services
        disposable_domains = ["mailinator.com", "10minutemail.com", "tempmail.com"]
        domain = email.split('@')[-1]
        if domain.lower() in disposable_domains:
            raise forms.ValidationError("Please use a real, non-disposable email address.")

        return email

    def clean(self):
        cleaned_data = super().clean()

         # Sanitize all string inputs
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[field] = bleach.clean(value, tags=[], strip=True)


        email = cleaned_data.get('email')
        otp = cleaned_data.get('otp')


        # Email required check
        if not email:
            self.add_error("email", "Email is required.")
        else:
            # Validate email format with regex
            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_regex, email):
                self.add_error("email", "Enter a valid email address.")

        # OTP required check
        if not otp:
            self.add_error("otp", "OTP is required.")
        else:
            # Ensure it's a 6-digit number
            if not re.match(r'^\d{6}$', str(otp)):
                self.add_error("otp", "OTP must be a 6-digit number.")

        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(request=request, *args, **kwargs)

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)



class ResendVerificationForm(forms.Form):
    def __init__(self, request=None, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)
        super().__init__(*args, **kwargs)
        self.request = request

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        self.show_captcha = kwargs.pop('show_captcha', False)  # ✅ remove before calling super
        super().__init__(*args, **kwargs)

        if self.show_captcha:
            self.fields['captcha'] = CaptchaField(widget=CustomCaptchaTextInput)