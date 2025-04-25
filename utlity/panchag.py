from skyfield.api import Topos, load
from datetime import datetime, timedelta
from .ephemeris_loader import get_ephemeris
from skyfield.almanac import find_discrete, sunrise_sunset

# Panchang data remains the same as your original code...


panchang_data = {
    "Tithi": {
        1: "Pratipada - Beginning, creation, initiation, new ventures",
        2: "Dwitiya - Harmony, partnership, balance",
        3: "Tritiya - Courage, strength, growth",
        4: "Chaturthi - Obstacles, challenges, Ganesh worship",
        5: "Panchami - Knowledge, learning, education",
        6: "Shashthi - Protection, health, healing",
        7: "Saptami - Victory, success, power",
        8: "Ashtami - Strength, overcoming evil, battle",
        9: "Navami - Energy, vitality, destruction of negativity",
        10: "Dashami - Accomplishment, fulfillment, authority",
        11: "Ekadashi - Spirituality, fasting, purification",
        12: "Dwadashi - Devotion, harmony, peace",
        13: "Trayodashi - Transformation, change, transition",
        14: "Chaturdashi - Power, control, aggressive actions",
        15: "Purnima - Fulfillment, completeness, spiritual growth",
        16: "Pratipada - Beginning, creation, initiation, new ventures",
        17: "Dwitiya - Harmony, partnership, balance",
        18: "Tritiya - Courage, strength, growth",
        19: "Chaturthi - Obstacles, challenges, Ganesh worship",
        20: "Panchami - Knowledge, learning, education",
        21: "Shashthi - Protection, health, healing",
        22: "Saptami - Victory, success, power",
        23: "Ashtami - Strength, overcoming evil, battle",
        24: "Navami - Energy, vitality, destruction of negativity",
        25: "Dashami - Accomplishment, fulfillment, authority",
        26: "Ekadashi - Spirituality, fasting, purification",
        27: "Dwadashi - Devotion, harmony, peace",
        28: "Trayodashi - Transformation, change, transition",
        29: "Chaturdashi - Power, control, aggressive actions",
        30: "Amavasya - Introspection, cleansing, new beginnings"
    },
    "Nakshatra": {
        1: "Ashwini - Quick action, speed, healing",
        2: "Bharani - Responsibility, discipline, endurance",
        3: "Krittika - Sharpness, energy, leadership",
        4: "Rohini - Beauty, fertility, creativity",
        5: "Mrigashira - Curiosity, exploration, quest for knowledge",
        6: "Ardra - Transformation, change, emotional upheaval",
        7: "Punarvasu - Renewal, reformation, positivity",
        8: "Pushya - Nourishment, growth, caring",
        9: "Ashlesha - Control, manipulation, secretive nature",
        10: "Magha - Authority, leadership, royal qualities",
        11: "Purva Phalguni - Pleasure, luxury, creativity",
        12: "Uttara Phalguni - Stability, reliability, hard work",
        13: "Hasta - Skillfulness, dexterity, craftsmanship",
        14: "Chitra - Brilliance, beauty, creativity",
        15: "Swati - Independence, freedom, flexibility",
        16: "Vishakha - Determination, ambition, competitiveness",
        17: "Anuradha - Friendship, cooperation, success through effort",
        18: "Jyeshtha - Seniority, authority, power",
        19: "Mula - Roots, foundation, destruction and rebuilding",
        20: "Purva Ashadha - Invincibility, fighting spirit, strength",
        21: "Uttara Ashadha - Victory, perseverance, long-term success",
        22: "Shravana - Listening, learning, wisdom",
        23: "Dhanishta - Wealth, prosperity, musical abilities",
        24: "Shatabhisha - Healing, mystery, secrets",
        25: "Purva Bhadrapada - Transformation, spiritual awakening",
        26: "Uttara Bhadrapada - Endurance, self-sacrifice, spiritual insights",
        27: "Revati - Nourishment, support, completion"
    },
    "Karana": {
        1: "Bava - Strength, power, initiation",
        2: "Balava - Nourishment, care, security",
        3: "Kaulava - Unity, bonding, forming connections",
        4: "Taitila - Stability, consistency, steadiness",
        5: "Garaja - Protection, safeguarding, defense",
        6: "Vanija - Business, trade, negotiations",
        7: "Vishti - Challenges, obstacles, careful decision-making",
        8: "Shakuni - Cleverness, strategy, cunning",
        9: "Chatushpada - Animal instincts, practicality, grounding",
        10: "Nagava - Transformation, movement, mystery",
        11: "Kimstughna - Endings, conclusions, dissolving old patterns"
    },
    "Yoga" : {
        1: "Vishkumbha - Obstacles and challenges",
        2: "Preeti - Affection, love, and harmony",
        3: "Ayushman - Longevity and good health",
        4: "Saubhagya - Good fortune and prosperity",
        5: "Shobhana - Beauty and charm",
        6: "Atiganda - Danger and misfortune",
        7: "Sukarma - Good deeds and positive actions",
        8: "Dhriti - Patience and stability",
        9: "Shoola - Sharpness and pain",
        10: "Ganda - Obstacles and problems",
        11: "Vriddhi - Growth and prosperity",
        12: "Dhruva - Stability and firmness",
        13: "Vyaghata - Obstruction and difficulties",
        14: "Harshana - Joy and happiness",
        15: "Vajra - Hardness and resilience",
        16: "Siddhi - Success and achievement",
        17: "Vyatipata - Calamity and disturbance",
        18: "Variyan - Comfort and luxury",
        19: "Parigha - Obstacles and barriers",
        20: "Shiva - Auspiciousness and peace",
        21: "Siddha - Accomplishment and success",
        22: "Sadhya - Realization and fulfillment",
        23: "Shubha - Goodness and auspiciousness",
        24: "Shukla - Brightness and purity",
        25: "Brahma - Creativity and knowledge",
        26: "Indra - Power and leadership",
        27: "Vaidhriti - Opposition and conflict"
    },
}




