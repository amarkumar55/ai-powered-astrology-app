import datetime
from django.views import View
from django.shortcuts import render
from django.contrib import messages
from django.utils.timezone import now
from panchang.forms import PanchangForm
from utlity.helper import store_activity
from utlity.panchag import calculate_nakshatra
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .models import BirthDetails, MoonPosition, AntarDasha, DashaEffect
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic
from utlity.dasha_antradasha import (
    calculate_dasha,
    calculate_antar_dashas,
    calculate_moon_longitude,
    generate_vimshottari_dasha
)


@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class DashaAntarDashaView(View):
    template_name = "dasha/index.html"

    def get(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = PanchangForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha,
        })
        return render(request, self.template_name, context)

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = PanchangForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                days = form.cleaned_data.get("days")
                months = form.cleaned_data.get("months")
                years = form.cleaned_data.get("years")
                hours = form.cleaned_data.get("hours")
                minutes = form.cleaned_data.get("minutes")
                seconds = form.cleaned_data.get("seconds")
                time_type = form.cleaned_data.get("time_format")
                place = form.cleaned_data.get("place_of_birth")
                lat = form.cleaned_data.get("latitude")
                lon = form.cleaned_data.get("longitude")

                # Convert 12-hour to 24-hour time
                if time_type.lower() == "pm" and hours != 12:
                    hours += 12
                elif time_type.lower() == "am" and hours == 12:
                    hours = 0

                # Validate and create date/time objects
                try:
                    birth_date = datetime.date(years, months, days)
                    birth_time = datetime.time(hours, minutes, seconds)
                except ValueError:
                    messages.error(request, "Invalid date or time provided.")
                    context.update({"form": form, "is_report_generate": False})
                    return render(request, self.template_name, context)

                birth_details, _ = BirthDetails.objects.get_or_create(
                    birth_date=birth_date,
                    birth_time=birth_time,
                    latitude__startswith=str(round(lat, 6)),
                    longitude__startswith=str(round(lon, 6))
                )

                moon_details = MoonPosition.objects.filter(birth_details=birth_details).first()

                if not moon_details:
                    moon_longitude = calculate_moon_longitude(lat, lon, years, months, days, hours, minutes, seconds)
                    nakshatra = calculate_nakshatra(moon_longitude)
                    moon_details = MoonPosition.objects.create(
                        birth_details=birth_details,
                        moon_longitude=moon_longitude,
                        nakshatra=nakshatra
                    )

                antar_dasha_details = AntarDasha.objects.filter(birth_details=birth_details)

                if antar_dasha_details.count() == 0:
                    starting_planet = calculate_dasha(moon_details.moon_longitude)
                    dasha_sequence = generate_vimshottari_dasha(birth_date, starting_planet)
                    for dasha in dasha_sequence:
                        planet_name, start_date = dasha
                        calculate_antar_dashas(
                            birth_details=birth_details,
                            mahadasha_start_date=str(start_date),
                            mahadasha_planet=planet_name,
                            nakshatra=moon_details.nakshatra,
                            remaining_years=0
                        )
                    antar_dasha_details = AntarDasha.objects.filter(birth_details=birth_details)

                current_time = now()
                current_dasha_affect = DashaEffect.objects.filter(
                    start_date__lte=current_time,
                    end_date__gte=current_time
                )

                reset_failed_attempts(request)
                store_activity(self.request, form.cleaned_data.copy() , "generated dasha antar dasha predition", request.user)
                messages.success(request, "Your Dasha and Antar Dasha prediction is generated.")

                return render(request, self.template_name, {
                    "form": form,
                    "name": f"{first_name} {last_name}",
                    "place": place,
                    "is_report_generate": True,
                    "antar_dasha_details": antar_dasha_details,
                    "current_dasha_affect": current_dasha_affect
                })

            except Exception as e:
                increment_failed_attempts(request)
                send_error_log(e)
                messages.error(request, "Something went wrong while processing your request.")

        else:
            increment_failed_attempts(request)
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha
        })
        return render(request, self.template_name, context)