import os
import json
import pdfkit
import requests
import logging
from .forms import KundliForm
from django.views import View
from datetime import date, time
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.timezone import now
from utlity.helper import store_activity
from .models import Location, KundliReport
from subscription.forms import CheckoutForm
from subscription.utlity import kundli_price
from django.shortcuts import render, redirect
from kundli.data import get_planet_descriptions
from dasha.models import AntarDasha, DashaEffect
from django_ratelimit.decorators import ratelimit
from dasha.models import BirthDetails,MoonPosition
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from utlity.dasha_antradasha import calculate_moon_longitude
from utlity.panchag import get_nakshatra_title, calculate_nakshatra
from utlity.compatibility import get_gan, get_nadi, get_yogi, get_varna
from utlity.kundli import gaja_ksesari_yoga,budha_aditya_yoga,check_pitra_dosha, get_houses
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic
from utlity.kundli import get_planet_positions, get_lagna,detect_panch_mahapurush_yogas,check_kaal_sarp_dosha,sade_sati_phases
from utlity.kundli import map_planets_to_houses,calculate_ascendant,sade_sati_check,get_rising_sign,get_planetary_longitudes,build_kundli_data
from utlity.kundli import generate_lagna_chart,check_manglik_dosha,clean_lagna_chart,clean_chart_data,generate_kundli_svg_and_return_url
from utlity.dasha_antradasha import (
    calculate_dasha,
    calculate_antar_dashas,
    calculate_moon_longitude,
    generate_vimshottari_dasha
)

