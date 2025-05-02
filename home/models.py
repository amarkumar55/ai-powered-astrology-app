import bleach
from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContactQuery(TimeStampMixin):
    alphabetic = RegexValidator(
        regex=r'^[a-zA-Z ]*$',  # Allows spaces in names
        message='Field must contain only alphabetic characters and spaces.'
    )
    
    full_name = models.CharField(
        max_length=30, 
        blank=False, 
        null=False, 
        validators=[alphabetic], 
        verbose_name="Full Name"
    )
    
    email = models.EmailField(
        blank=False, 
        null=False, 
        verbose_name="Email Address"
    )
    
    message = models.TextField(
        blank=False, 
        null=False, 
        verbose_name="Message"
    )

    def save(self, *args, **kwargs):
        self.full_name = bleach.clean(self.full_name, tags=[], strip=True)
        self.email = bleach.clean(self.email, tags=[], strip=True)
        self.message = bleach.clean(self.message, tags=[], strip=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.email}"


