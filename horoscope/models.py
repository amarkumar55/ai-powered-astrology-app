from django.db import models
from django.utils import timezone
from home.models import TimeStampMixin
    
class Horoscope(TimeStampMixin):
   
    sign = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly')])
    general = models.TextField(blank=True)
    love = models.TextField(blank=True)
    career = models.TextField(blank=True)
    health = models.TextField(blank=True)
    finance = models.TextField(blank=True) 

    def __str__(self):
        return f"{self.sign} - {self.type.capitalize()} Horoscope ({self.date})"
    
    class Meta:
        app_label = 'astrology'
