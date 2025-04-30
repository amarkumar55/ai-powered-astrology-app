import os
import json
import requests
from .forms import KundliForm
from django.views import View
from datetime import date, time
from django.contrib import messages
from django.http import JsonResponse
from utlity.helper import store_activity
from .models import Location, KundliReport
from subscription.forms import CheckoutForm
from subscription.utlity import kundli_price
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit
from dasha.models import BirthDetails,MoonPosition
from django.utils.decorators import method_decorator
from utlity.dasha_antradasha import calculate_moon_longitude
from utlity.panchag import get_nakshatra_title, calculate_nakshatra
from utlity.compatibility import get_gan, get_nadi, get_yogi, get_varna
from utlity.kundli import gaja_ksesari_yoga,budha_aditya_yoga,check_pitra_dosha, get_houses
from authentication.utlity import send_error_log, reset_failed_attempts, increment_failed_attempts,handle_captcha_logic
from utlity.kundli import get_planet_positions, get_lagna,detect_panch_mahapurush_yogas,check_kaal_sarp_dosha,sade_sati_phases
from utlity.kundli import map_planets_to_houses,calculate_ascendant,sade_sati_check,get_rising_sign,get_planetary_longitudes,build_kundli_data
from utlity.kundli import generate_lagna_chart,check_manglik_dosha,clean_lagna_chart,clean_chart_data,generate_kundli_svg_and_return_url


@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
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
                    lagna_chart = generate_lagna_chart(planet_positions_data, lagna)
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
                

                    kundli_details = KundliReport.objects.create(
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
                            kundli_data = kundli_data
                    )


                reset_failed_attempts(request)

                if request.user.is_authenticated:
                   store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", None)
                    
                kundli_details = KundliReport.objects.filter(birth_details=birth_details).first()
                moon_details = MoonPosition.objects.filter(birth_details=birth_details).first()
          
                nakshatra = int(moon_details.nakshatra)
                lagna_chart = clean_lagna_chart(json.loads(kundli_details.lagna_chart))

                messages.success(request, "Your Personalized Kundli prediction is generated.")

                return render(request, self.template_name, {
                    "form": form,
                    "is_report_generate": True,
                    "name" : f"{first_name} {last_name}",
                    "birth_date": birth_date,
                    "birth_time" : birth_time,
                    "birth_place": place,
                    "kundli":kundli_details,
                    "nakshatra" : get_nakshatra_title(nakshatra),
                    "lagna_chart":clean_lagna_chart(json.loads(kundli_details.lagna_chart)),
                    "chart_url" : generate_kundli_svg_and_return_url(lagna_chart),
                    "ganra":get_gan(nakshatra),
                    "nadi": get_nadi(nakshatra),
                    "yoni": get_yogi(nakshatra),
                    "varna":get_varna(nakshatra),
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
            messages.error(request, "Unable to process your request currently. Please check your details.")

        context.update({
            "form": form,
            "is_report_generate": False,
            "show_captcha": show_captcha
        })
        return render(request, self.template_name, context)



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
                    lagna_chart = generate_lagna_chart(planet_positions_data, lagna)
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
                

                    kundli_details = KundliReport.objects.create(
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
                            kundli_data = kundli_data
                    )

                user = request.user 

                self.request.session['user_id'] = user.pk
                self.request.session['user_name'] = f"{first_name}  {last_name}"
                self.request.session['kundli_id'] = kundli_details.id
                self.request.session['place'] = place
    
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



@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class KundliPaymentProcessView(View):
    template_name = "kundli/payment.html"
   
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

    def post(self, request):
        show_captcha, context = handle_captcha_logic(request, {})
        form = CheckoutForm(request.POST, show_captcha=show_captcha)

        if form.is_valid():
            try:                
                reset_failed_attempts(request)
                
                if request.user.is_authenticated:
                   store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", request.user)
                else:
                    store_activity(request, form.cleaned_data.copy(), "kundli_predition_generate", None)
                    
            
                messages.success(request, "Your Personalized Kundli prediction is generated.")
               
                userId = self.request.session.get('user_id')
                user_name = self.request.session.get('user_name')
                kundlid = self.request.session.get('kundli_id')
                place = self.request.session.get('place')
         
                if not kundlid or not userId or user_name:
                   messages.error(request, "Invalid request. Please contact with team with your payment Id")

            
                kundli_details = KundliReport.objects.filter(id=kundlid).first()

                birth_details = BirthDetails.objects.get(id=kundli_details.birth_details)

                if not kundli_details:
                   messages.error(request, "Invalid request. Please contact with team with your payment Id")
             
                moon_details = MoonPosition.objects.filter(birth_details=kundli_details.birth_details).first()

                if not moon_details:
                   messages.error(request, "Invalid request. Please contact with team with your payment Id")
          
                nakshatra = int(moon_details.nakshatra)
                lagna_chart = clean_lagna_chart(json.loads(kundli_details.lagna_chart))

                return render(request, "kundli/premium.html", {
                    "form": form,
                    "is_report_generate": True,
                    "name" : user_name,
                    "birth_date": birth_details.birth_date,
                    "birth_time" : birth_details.birth_time,
                    "birth_place": place,
                    "kundli":kundli_details,
                    "nakshatra" : get_nakshatra_title(nakshatra),
                    "lagna_chart":clean_lagna_chart(json.loads(kundli_details.lagna_chart)),
                    "chart_url" : generate_kundli_svg_and_return_url(lagna_chart),
                    "ganra":get_gan(nakshatra),
                    "nadi": get_nadi(nakshatra),
                    "yoni": get_yogi(nakshatra),
                    "varna":get_varna(nakshatra),
                    "sade_sati_result": json.loads(kundli_details.sade_sati_result),
                    "sade_sati_phases": json.loads(kundli_details.sade_sati_phases),
                    "manglik_dosha": kundli_details.manglik_dosha,
                    "kaal_sarp_dosha":kundli_details.kaal_sarp_dosha,
                    "mahapurush_yogas":json.loads(kundli_details.mahapurush_yogas),
                    "gaja_kesari_yoga":kundli_details.gaja_kesari_yoga,
                    "budha_aditya_yoga":kundli_details.budha_aditya_yoga,
                    "pitra_dosha":kundli_details.pitra_dosha,
                    "kundli_data":clean_chart_data(kundli_details.kundli_data),
                 
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
    
@method_decorator(ratelimit(key='user_or_ip', rate='1/m', method='POST', block=True), name='dispatch')
class KundliPremiumDownloadView(View):
    pass
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