def calculate_tithi(sun_long, moon_long):
    tithi = int(((moon_long - sun_long) % 360) / 12) + 1
    return tithi

def calculate_nakshatra(moon_long):
    nakshatra = int((moon_long % 360) / (360 / 27)) + 1
    return nakshatra

def get_nakshatra_title(nakshatra):
    return panchang_data['Nakshatra'][nakshatra]

def calculate_yoga(sun_long, moon_long):
    yoga = int(((sun_long + moon_long) % 360) / (360 / 27)) + 1
    return yoga

def calculate_karana(tithi):
    karana = ((tithi - 1) * 2) % 11 + 1
    return karana

def calculate_vara(day_of_week):
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return weekdays[day_of_week]

def calculate_sunrise_sunset(location, ts, eph, t):
    f = sunrise_sunset(eph, location)
    t0 = ts.utc(t.year, t.month, t.day)
    t1 = ts.utc((t + timedelta(days=1)).year, (t + timedelta(days=1)).month, (t + timedelta(days=1)).day)
    times, events = find_discrete(t0, t1, f)

    sunrise, sunset = None, None
    for ti, event in zip(times, events):
        event_time = ti.utc_strftime('%Y-%m-%d %H:%M:%S')
        if event == 0:
            sunrise = event_time
        elif event == 1:
            sunset = event_time

    return sunrise, sunset

def calculate_rahu_kaal(day_of_week, sunrise, sunset):
    duration = (sunset - sunrise) / 8
    rahu_segments = [7, 2, 5, 6, 4, 3, 8]  # Sunday to Saturday
    segment = rahu_segments[day_of_week]
    rahu_start = sunrise + timedelta(seconds=int(duration.total_seconds() * (segment - 1)))
    rahu_end = rahu_start + duration
    return rahu_start.time(), rahu_end.time()

def calculate_time_duration(sunrise, sunset):
    return (sunset - sunrise) / 8

def calculate_gulika_kaal(day_of_week, sunrise, duration):
    start_part = [7, 6, 5, 4, 3, 2, 1][day_of_week]
    gulika_start = sunrise + timedelta(seconds=int(duration.total_seconds() * (start_part - 1)))
    gulika_end = gulika_start + duration
    return gulika_start.time(), gulika_end.time()

