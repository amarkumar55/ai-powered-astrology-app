from dasha.models import AntarDasha
from skyfield.api import load, Topos
from datetime import datetime, timedelta
from .ephemeris_loader import get_ephemeris
# Define the Dasha order and durations in years
DASHAS = [
    ("Ketu", 7),
    ("Venus", 20),
    ("Sun", 6),
    ("Moon", 10),
    ("Mars", 7),
    ("Rahu", 18),
    ("Jupiter", 16),
    ("Saturn", 19),
    ("Mercury", 17)
]

# Nakshatra-Planet Mapping
NAKSHATRA_PLANET_MAP = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
] * 3  # 27 Nakshatras

# Antar Dasha durations in months
ANTAR_DASHA_DURATIONS = {
    "Ketu": 1.75,    # months
    "Venus": 5.00,
    "Sun": 1.50,
    "Moon": 2.50,
    "Mars": 1.75,
    "Rahu": 4.50,
    "Jupiter": 4.00,
    "Saturn": 4.75,
    "Mercury": 4.25
}

def calculate_dasha(moon_longitude):
    """Determine the starting Dasha based on the Moon's Nakshatra."""
    nakshatra_index = int(moon_longitude / 13.3333)  # 360° / 27 = 13.3333°
    return NAKSHATRA_PLANET_MAP[nakshatra_index]

def get_planet_duration(planet):
    """Get the duration of a Dasha for a given planet."""
    for p, duration in DASHAS:
        if p == planet:
            return duration
    return 0

def get_next_dasha(current_planet):
    """Get the next planet in the Dasha cycle."""
    current_index = [p for p, _ in DASHAS].index(current_planet)
    next_index = (current_index + 1) % len(DASHAS)
    return DASHAS[next_index][0]

def calculate_moon_longitude(lat, lon, year, month, day, hour=0, minute=0, second=0):
    """Calculate Moon's position at the given date and time."""
    planets = get_ephemeris()
    earth, moon = planets['earth'], planets['moon']
    ts = load.timescale()
    t = ts.utc(year, month, day, hour, minute, second)
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    astrometric = observer.at(t).observe(moon)
    apparent = astrometric.apparent()
    _, moon_longitude, _ = apparent.ecliptic_latlon()  # Get the longitude
    return moon_longitude.degrees 

def generate_vimshottari_dasha(start_date, start_planet):
    """Generate the full Dasha sequence with start date and planet."""
    dasha_sequence = []
    current_date = start_date
    current_planet = start_planet

    for _ in range(9):  # Total 9 Mahadashas
        duration = get_planet_duration(current_planet)
        end_date = current_date + timedelta(days=duration * 365.25)  # Convert years to days
        dasha_sequence.append((current_planet, current_date, end_date))
        current_date = end_date
        current_planet = get_next_dasha(current_planet)

    return dasha_sequence


def calculate_antar_dashas(birth_details, mahadasha_start_date, mahadasha_planet, nakshatra, remaining_years):
   
    # Check if already calculated
    if AntarDasha.objects.filter(
        birth_details=birth_details,
        major_dasha=mahadasha_planet
    ).exists():
        return

    start_date = datetime.strptime(mahadasha_start_date, "%Y-%m-%d")

    for planet, months in ANTAR_DASHA_DURATIONS.items():
        duration_days = int(months * 30.44)  # Approximate conversion to days
        end_date = start_date + timedelta(days=duration_days)

        # Save to database
        AntarDasha.objects.create(
            birth_details=birth_details,
            nakshatra=nakshatra,
            major_dasha=mahadasha_planet,
            remaining_years=remaining_years,
            antar_dasha_planet=planet,
            start_date=start_date.date(),
            end_date=end_date.date()
        )
        
        # Update start_date for the next iteration
        start_date = end_date + timedelta(days=1)
