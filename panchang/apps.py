from django.apps import AppConfig
from utlity.ephemeris_loader import preload_ephemeris

class PanchangConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'panchang'
    def ready(self):
        preload_ephemeris()