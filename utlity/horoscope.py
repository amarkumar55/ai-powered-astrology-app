from skyfield.api import load
from datetime import datetime, timedelta
from  horoscope.models import Horoscope
import random
from .ephemeris_loader import get_ephemeris

def generate_message_horoscope(ra):
    morning_messages = [
        "You will experience peace and tranquility today. Focus on self-care and relaxation.",
        "A calm and harmonious morning awaits you. Take time to reflect on your thoughts.",
        "Your morning energy will be positive, bringing you a sense of contentment."
    ]
    afternoon_messages = [
        "Your energy will be high, and you may find success in your endeavors. Take initiative!",
        "Today brings new opportunities, so be proactive and confident.",
        "A productive afternoon is ahead. Use your motivation wisely."
    ]
    evening_messages = [
        "Today may present some challenges, but your perseverance will help you overcome them.",
        "Patience and resilience will be your strengths today. Stay focused.",
        "A few obstacles may come your way, but your determination will see you through."
    ]
    night_messages = [
        "Reflect on your actions and plan for the future. This is a good time for contemplation.",
        "Tonight is ideal for setting new goals and evaluating your progress.",
        "Take a break from the hustle and find peace in solitude."
    ]

    if ra.hours < 6:
        horoscope = random.choice(morning_messages)
    elif ra.hours < 12:
        horoscope = random.choice(afternoon_messages)
    elif ra.hours < 18:
        horoscope = random.choice(evening_messages)
    else:
        horoscope = random.choice(night_messages)

    return horoscope



def generate_horoscope(sign, day):
    planets = get_ephemeris()
    earth = planets['earth']
    sun = planets['sun']

    ts = load.timescale()
    t = ts.utc(day.year, day.month, day.day)

    astrometric = earth.at(t).observe(sun)
    ra, dec, distance = astrometric.radec()

    return generate_message_horoscope(ra)

def generate_daily_horoscope():
    today = datetime.now().date()
    zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    for sign in zodiac_signs:
        horoscope_text = generate_horoscope(sign, today)
        Horoscope.objects.create(sign=sign, date=today, type='daily', prediction=horoscope_text)

def generate_weekly_horoscope():
    today = datetime.now().date()
    zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    for sign in zodiac_signs:
        weekly_text = ""
        for i in range(7):
            day = today + timedelta(days=i)
            weekly_text += f"{day.strftime('%A')}: {generate_horoscope(sign, day)}\n\n"
        Horoscope.objects.create(sign=sign, date=today, type='weekly', prediction=weekly_text)


def get_zodiac_sign(day, month):
    zodiac_signs = [
        ("Capricorn", (1, 20)), ("Aquarius", (2, 19)), ("Pisces", (3, 21)), ("Aries", (4, 20)), 
        ("Taurus", (5, 21)), ("Gemini", (6, 21)), ("Cancer", (7, 23)), ("Leo", (8, 23)), 
        ("Virgo", (9, 23)), ("Libra", (10, 23)), ("Scorpio", (11, 22)), ("Sagittarius", (12, 22)), 
        ("Capricorn", (12, 31))
    ]
    for sign, (m, d) in zodiac_signs:
        if (month, day) <= (m, d):
            return sign
    return "Capricorn"
