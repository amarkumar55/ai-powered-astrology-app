from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
# Create your models here.

User = get_user_model()

class UserPanchang(models.Model):

    alphabetic = RegexValidator(
        regex=r'^[a-zA-Z]*$',
        message='Field must contain only alphabetic characters.'
    )

    # required fields      
    first_name = models.CharField(max_length=30, blank=False, null=False, validators=[alphabetic])
    last_name = models.CharField(max_length=30,  blank=False, null=False, validators=[alphabetic])
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_of_birth = models.DateField()
    time_of_birth = models.TimeField()
    place = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    tithi = models.CharField(max_length=50, null=False, blank=False)
    nakshatra = models.CharField(max_length=50, null=False, blank=False)
    yoga = models.CharField(max_length=50, null=False, blank=False)
    karana = models.CharField(max_length=50, null=False, blank=False)
    vara = models.CharField(max_length=50, null=False, blank=False)
    sunrise = models.TimeField()
    sunset = models.TimeField()
    rahu_kaal = models.CharField(max_length=50)
    gulika_kaal = models.CharField(max_length=50)
    yamaganda = models.CharField(max_length=50)
    abhijit_muhurat = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panchang for {self.name} on {self.date_of_birth}"
    

class Panchang(models.Model):
     
    date = models.DateField()
    tithi = models.CharField(max_length=50)
    vara = models.CharField(max_length=50)
    nakshatra = models.CharField(max_length=50)
    yoga = models.CharField(max_length=50)
    karana = models.CharField(max_length=50)
    sunrise = models.TimeField()
    sunset = models.TimeField()
    rahu_kaal = models.CharField(max_length=50)
    gulika_kaal = models.CharField(max_length=50)
    yamaganda = models.CharField(max_length=50)
    abhijit_muhurat = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panchang for {self.date}"
