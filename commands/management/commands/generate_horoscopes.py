from django.core.management.base import BaseCommand
from utlity.horoscope import generate_daily_horoscope, generate_weekly_horoscope

class Command(BaseCommand):
    
    help = "Generate daily and weekly horoscopes"

    def handle(self, *args, **kwargs):
        generate_daily_horoscope()
        generate_weekly_horoscope()
        self.stdout.write(self.style.SUCCESS("Horoscopes generated successfully!"))
