from django import forms
from django.contrib.auth import get_user_model
from .models import Vendor, ChatRoom, Message, VendorAvailability
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class VendorRegistrationForm(forms.ModelForm):
    """Form for vendors to register as consultants"""
    
    class Meta:
        model = Vendor
        fields = [
            'specialization', 'experience_years', 'bio', 'hourly_rate',
            'languages', 'consultation_hours', 'profile_image', 'certificates'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
            'languages': forms.TextInput(attrs={'placeholder': 'English, Hindi, etc.'}),
            'consultation_hours': forms.TextInput(attrs={'placeholder': '{"monday": ["09:00-17:00"], "tuesday": ["09:00-17:00"]}'}),
            'hourly_rate': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

class VendorAvailabilityForm(forms.ModelForm):
    """Form for vendors to set their availability"""
    
    class Meta:
        model = VendorAvailability
        fields = ['day_of_week', 'start_time', 'end_time', 'is_available']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data

class ChatRoomForm(forms.ModelForm):
    """Form for creating a new chat room"""
    
    class Meta:
        model = ChatRoom
        fields = ['vendor']
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show available vendors
            self.fields['vendor'].queryset = Vendor.objects.filter(
                status='approved',
                is_available=True
            ).exclude(user=user)

class MessageForm(forms.ModelForm):
    """Form for sending messages in chat"""
    
    class Meta:
        model = Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Type your message...',
                'class': 'form-textarea'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*,.pdf,.doc,.docx,.txt'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 
                           'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/plain']
            if file.content_type not in allowed_types:
                raise forms.ValidationError("File type not allowed.")
        
        return file

class VendorSearchForm(forms.Form):
    """Form for searching vendors"""
    
    specialization = forms.ChoiceField(
        choices=[('', 'All Specializations')] + Vendor.SPECIALIZATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    max_rate = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max hourly rate',
            'class': 'form-input'
        })
    )
    
    rating_min = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min rating',
            'class': 'form-input'
        })
    )
    
    available_now = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

class VendorReviewForm(forms.Form):
    """Form for reviewing vendors after chat sessions"""
    
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'min': '1',
            'max': '5',
            'class': 'form-input'
        })
    )
    
    review = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Share your experience with this consultant...',
            'class': 'form-textarea'
        })
    )

class VendorProfileUpdateForm(forms.ModelForm):
    """Form for vendors to update their profile"""
    
    class Meta:
        model = Vendor
        fields = [
            'specialization', 'bio', 'hourly_rate', 'languages',
            'consultation_hours', 'profile_image', 'supports_video_call'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
            'languages': forms.TextInput(attrs={'placeholder': 'English, Hindi, etc.'}),
            'consultation_hours': forms.TextInput(attrs={'placeholder': '{"monday": ["09:00-17:00"]}'}),
            'hourly_rate': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

class PaymentForm(forms.Form):
    """Form for payment processing"""
    
    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay (Credit/Debit Cards, UPI)'),
        ('stripe', 'Stripe (International Cards)'),
        ('paypal', 'PayPal'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.HiddenInput()
    )

class VideoCallForm(forms.Form):
    """Form for initiating video calls"""
    
    call_type = forms.ChoiceField(
        choices=[
            ('audio', 'Audio Call'),
            ('video', 'Video Call')
        ],
        initial='video',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'}) 