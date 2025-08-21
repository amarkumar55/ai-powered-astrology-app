from django.db import models
from home.models import TimeStampMixin

# Common model to store shared birth details
class BirthDetails(TimeStampMixin):
    birth_date = models.DateField()
    birth_time = models.TimeField()
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        unique_together = ("birth_date", "birth_time", "latitude", "longitude")
        app_label = 'astrology'

    def __str__(self):
        return f"Birth: {self.birth_date} {self.birth_time} (Lat: {self.latitude}, Lon: {self.longitude})"

# AntarDasha model linked to birth details
class AntarDasha(TimeStampMixin):
    birth_details = models.ForeignKey(BirthDetails, on_delete=models.CASCADE)
    nakshatra = models.CharField(max_length=50)
    major_dasha = models.CharField(max_length=50)
    remaining_years = models.FloatField()
    antar_dasha_planet = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
  
    class Meta:
        app_label = 'astrology'
    def __str__(self):
        return f"{self.major_dasha} - {self.antar_dasha_planet} ({self.start_date} to {self.end_date})"

# PlanetaryPosition model linked to birth details
class PlanetaryPosition(TimeStampMixin):
    birth_details = models.ForeignKey(BirthDetails, on_delete=models.CASCADE)
    planet = models.CharField(max_length=50)
    speed = models.DecimalField(max_digits=8, decimal_places=4)
    nakshatra = models.CharField(max_length=50)
    rashi = models.CharField(max_length=50)

    class Meta:
        unique_together = ("birth_details", "planet")
        app_label = 'astrology'
    def __str__(self):
        return f"{self.planet} - {self.rashi} ({self.birth_details})"

# MoonPosition model linked to birth details
class MoonPosition(TimeStampMixin):
    birth_details = models.ForeignKey(BirthDetails, on_delete=models.CASCADE)
    moon_longitude = models.FloatField()
    nakshatra = models.CharField(max_length=50)

    def __str__(self):
        return f"Moon: {self.nakshatra} ({self.birth_details})"
    
    class Meta:
        app_label = 'astrology'

class DashaEffect(TimeStampMixin):
    mahadasha_planet = models.CharField(max_length=50)
    antar_dasha_planet = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    mahadasha_effect = models.TextField()
    antardasha_effect = models.TextField()
    combined_effect = models.TextField()

    class Meta:
        app_label = 'astrology'