APP_BASE_URL = os.environ.get('APP_BASE_URL')
@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True), name='dispatch')
class KundliPreditionView(View):
    template_name = "kundli/index.html"

    def get(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha,
        })
        return render(request, self.template_name, context)

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:

                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                days = form.cleaned_data.get("days")
                months = form.cleaned_data.get("months")
                years = form.cleaned_data.get("years")
                hours = form.cleaned_data.get("hours")
                minutes = form.cleaned_data.get("minutes")  # Fixed field reference
                seconds = form.cleaned_data.get("seconds")  # Fixed field reference
                place = form.cleaned_data.get("place")
                time_type = form.cleaned_data.get("time_format")
                birth_date = date(years, months, days)
                birth_time = time(hours, minutes, seconds)
                latitude = form.cleaned_data.get("latitude")
                longitude = form.cleaned_data.get("longitude")

        
                if time_type.lower() == "pm" and hours != 12:
                    hours += 12
                elif time_type.lower() == "am" and hours == 12:
                    hours = 0

                lat = round(latitude, 6)
                lon = round(longitude, 6)

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

                global moon_details
              
                if  birth_details:
                    moon_details = MoonPosition.objects.filter(birth_details=birth_details).first()
                    if not moon_details:
                        moon_longitude = calculate_moon_longitude(latitude, longitude, years, months, days, hours, minutes, seconds)
                        nakshatra = calculate_nakshatra(moon_longitude)
                        moon_details = MoonPosition.objects.create(
                            birth_details=birth_details,
                            moon_longitude=moon_longitude,
                            nakshatra=nakshatra
                        )

                kundli_details = KundliReport.objects.filter(birth_details=birth_details).first()

                if not kundli_details:
                    planet_positions = get_planet_positions(years, months, days, hours, months, seconds, latitude, longitude)
                    planet_positions_data = {k: float(v) for k, v in planet_positions.items()}
                    lagna = get_lagna(years, months, days, hours, months, seconds, latitude, longitude)
                    lagna_rashi = get_rising_sign(lagna)
                    houses = get_houses(lagna)
                    planets_longitudes = get_planetary_longitudes(years, months, days, hours, months, seconds, latitude, longitude)
                    planet_longitudes_data = {k: float(v) for k, v in planets_longitudes.items()}
                    planet_house_map = map_planets_to_houses(planets_longitudes, houses)
                    asc_deg = calculate_ascendant(years, months, days, hours, months, seconds, latitude, longitude)
                    asc_sign = get_rising_sign(asc_deg)
                    birth_sign = get_rising_sign(moon_details.moon_longitude)
                    sade_sati_result = sade_sati_check(moon_details.moon_longitude)
                    sade_phase = sade_sati_phases(moon_details.moon_longitude,birth_date)
                    mahapurush_yogas = detect_panch_mahapurush_yogas(planet_house_map, houses)
                    manglik_dosha = check_manglik_dosha(planet_positions_data)
                    kaal_sarp_dosha = check_kaal_sarp_dosha(planet_longitudes_data)
                    gaja_yoga   = gaja_ksesari_yoga(planet_house_map)
                    budha_yoga = budha_aditya_yoga(planet_house_map)
                    kundli_data = build_kundli_data(planet_positions_data, houses)
                    pirta_dosha  = check_pitra_dosha(kundli_data)
                    lagna_chart = clean_lagna_chart(generate_lagna_chart(planet_positions_data, lagna))
                    chart_url = APP_BASE_URL + generate_kundli_svg_and_return_url(lagna_chart),
                    nakshatra = int(moon_details.nakshatra) 

                    kundli_details = KundliReport.objects.create(
                        name = f"{first_name} {last_name}",
                        place = place, 
                        birth_details=birth_details,
                        ascendant = lagna_rashi,
                        asc_deg = asc_deg,
                        asc_sign = asc_sign,
                        birth_sign=birth_sign,
                        lagna_chart = json.dumps(lagna_chart),
                        houses = json.dumps(houses),
                        planet_positions = json.dumps(planet_positions_data),
                        planets_longitudes = json.dumps(planet_longitudes_data),
                        planet_house_map = json.dumps(planet_house_map),
                        sade_sati_result = json.dumps(sade_sati_result),
                        sade_sati_phases = json.dumps(sade_phase),
                        manglik_dosha = manglik_dosha,
                        kaal_sarp_dosha = kaal_sarp_dosha,
                        mahapurush_yogas = json.dumps(mahapurush_yogas),
                        gaja_kesari_yoga = gaja_yoga,
                        budha_aditya_yoga = budha_yoga,
                        pitra_dosha = pirta_dosha,
                        kundli_data = kundli_data,
                        chart_url = chart_url,
                        nakshatra= get_nakshatra_title(nakshatra),
                        ganra = get_gan(nakshatra),
                        nadi  = get_nadi(nakshatra),
                        yoni  = get_yogi(nakshatra),
                        varna = get_varna(nakshatra),
                    )


                reset_failed_attempts(request)

                if request.user.is_authenticated:
                   store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", None)
                                    
                messages.success(request, "Your Personalized Kundli prediction is generated.")

                return render(request, self.template_name, {
                    "form": form,
                    "is_report_generate": True,
                    "birth_date": birth_date,
                    "birth_time" : birth_time,
                    "kundli":kundli_details,
                    "sade_sati_result": json.loads(kundli_details.sade_sati_result),
                    "sade_sati_phases": json.loads(kundli_details.sade_sati_phases),
                    "manglik_dosha": kundli_details.manglik_dosha,
                    "kaal_sarp_dosha":kundli_details.kaal_sarp_dosha,
                    "mahapurush_yogas":json.loads(kundli_details.mahapurush_yogas),
                    "gaja_kesari_yoga":kundli_details.gaja_kesari_yoga,
                    "budha_aditya_yoga":kundli_details.budha_aditya_yoga,
                    "pitra_dosha":kundli_details.pitra_dosha,
                    "kundli_data":clean_chart_data(kundli_details.kundli_data) 
                })

            except Exception as e:
                increment_failed_attempts(request)
                send_error_log(e)
                messages.error(request, "Something went wrong while processing your request.")

        else:
            increment_failed_attempts(request)
            for field, errors in form.errors.items():
                for error in errors:
                    logging.error(f"{field}: {error}")
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha
        })
        return render(request, self.template_name, context)



