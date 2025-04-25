from django.core.management.base import BaseCommand
from django.utils.timezone import now
from panchang.models import Panchang
from utlity.panchag import calculate_panchang
from datetime import datetime, date

class Command(BaseCommand):
    
    help = "Generate daily panchang"
    
    # Convert time strings to time objects 
    def parse_time(time_str):
        try:
            # Ensure the time_str is a string before parsing
            if isinstance(time_str, str):
                return datetime.strptime(time_str, '%H:%M:%S').time()
            return time_str  # If it's already a time object
        except ValueError:
            return None
    
    def handle(self, *args, **kwargs):
        today = date.today()
        latitue = "22.5744 N"
        longtiute = "88.3629 E"
        panchang = calculate_panchang(latitue, longtiute, now().year, now().month, now().day, now().hour, now().minute, now().second)

        # Example: Creating a dummy Panchang entry
        panchang = Panchang.objects.create(
            date=today.isoformat(), 
            tithi=panchang['tithi'],
            nakshatra=panchang['nakshatra'],
            yoga=panchang['yoga'],
            karana=panchang['karana'],
            vara=panchang['vara'],
            sunrise=panchang['sunrise'],
            sunset=panchang['sunset'],
            rahu_kaal=panchang['rahu_kaal'],
            gulika_kaal=panchang['gulika_kaal'],
            yamaganda=panchang['yamaganda'],
            abhijit_muhurat=panchang['abhijit_muhurat'],
        )
        self.stdout.write(self.style.SUCCESS("Panchag generated successfully!"))
