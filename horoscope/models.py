from django.db import models
from datetime import datetime
    

class Horoscope(models.Model):
    sign = models.CharField(max_length=50)
    date = models.DateField(default=datetime.now)
    type = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly')])
    prediction = models.TextField()

    def __str__(self):
        return f"{self.sign} - {self.type.capitalize()} Horoscope ({self.date})"