@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='30/m', method='POST', block=True), name='dispatch')
class KundliPremiumView(View):
    template_name = "kundli/index.html"

    def get(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(show_captcha=show_captcha)

        context.update({
            "form": form,
            "show_captcha": show_captcha,
            "is_premium" : True
        })
        return render(request, self.template_name, context)

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = KundliForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:

                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                days = form.cleaned_data.get("days")
                months = form.cleaned_data.get("months")
                years = form.cleaned_data.get("years")
                hours = form.cleaned_data.get("hours")
                minutes = form.cleaned_data.get("minutes")  # Fixed field reference
                seconds = form.cleaned_data.get("seconds")  # Fixed field reference
                place = form.cleaned_data.get("place")
                time_type = form.cleaned_data.get("time_format")
                birth_date = date(years, months, days)
                birth_time = time(hours, minutes, seconds)
                latitude = form.cleaned_data.get("latitude")
                longitude = form.cleaned_data.get("longitude")

        
                if time_type.lower() == "pm" and hours != 12:
                    hours += 12
                elif time_type.lower() == "am" and hours == 12:
                    hours = 0

                lat = round(latitude, 6)
                lon = round(longitude, 6)

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

                global moon_details
              
                if  birth_details:
                    moon_details = MoonPosition.objects.filter(birth_details=birth_details).first()
                    if not moon_details:
                        moon_longitude = calculate_moon_longitude(latitude, longitude, years, months, days, hours, minutes, seconds)
                        nakshatra = calculate_nakshatra(moon_longitude)
                        moon_details = MoonPosition.objects.create(
                            birth_details=birth_details,
                            moon_longitude=moon_longitude,
                            nakshatra=nakshatra
                        )

                kundli_details = KundliReport.objects.filter(birth_details=birth_details).first()

                if not kundli_details:
                    planet_positions = get_planet_positions(years, months, days, hours, months, seconds, latitude, longitude)
                    planet_positions_data = {k: float(v) for k, v in planet_positions.items()}
                    lagna = get_lagna(years, months, days, hours, months, seconds, latitude, longitude)
                    lagna_rashi = get_rising_sign(lagna)
                    houses = get_houses(lagna)
                    planets_longitudes = get_planetary_longitudes(years, months, days, hours, months, seconds, latitude, longitude)
                    planet_longitudes_data = {k: float(v) for k, v in planets_longitudes.items()}
                    planet_house_map = map_planets_to_houses(planets_longitudes, houses)
                    asc_deg = calculate_ascendant(years, months, days, hours, months, seconds, latitude, longitude)
                    asc_sign = get_rising_sign(asc_deg)
                    birth_sign = get_rising_sign(moon_details.moon_longitude)
                    sade_sati_result = sade_sati_check(moon_details.moon_longitude)
                    sade_phase = sade_sati_phases(moon_details.moon_longitude,birth_date)
                    mahapurush_yogas = detect_panch_mahapurush_yogas(planet_house_map, houses)
                    manglik_dosha = check_manglik_dosha(planet_positions_data)
                    kaal_sarp_dosha = check_kaal_sarp_dosha(planet_longitudes_data)
                    gaja_yoga   = gaja_ksesari_yoga(planet_house_map)
                    budha_yoga = budha_aditya_yoga(planet_house_map)
                    kundli_data = build_kundli_data(planet_positions_data, houses)
                    pirta_dosha  = check_pitra_dosha(kundli_data)
                    lagna_chart = clean_lagna_chart(generate_lagna_chart(planet_positions_data, lagna))
                    chart_url = APP_BASE_URL+generate_kundli_svg_and_return_url(lagna_chart),
                    nakshatra = int(moon_details.nakshatra) 
                

                    kundli_details = KundliReport.objects.create(
                        name = f"{first_name} {last_name}",
                        place = place, 
                        birth_details=birth_details,
                        ascendant = lagna_rashi,
                        asc_deg = asc_deg,
                        asc_sign = asc_sign,
                        birth_sign=birth_sign,
                        lagna_chart = json.dumps(lagna_chart),
                        houses = json.dumps(houses),
                        planet_positions = json.dumps(planet_positions_data),
                        planets_longitudes = json.dumps(planet_longitudes_data),
                        planet_house_map = json.dumps(planet_house_map),
                        sade_sati_result = json.dumps(sade_sati_result),
                        sade_sati_phases = json.dumps(sade_phase),
                        manglik_dosha = manglik_dosha,
                        kaal_sarp_dosha = kaal_sarp_dosha,
                        mahapurush_yogas = json.dumps(mahapurush_yogas),
                        gaja_kesari_yoga = gaja_yoga,
                        budha_aditya_yoga = budha_yoga,
                        pitra_dosha = pirta_dosha,
                        kundli_data = kundli_data,
                        chart_url = chart_url,
                        nakshatra= get_nakshatra_title(nakshatra),
                        ganra = get_gan(nakshatra),
                        nadi  = get_nadi(nakshatra),
                        yoni  = get_yogi(nakshatra),
                        varna = get_varna(nakshatra),
                    )

    
                self.request.session['kundli_id'] = kundli_details.id
         
                reset_failed_attempts(request)
                messages.success(request, "Your Personalized Kundli prediction is generated. Please complete payment to download")
                return redirect('kundli.premium_payment')
            
            except Exception as e:
                increment_failed_attempts(request)
                send_error_log(e)
                messages.error(request, "Something went wrong while processing your request.")

        else:
            increment_failed_attempts(request)
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({
            "form": form,
            "show_captcha": show_captcha
        })
        return render(request, self.template_name, context)



@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True), name='dispatch')
class KundliPaymentProcessView(View):
    template_name = "kundli/checkout.html"
   
    def get(self, request):
        if not self.request.session.get('kundli_id'):
           messages.error(request,"Invalid request, Please contact us")
           return redirect('kundli.premium_anaysis')

        show_captcha, context = handle_captcha_logic(request, {})
        form = CheckoutForm(show_captcha=show_captcha)
        price = os.environ.get('KUNDLI_PREMIMUM_PRICE')
        data = kundli_price(price)

        context.update({
            "form": form,
            "show_captcha": show_captcha,
            "price":price,
            "gst":data['gst'],
            "total":data['total'],
            "countries":data['countries'],
        })

        return render(request, self.template_name, context)  
    
