from django.db import models
from dasha.models import BirthDetails
# Create your models here.

class Location(models.Model):
    place =  models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)


class KundliReport(models.Model):
    name = models.CharField(max_length=100,  blank=True, null=True,default='')
    place = models.CharField(max_length=200,  blank=True, null=True,default='')
    birth_details = models.ForeignKey(BirthDetails, on_delete=models.CASCADE) 
    ascendant = models.CharField(max_length=50)
    asc_deg = models.FloatField(max_length=20)
    asc_sign = models.CharField(max_length=50)
    birth_sign = models.CharField(max_length=50)
    lagna_chart = models.JSONField()
    chart_url = models.CharField(max_length=200, blank=True, null=True , default='')
    nakshatra= models.CharField(max_length=150, blank=True, null=True,default='')
    ganra = models.CharField(max_length=10, blank=True, null=True,default='')
    nadi  = models.CharField(max_length=15, blank=True, null=True,default='')
    yoni  = models.CharField(max_length=10, blank=True, null=True,default='')
    varna = models.CharField(max_length=15, blank=True, null=True,default='')
    houses = models.JSONField()
    planet_positions = models.JSONField()
    planets_longitudes = models.JSONField()
    planet_house_map = models.JSONField()
    sade_sati_result = models.JSONField()
    sade_sati_phases = models.JSONField()
    kundli_data = models.JSONField()
    manglik_dosha = models.BooleanField()
    kaal_sarp_dosha = models.BooleanField()
    mahapurush_yogas = models.JSONField()
    gaja_kesari_yoga = models.BooleanField()
    budha_aditya_yoga = models.BooleanField()
    pitra_dosha = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    