def calculate_yamaganda(day_of_week, sunrise, duration):
    start_part = [5, 4, 3, 2, 7, 6, 1][day_of_week]
    yamaganda_start = sunrise + timedelta(seconds=int(duration.total_seconds() * (start_part - 1)))
    yamaganda_end = yamaganda_start + duration
    return yamaganda_start.time(), yamaganda_end.time()

def calculate_abhijit_muhurat(sunrise, sunset):
    noon = sunrise + (sunset - sunrise) / 2
    abhijit_start = noon - timedelta(minutes=24)
    abhijit_end = noon + timedelta(minutes=24)
    return abhijit_start.time(), abhijit_end.time()

def format_time(time_obj):
    return time_obj.strftime('%I:%M %p')

def calculate_panchang(latitude, longitude, years, months, days, hours, minutes, seconds):
    eph = get_ephemeris()
    ts = load.timescale()
    location = Topos(latitude, longitude)

    if years and months:
        user_time = datetime(years, months, days, hours, minutes, seconds)
        t = ts.utc(years, months, days, hours, minutes, seconds)
    else:
        user_time = datetime.now()
        t = ts.utc(datetime.utcnow())

    sun = eph['sun']
    moon = eph['moon']

    astrometric_sun = sun.at(t)
    astrometric_moon = moon.at(t)

    ecliptic_sun = astrometric_sun.ecliptic_latlon()
    ecliptic_moon = astrometric_moon.ecliptic_latlon()

    sun_long = ecliptic_sun[1].degrees
    moon_long = ecliptic_moon[1].degrees

    tithi = calculate_tithi(sun_long, moon_long)
    nakshatra = calculate_nakshatra(moon_long)
    yoga = calculate_yoga(sun_long, moon_long)
    karana = calculate_karana(tithi)
    vara = calculate_vara(user_time.weekday())

   
    sunrise, sunset = calculate_sunrise_sunset(location, ts, eph, user_time)
    sunrise_dt = datetime.strptime(sunrise, '%Y-%m-%d %H:%M:%S')
    sunset_dt = datetime.strptime(sunset, '%Y-%m-%d %H:%M:%S')

    duration = calculate_time_duration(sunrise_dt, sunset_dt)
    rahu_kaal_start, rahu_kaal_end = calculate_rahu_kaal(user_time.weekday(), sunrise_dt, sunset_dt)
    gulika_kaal_start, gulika_kaal_end = calculate_gulika_kaal(user_time.weekday(), sunrise_dt, duration)
    yamaganda_start, yamaganda_end = calculate_yamaganda(user_time.weekday(), sunrise_dt, duration)
    abhijit_start, abhijit_end = calculate_abhijit_muhurat(sunrise_dt, sunset_dt)

    tithi_final_data = panchang_data["Tithi"][tithi].split("-")
    nakshatra_final_data = panchang_data["Nakshatra"][nakshatra].split("-")
    karana_final_data = panchang_data["Karana"][karana].split("-")
    yoga_final_data  = panchang_data["Yoga"][yoga].split("-")

    panchang = {
        "tithi": tithi_final_data[0] +"("+ tithi_final_data[1] + ")",
        "nakshatra": nakshatra_final_data[0] +"("+ nakshatra_final_data[1]+ ")",
        "yoga": yoga_final_data[0] +"("+ yoga_final_data[1]+ ")",
        "karana": karana_final_data[0] +"("+karana_final_data[1]+")",
        "vara": vara,
        "sunrise":  datetime.strptime(sunrise, '%Y-%m-%d %H:%M:%S'),
        "sunset":   datetime.strptime(sunset, '%Y-%m-%d %H:%M:%S'),
        "rahu_kaal": f"{format_time(rahu_kaal_start)} - {format_time(rahu_kaal_end)}",
        "gulika_kaal": f"{format_time(gulika_kaal_start)} - {format_time(gulika_kaal_end)}",
        "yamaganda": f"{format_time(yamaganda_start)} - {format_time(yamaganda_end)}",
        "abhijit_muhurat": f"{format_time(abhijit_start)} - {format_time(abhijit_end)}",
    }

    return panchang
