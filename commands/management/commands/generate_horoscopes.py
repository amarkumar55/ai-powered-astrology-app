from django.core.management.base import BaseCommand
from datetime import date
from utlity.horoscope import generate_daily_horoscope, generate_weekly_horoscope, generate_monthly_horoscope, generate_yearly_horoscope

class Command(BaseCommand):
    
    help = "Generate daily and weekly horoscopes"

    def handle(self, *args, **kwargs):
        today = date.today()
        generate_daily_horoscope()

        if today.weekday() == 0:  # Monday
            generate_weekly_horoscope()

        if today.day == 1:
            generate_monthly_horoscope()

        if today.month == 1 and today.day == 1:
            generate_yearly_horoscope()

        self.stdout.write(self.style.SUCCESS("Horoscopes generated successfully!"))