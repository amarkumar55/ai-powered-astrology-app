from django.db import models
from dasha.models import BirthDetails
from home.models import TimeStampMixin
# Create your models here.

class KundliMatching(TimeStampMixin):
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

    class Meta:
        app_label = 'astrology'
    
    def __str__(self):
        return f"Kundli Matching: {self.boy_birth} & {self.girl_birth}"
    