@method_decorator(login_required, name='dispatch')    
@method_decorator(
    ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True), 
    name='dispatch'
)
class KundliPremiumDownloadView(View):
    template_name = "kundli/premium.html"

    def _get_kundli_context(self):
        if not self.request.session.get('kundli_id'):
           messages.error(self.request,"Invalid request, Please contact us")
           return redirect('kundli.premium_anaysis')
        
        kundli_details = KundliReport.objects.filter(id=self.request.session.get('kundli_id')).first()
        
        if not kundli_details:
           messages.error(self.request,"Invalid request, Please contact us")
           return redirect('kundli.premium_anaysis')

        birth_details = kundli_details.birth_details

        antar_dasha_details = AntarDasha.objects.filter(birth_details=birth_details)
        
        moon_details = MoonPosition.objects.filter(birth_details=birth_details).first()

        if not moon_details:
           messages.error(self.request,"Something Went Wrong!, you can download your kundli from kundli menu")
           return redirect('kundli.premium_anaysis')

        if not antar_dasha_details.exists():
            starting_planet = calculate_dasha(moon_details.moon_longitude)
            dasha_sequence = generate_vimshottari_dasha(birth_details.birth_date, starting_planet)
            for planet_name, start_date, _ in dasha_sequence:
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
        kundli_data = clean_chart_data(kundli_details.kundli_data)
        planet_descriptions = get_planet_descriptions(kundli_data)

        context = {
            "birth_date": birth_details.birth_date,
            "birth_time": birth_details.birth_time,
            "kundli": kundli_details,
            "sade_sati_result": json.loads(kundli_details.sade_sati_result),
            "sade_sati_phases": json.loads(kundli_details.sade_sati_phases),
            "manglik_dosha": kundli_details.manglik_dosha,
            "kaal_sarp_dosha": kundli_details.kaal_sarp_dosha,
            "mahapurush_yogas": json.loads(kundli_details.mahapurush_yogas),
            "gaja_kesari_yoga": kundli_details.gaja_kesari_yoga,
            "budha_aditya_yoga": kundli_details.budha_aditya_yoga,
            "pitra_dosha": kundli_details.pitra_dosha,
            "kundli_data": kundli_data,
            "antar_dasha_details": antar_dasha_details,
            "current_dasha_affect": current_dasha_affect,
            "planet_descriptions": planet_descriptions
        }
        return context, None

    def get(self, request):
        context, error = self._get_kundli_context()
        if error:
            messages.error(request, error)
            return redirect('kundli.premium_anaysis') 
        return render(request, self.template_name, context)

    def post(self, request):
        context, error = self._get_kundli_context()
        if error:
            messages.error(request, error)
            return redirect('kundli.premium_anaysis')

        html = render_to_string("kundli/kundli_pdf.html", context) 
        pdf = pdfkit.from_string(html, False, configuration=settings.PDFKIT_CONFIG,options={"enable-local-file-access": ""})
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="kundli_report.pdf"'
        return response

@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key='user_or_ip', rate='5/m', block=True), name='dispatch')
class SearchLocationView(View):

    def get(self, request):
        query = request.GET.get("place", "").strip()
        location_api_key = os.environ.get('LOCATIONIQ_API_KEY')

        if not query or not location_api_key:
            return JsonResponse({"error": "No place provided"}, status=400)

        # Check local DB/cache
        exist_in_cache = Location.objects.filter(place__icontains=query).values("place", "latitude", "longitude")

        if exist_in_cache.exists():
            return JsonResponse(list(exist_in_cache), safe=False)

        # External API call
        api_url = f"https://us1.locationiq.com/v1/search.php?key={location_api_key}&q={query}&format=json"

        try:
            response = requests.get(api_url)
            data = response.json()

            if not data:
                return JsonResponse({"error": "Location not found"}, status=404)

            locations = []
            for item in data:
                # Avoid duplicates (adjusted logic)
                Location.objects.get_or_create(
                    place=item.get("display_name"),
                    defaults={
                        "latitude": round(float(item.get("lat")), 6),
                        "longitude": round(float(item.get("lon")), 6),
                    }
                )
                locations.append({
                    "place": item.get("display_name"),
                    "latitude": item.get("lat"),
                    "longitude": item.get("lon"),
                })

            return JsonResponse(locations, safe=False)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)
