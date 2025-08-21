import uuid
import json
import datetime
from django.core import serializers
from django.views import View
from django.shortcuts import render,redirect
from django.urls import reverse
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
        tag = request.GET.get('tag', '').strip()
        session_key = f'dasha_result_{tag}'
        data = request.session.get(session_key)
        is_report_generate = data is not None
        show_captcha, context = handle_captcha_logic(request, {})
        form = PanchangForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": is_report_generate,
            "show_captcha": show_captcha,
            "name": data.get("name") if data else "",
            "place": data.get("place") if data else "",
            "antar_dasha_details": json.loads(data.get("antar_dasha_details", "[]")) if data else [],
            "current_dasha_affect": json.loads(data.get("current_dasha_affect", "[]")) if data else []
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
                place = form.cleaned_data.get("place")
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

                lat = round(lat, 6)
                lon = round(lon, 6)

                birth_details = BirthDetails.objects.filter(
                        birth_date=birth_date,
                        birth_time=birth_time,
                        latitude__gte=lat - 0.000001,
                        latitude__lte=lat + 0.000001,
                        longitude__gte=lon - 0.000001,
                        longitude__lte=lon + 0.000001
                ).first()

                if not birth_details:
                    birth_details = BirthDetails.objects.create(
                        birth_date=birth_date,
                        birth_time=birth_time,
                        latitude=lat,
                        longitude=lon
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
                        planet_name, start_date, _ = dasha
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

                antar_dasha_serialized = serializers.serialize('json', antar_dasha_details)
                current_dasha_serialized = serializers.serialize('json', current_dasha_affect)

                data = {
                    "name": f"{first_name} {last_name}",
                    "place": place,
                    "antar_dasha_details": antar_dasha_serialized,
                    "current_dasha_affect": current_dasha_serialized
                }

                tag = uuid.uuid4().hex 
                request.session[f'dasha_result_{tag}'] = data

                reset_failed_attempts(request)
                if request.user.is_authenticated:
                   store_activity(self.request, form.cleaned_data.copy() , "generated dasha antar dasha predition", request.user)
                else:
                    store_activity(self.request, form.cleaned_data.copy() , "generated dasha antar dasha predition", None)

                messages.success(request, "Your Dasha and Antar Dasha prediction is generated.")

                return redirect(f"{reverse('dasha.index')}?tag={tag}")

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