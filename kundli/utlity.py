import os
import json
import logging
from datetime import date, time
from django.contrib import messages
from kundli.models import KundliReport
from django.utils.timezone import now
from django.shortcuts import redirect
from kundli.data import get_planet_descriptions
from authentication.utlity import send_error_log
from dasha.models import AntarDasha, DashaEffect
from dasha.models import BirthDetails,MoonPosition
from utlity.dasha_antradasha import calculate_moon_longitude
from utlity.panchag import get_nakshatra_title, calculate_nakshatra
from utlity.compatibility import get_gan, get_nadi, get_yogi, get_varna
from utlity.kundli import gaja_ksesari_yoga,budha_aditya_yoga,check_pitra_dosha, get_houses
from utlity.kundli import get_planet_positions, get_lagna,detect_panch_mahapurush_yogas,check_kaal_sarp_dosha,sade_sati_phases
from utlity.kundli import map_planets_to_houses,calculate_ascendant,sade_sati_check,get_rising_sign,get_planetary_longitudes,build_kundli_data
from utlity.kundli import generate_lagna_chart,check_manglik_dosha,clean_lagna_chart,clean_chart_data,generate_kundli_svg_and_return_url

from utlity.dasha_antradasha import (
    calculate_dasha,
    calculate_antar_dashas,
    calculate_moon_longitude,
    generate_vimshottari_dasha
)

payment_logger = logging.getLogger('payment')

APP_BASE_URL = os.environ.get('APP_BASE_URL')

def generate_kundli_details(request, clean_data):
    try:
        first_name = clean_data.get('first_name', '')
        last_name =  clean_data.get('last_name', '')
        days = clean_data.get("days")
        months = clean_data.get("months")
        years = clean_data.get("years")
        hours = clean_data.get("hours")
        minutes = clean_data.get("minutes")  # Fixed field reference
        seconds = clean_data.get("seconds")  # Fixed field reference
        place = clean_data.get("place")
        time_type = clean_data.get("time_format")
        birth_date = date(years, months, days)
        birth_time = time(hours, minutes, seconds)
        latitude = clean_data.get("latitude")
        longitude = clean_data.get("longitude")

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
            chart_url = APP_BASE_URL + generate_kundli_svg_and_return_url(lagna_chart)
            nakshatra = int(moon_details.nakshatra) 

    
            kundli_details = KundliReport.objects.create(
                user = request.user,
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

        
        return kundli_details
    except Exception as e:
        send_error_log(e)
        return None
    


def get_kundli_context(request, kundli_id):
   
    try:
       kundli_details = KundliReport.objects.get(id=kundli_id)
    except KundliReport.DoesNotExist:
        messages.error(request,"Invalid request, Please contact us")
        return redirect('kundli.premium_anaysis')
    
    if not kundli_details:
        messages.error(request,"Invalid request, Please contact us")
        return redirect('kundli.premium_anaysis')
    
    if kundli_details.user.id != request.user.id:
        messages.error(request,"Invalid request, Please contact us")
        return redirect('kundli.premium_anaysis')

    birth_details = kundli_details.birth_details
    antar_dasha_details = AntarDasha.objects.filter(birth_details=birth_details)
    moon_details = MoonPosition.objects.filter(birth_details=birth_details).first()

    if not moon_details:
        messages.error(request,"Something Went Wrong!, you can download your kundli from kundli menu")
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
    return context





def clean_chart_data(chart):
    # Replace technical names with human-friendly ones
    planet_name_map = {
        'sun': 'Sun', 'moon': 'Moon', 'mercury': 'Mercury',
        'venus': 'Venus', 'mars barycenter': 'Mars',
        'jupiter barycenter': 'Jupiter', 'saturn barycenter': 'Saturn',
        'rahu': 'Rahu', 'ketu': 'Ketu'
    }

    # Clean planet details
    planets = []
    for key, val in chart.items():
        if key in planet_name_map:
            planets.append({
                'name': planet_name_map[key],
                'degree': round(val['degree'], 2),
                'sign': val['sign'],
                'house': val['house']
            })

    # Clean house details
    houses = []
    for i in range(1, 13):
        key = f"{i}th_house"
        if key in chart:
            house = chart[key]
            house_planets = [
                planet_name_map.get(p, p.title()) for p in house.get('planets', [])
            ]
            houses.append({
                'number': i,
                'sign': house['sign'],
                'start_degree': house['start_degree'],
                'planets': house_planets
            })

    return {
        'planets': planets,
        'houses': houses
    }



def get_valid_context_or_redirect(request, kundli_id):

    if not kundli_id:
        messages.error(request, "Invalid request, please contact us.")
        return redirect('kundli.premium_anaysis')

    context = get_kundli_context(request, kundli_id)
      
    if not context:
        messages.error(request, "Unable to download your kundli. Sorry for the inconvenience! We'll be back soon!")
        return redirect('kundli.premium_anaysis')
        
    return context