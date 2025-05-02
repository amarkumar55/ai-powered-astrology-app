from django.db import models
from dasha.models import BirthDetails
# Create your models here.

class KundliMatching(models.Model):
    boy_birth = models.ForeignKey(
        BirthDetails,
        on_delete=models.CASCADE,
        related_name='as_boy'
    )
    girl_birth = models.ForeignKey(
        BirthDetails,
        on_delete=models.CASCADE,
        related_name='as_girl'
    )
    varna_score = models.IntegerField()
    vasha_score = models.IntegerField()
    tara_score = models.IntegerField()
    yoni_score = models.IntegerField()
    graha_maitry_score = models.IntegerField()
    gana_score = models.IntegerField()
    bhakoot_score = models.IntegerField()
    nadi_score = models.IntegerField()
