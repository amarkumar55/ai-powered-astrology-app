from skyfield.api import load
from datetime import datetime, timedelta
from horoscope.models import Horoscope
from .ephemeris_loader import get_ephemeris
import random

ZODIAC_SIGNS_WITH_RULERS = [
    ("Capricorn", (12, 22), (1, 19), "Saturn"),
    ("Aquarius", (1, 20), (2, 18), "Uranus"),
    ("Pisces", (2, 19), (3, 20), "Neptune"),
    ("Aries", (3, 21), (4, 19), "Mars"),
    ("Taurus", (4, 20), (5, 20), "Venus"),
    ("Gemini", (5, 21), (6, 20), "Mercury"),
    ("Cancer", (6, 21), (7, 22), "Moon"),
    ("Leo", (7, 23), (8, 22), "Sun"),
    ("Virgo", (8, 23), (9, 22), "Mercury"),
    ("Libra", (9, 23), (10, 22), "Venus"),
    ("Scorpio", (10, 23), (11, 21), "Pluto"),
    ("Sagittarius", (11, 22), (12, 21), "Jupiter"),
]

ZODIAC_SIGNS = [z[0] for z in ZODIAC_SIGNS_WITH_RULERS]

PLANET_ALIASES = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}

MESSAGES = {
    "very_favorable": [
        "Cosmic harmony blesses your sign—expect joy and success today!",
        "Your ruling planet is in perfect sync—embrace bold decisions.",
        "A beautiful day to start new ventures or express yourself freely."
        "Luck is on your side—seize opportunities without hesitation.",
        "The stars shine brightly on your journey—make bold strides.",
        "Your energy is magnetic today—share it with the world.",
        "Everything aligns for success—take action with confidence."
    ],
    "favorable": [
        "Positive influences support you—trust your instincts.",
        "Momentum builds slowly—patience will bring rewards.",
        "Take small steps toward your goals—everything aligns nicely.",
        "Steady cosmic currents help you make progress—keep moving.",
        "Support comes from unexpected places—stay open to guidance.",
        "You're gaining clarity—keep nurturing your long-term goals.",
        "Things are falling into place—your focus will pay off."
    ],
    "neutral": [
        "A steady day—focus on health and routine.",
        "Use this calm to reflect and plan your week.",
        "No major shifts—stick to what you know and build confidence."
        "Today invites quiet growth—use it to restore balance.",
        "Focus on self-care and staying present.",
        "Let the day flow naturally—answers will surface in time.",
        "Good time to tidy up loose ends and reflect on progress."
    ],
    "challenging": [
        "Planetary tension may cause friction—stay grounded.",
        "Today may test your patience—respond with grace.",
        "Avoid impulsive choices—clarity will come soon.",
        "Frustration may arise—step back and breathe before reacting.",
        "Astrological pressure may stir emotions—lean on your strengths.",
        "Clarity may be clouded—avoid major decisions if possible.",
        "You may feel off-course, but this moment will pass soon."
    ]
}

RETROGRADE_MESSAGES = [
    "Your ruling planet is in retrograde—pause before acting.",
    "Reflect more than react today—retrograde energy is strong.",
    "Expect delays or communication mishaps—double-check plans.",
    "Retrograde calls for inner clarity—don't rush major moves."
]

# Utility
def get_ruling_planet(sign):
    for s, _, _, planet in ZODIAC_SIGNS_WITH_RULERS:
        if s == sign:
            return PLANET_ALIASES[planet]
    return "sun"  # Fallback


def is_retrograde(planet, date, eph, ts):
    t1 = ts.utc(date.year, date.month, date.day)
    t2 = ts.utc(date.year, date.month, date.day + 1)

    ast1 = eph["earth"].at(t1).observe(planet)
    ast2 = eph["earth"].at(t2).observe(planet)

    ra1, _, _ = ast1.radec()
    ra2, _, _ = ast2.radec()

    return ra2.hours < ra1.hours


def get_alignment_score(sign, date, eph, ts):
    ruling_planet = get_ruling_planet(sign)
    earth = eph["earth"]
    sun = eph["sun"]
    moon = eph["moon"]
    target = eph[ruling_planet]
    t = ts.utc(date.year, date.month, date.day)

    astrometric_sun = earth.at(t).observe(sun).apparent()
    astrometric_planet = earth.at(t).observe(target).apparent()
    astrometric_moon = earth.at(t).observe(moon).apparent()

    ra_sun, _, _ = astrometric_sun.radec()
    ra_planet, _, _ = astrometric_planet.radec()
    ra_moon, _, _ = astrometric_moon.radec()

    # Angles in degrees
    angle_sun_planet = abs(ra_sun.hours - ra_planet.hours) * 15
    angle_moon_planet = abs(ra_moon.hours - ra_planet.hours) * 15

    # Weighted average: Sun (60%), Moon (40%)
    return (0.6 * angle_sun_planet + 0.4 * angle_moon_planet)

def get_mood_from_score(score):
    if score < 30:
        return "very_favorable"
    elif score < 90:
        return "favorable"
    elif score < 150:
        return "neutral"
    else:
        return "challenging"

def generate_range_prediction(sign, start_date, days, eph, ts):
    scores = []
    retrograde_warning = False
    ruling_planet_key = eph[get_ruling_planet(sign)]

    for i in range(days):
        day = start_date + timedelta(days=i)
        score = get_alignment_score(sign, day, eph, ts)
        scores.append(score)
        if is_retrograde(ruling_planet_key, day, eph, ts):
            retrograde_warning = True

    avg_score = sum(scores) / len(scores)
    mood = get_mood_from_score(avg_score)
    message = random.choice(MESSAGES[mood])

    if retrograde_warning:
        message += " " + random.choice(RETROGRADE_MESSAGES)

    return message

# Daily
def generate_daily_horoscope():
    today = datetime.now().date()
    eph = get_ephemeris()
    ts = load.timescale()
    for sign in ZODIAC_SIGNS:
        if not Horoscope.objects.filter(sign=sign, date=today, type='daily').exists():
            prediction = generate_range_prediction(sign, today, 1, eph, ts)
            Horoscope.objects.create(sign=sign, date=today, type='daily', prediction=prediction)

# Weekly
def generate_weekly_horoscope():
    today = datetime.now().date()
    eph = get_ephemeris()
    ts = load.timescale()
    for sign in ZODIAC_SIGNS:
        if not Horoscope.objects.filter(sign=sign, date=today, type='weekly').exists():
            prediction = generate_range_prediction(sign, today, 7, eph, ts)
            Horoscope.objects.create(sign=sign, date=today, type='weekly', prediction=prediction)

# Monthly
def generate_monthly_horoscope():
    today = datetime.now().date()
    eph = get_ephemeris()
    ts = load.timescale()
    for sign in ZODIAC_SIGNS:
        if not Horoscope.objects.filter(sign=sign, date=today, type='monthly').exists():
            prediction = generate_range_prediction(sign, today, 30, eph, ts)
            Horoscope.objects.create(sign=sign, date=today, type='monthly', prediction=prediction)

# Yearly
def generate_yearly_horoscope():
    today = datetime.now().date()
    eph = get_ephemeris()
    ts = load.timescale()
    for sign in ZODIAC_SIGNS:
        if not Horoscope.objects.filter(sign=sign, date=today, type='yearly').exists():
            prediction = generate_range_prediction(sign, today, 365, eph, ts)
            Horoscope.objects.create(sign=sign, date=today, type='yearly', prediction=prediction)
