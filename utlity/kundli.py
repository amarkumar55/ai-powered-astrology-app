from skyfield.api import load, Topos,wgs84,N, E
from math import degrees, atan2, radians, sin, cos, tan
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dateutil.relativedelta import relativedelta
from .ephemeris_loader import get_ephemeris

ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]


PLANET_NAMES = {
    'sun': 'Sun',
    'moon': 'Moon',
    'mercury': 'Mercury',
    'venus': 'Venus',
    "mars barycenter":"MARS BARYCENTER",
    "jupiter barycenter":"JUPITER BARYCENTER",
    "saturn barycenter":"SATURN BARYCENTER",
    "rahu":"Rahu",
    "ketu":"Ketu",
}


NAISARGIKA_BALA = {
    'Sun': 60,
    'Moon': 51,
    'Venus': 43,
    'Jupiter': 34,
    'Mercury': 26,
    'Mars': 17,
    'Saturn': 9
}


EXALTATION = {
    'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn',
    'Mercury': 'Virgo', 'Jupiter': 'Cancer', 'Venus': 'Pisces',
    'Saturn': 'Libra'
}

DEBILITATION = {
    'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer',
    'Mercury': 'Pisces', 'Jupiter': 'Capricorn', 'Venus': 'Virgo',
    'Saturn': 'Aries'
}

DIK_BALA_HOUSES = {
    'Sun': 10,
    'Moon': 4,
    'Mars': 10,
    'Mercury': 1,
    'Jupiter': 1,
    'Venus': 7,
    'Saturn': 7
}


# Define planet own and exaltation signs
PLANET_OWN_SIGNS = {
    'Mars': [1, 8],       # Aries, Scorpio
    'Mercury': [3, 6],    # Gemini, Virgo
    'Jupiter': [9, 12],   # Sagittarius, Pisces
    'Venus': [2, 7],      # Taurus, Libra
    'Saturn': [10, 11],   # Capricorn, Aquarius
}

PLANET_EXALTATION_SIGNS = {
    'Mars': 10,       # Capricorn
    'Mercury': 6,     # Virgo
    'Jupiter': 4,     # Cancer
    'Venus': 12,      # Pisces
    'Saturn': 7       # Libra
}

KENDRA_HOUSES = [1, 4, 7, 10]

malefics = ['Saturn', 'Rahu', 'Ketu', 'Mars']
aspected_by = {
    'Sun': ['Saturn'],  
    '9th_house': ['Ketu'],
    '9th_lord': ['Rahu']
}


def get_rising_sign(asc_deg):
    sign_index = int(asc_deg // 30)
    return ZODIAC_SIGNS[sign_index]

def get_sign_from_longitude(degree):
    sign_index = int(degree // 30)
    return ZODIAC_SIGNS[sign_index], sign_index + 1


def get_planet_positions(year, month, day, hours, minutes, seconds, lat, lon):
    planets = get_ephemeris()
    earth = planets['earth']
    ts = load.timescale()
    t = ts.utc(year, month, day, hours, minutes, seconds)
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)

    planet_positions = {}

    for name in ['sun', 'moon', 'mercury', 'venus', 'MARS BARYCENTER', 'JUPITER BARYCENTER', 'SATURN BARYCENTER', 'rahu', 'ketu']:
        if name in ['rahu', 'ketu']:
            continue
        planet = planets[name]
        e = observer.at(t)
        astrometric = e.observe(planet).apparent()
        lon = astrometric.ecliptic_latlon()[1].degrees  # Use [1] instead of [2]
        planet_positions[name.lower()] = lon

    planet_positions.update(get_rahu_ketu(planets, observer, t))

    return planet_positions


def get_rahu_ketu(ephemeris, observer, t):
    moon = ephemeris['moon']
    sun = ephemeris['sun']
    e = observer.at(t)
    moon_pos = e.observe(moon).apparent()
    sun_pos = e.observe(sun).apparent()
    moon_lon = moon_pos.ecliptic_latlon()[1].degrees  # Use index [1]
    sun_lon = sun_pos.ecliptic_latlon()[1].degrees    # Use index [1]
    rahu = (moon_lon - sun_lon + 360) % 360
    ketu = (rahu + 180) % 360
    return {'rahu': rahu, 'ketu': ketu}

def calculate_ascendant(year, month, day, hour, minutes, seconds,lat, lon):

    eph = get_ephemeris()
    ts = load.timescale()
    t = ts.utc(year, month, day, hour, minutes, seconds)

    gmst_deg = t.gmst * 15  # GMST in degrees

    asc_deg = (gmst_deg + lon) % 360  # Basic approximation

    return asc_deg

def get_lagna(year, month, day, hour=0, minute=0, second=0, latitude=0, longitude = 0):
    ts = load.timescale()
    t = ts.utc(year, month, day, hour, minute, second)

    eph = get_ephemeris()
    earth = eph['earth']
    observer = earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude)
    
    # Correct sidereal time calculation
    sidereal_time = t.gmst  # in hours
    lst_deg = (sidereal_time * 15 + longitude) % 360  # convert hours to degrees

    # Obliquity of the ecliptic (approximate)
    epsilon = radians(23.439)

    asc_rad = atan2(
        -cos(radians(lst_deg)),
        sin(radians(lst_deg)) * cos(epsilon) - tan(radians(latitude)) * sin(epsilon)
    )

    asc_deg = (degrees(asc_rad) + 360) % 360
    return round(asc_deg, 2)

def get_houses(lagna_degree):
    SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    house_data = []
    for i in range(12):
        start_degree = (lagna_degree + 30 * i) % 360
        sign_index = int(start_degree // 30)
        house_data.append({
            'house': i + 1,
            'start_degree': round(start_degree, 2),
            'sign': SIGNS[sign_index]
        })

    return house_data


def map_planets_to_houses(planets_longitudes, houses):
    planet_positions = {}

    for planet, longitude in planets_longitudes.items():
        for i in range(12):
            house_start = houses[i]['start_degree']
            house_end = houses[(i + 1) % 12]['start_degree']

            # Handle circular wrap from 360 back to 0
            if house_start < house_end:
                if house_start <= longitude < house_end:
                    planet_positions[planet] = i + 1  # House numbers are 1-indexed
                    break
            else:
                # Wrap-around case (e.g., 330° to 0°)
                if longitude >= house_start or longitude < house_end:
                    planet_positions[planet] = i + 1
                    break

    return planet_positions


def get_planetary_longitudes(year, month, day, hour, minute, second, latitude, longitude):
    planets = get_ephemeris()
    ts = load.timescale()
    t = ts.utc(year, month, day, hour, minute, second)
    observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
    earth = planets['earth'] + observer

    planet_names = {
        'sun': planets['sun'],
        'moon': planets['moon'],
        'mars': planets['mars barycenter'],
        'mercury': planets['mercury'],
        'jupiter': planets['jupiter barycenter'],
        'venus': planets['venus'],
        'saturn': planets['saturn barycenter'],
    }

    planet_longitudes = {}

    # Regular planets
    for name, planet in planet_names.items():
        astrometric = earth.at(t).observe(planet)
        apparent = astrometric.apparent()
        lat, lon, _ = apparent.ecliptic_latlon()  # Correct unpacking
        planet_longitudes[name] = lon.degrees

    # Manually calculate Rahu and Ketu
    moon = planets['moon']
    sun = planets['sun']
    astrometric_moon = earth.at(t).observe(moon).apparent()
    astrometric_sun = earth.at(t).observe(sun).apparent()

    _, moon_lon, _ = astrometric_moon.ecliptic_latlon()
    _, sun_lon, _ = astrometric_sun.ecliptic_latlon()

    rahu_lon = (moon_lon.degrees - sun_lon.degrees + 360) % 360
    ketu_lon = (rahu_lon + 180) % 360

    planet_longitudes['rahu'] = rahu_lon
    planet_longitudes['ketu'] = ketu_lon

    return planet_longitudes


def generate_lagna_chart(planet_positions, ascendant_degree):
    _, lagna_sign_index = get_sign_from_longitude(ascendant_degree)

    # Lagna is the 1st house, signs rotate from there
    chart = {i+1: {'sign': ZODIAC_SIGNS[(lagna_sign_index - 1 + i) % 12], 'planets': []} for i in range(12)}

    for planet, degree in planet_positions.items():
        _, sign_index = get_sign_from_longitude(degree)
        # Calculate house from lagna
        house = (sign_index - lagna_sign_index + 12) % 12 + 1
        chart[house]['planets'].append(PLANET_NAMES[planet])

    return chart


def north_indian_chart(chart):
    
    NORTH_INDIAN_POSITIONS = {
        "1": (1, 1),
        "2": (0, 1),
        "3": (0, 2),
        "4": (0, 3),
        "5": (1, 3),
        "6": (2, 3),
        "7": (2, 2),
        "8": (2, 1),
        "9": (2, 0),
        "10": (1, 0),
        "11": (0, 0),
        "12": (0, 1)
    }

    # Optionally replace BARYCENTER names
    REPLACE_PLANETS = {
        "MARS BARYCENTER": "Mars",
        "SATURN BARYCENTER": "Saturn",
        "JUPITER BARYCENTER": "Jupiter",
    }

    # Prepare a 3x4 grid
    grid = [[[] for _ in range(4)] for _ in range(3)]

    for house, pos in NORTH_INDIAN_POSITIONS.items():
        r, c = pos
        house_data = chart.get(house, {'sign': '-', 'planets': []})
        sign = house_data['sign'][:3] if house_data['sign'] else '-'
        planets = [REPLACE_PLANETS.get(p, p) for p in house_data['planets']]
        grid[r][c] = [sign] + planets if planets else [sign, '-']

    return grid


def draw_north_indian_chart(rotated_signs, planet_signs):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Coordinates for houses (square format)
    boxes = [
        (50, 85), (75, 75), (85, 50), (75, 25),
        (50, 15), (25, 25), (15, 50), (25, 75),
        (50, 50), (62.5, 62.5), (50, 75), (37.5, 62.5)
    ]

    for i, (x, y) in enumerate(boxes[:8]):
        ax.add_patch(patches.Rectangle((x-12.5, y-12.5), 25, 25, fill=False))
        ax.text(x, y + 10, rotated_signs[i], ha='center', fontsize=8, weight='bold')
        planets = planet_signs.get(rotated_signs[i], [])
        ax.text(x, y - 5, ', '.join(planets), ha='center', fontsize=7)

    # Draw center diamond
    for i in range(4):
        x1, y1 = boxes[8 + i]
        x2, y2 = boxes[8 + ((i+1)%4)]
        ax.plot([x1, x2], [y1, y2], 'k')

    ax.text(50, 50, 'Ascendant\n' + rotated_signs[0], ha='center', fontsize=9, weight='bold')
    plt.title("North Indian Birth Chart", fontsize=14)
    plt.show()


def get_sthana_bala(planet_name, sign_name):
    if sign_name == EXALTATION.get(planet_name):
        return 60  # Full strength
    elif sign_name == DEBILITATION.get(planet_name):
        return 10  # Very weak
    else:
        return 30  # Moderate strength
    
def get_naisargika_bala(planet_name):
    return NAISARGIKA_BALA.get(planet_name, 0)

def check_manglik_dosha(planet_positions):
    manglik_houses = [1, 4, 7, 8, 12]
    mars_house = planet_positions.get('mars')
    return mars_house in manglik_houses

def check_kaal_sarp_dosha(planet_longitudes):
    """
    Checks if Kaal Sarp Dosha is present in the chart.

    Parameters:
        planet_longitudes (dict): {'Sun': 102.3, 'Moon': 110.5, ..., 'Rahu': 180.0, 'Ketu': 0.0}

    Returns:
        bool: True if Kaal Sarp Dosha is present
    """
    rahu = planet_longitudes.get('rahu')
    ketu = planet_longitudes.get('ketu')

    # Normalize all values to 0–360 degrees
    def in_range(value, start, end):
        if start < end:
            return start < value < end
        else:
            return value > start or value < end

    planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn']
    count = 0

    for planet in planets:
        deg = planet_longitudes.get(planet)
        if in_range(deg, ketu, rahu):
            count += 1

    return count == len(planets)


def gaja_ksesari_yoga(house_positions):
    """
    Check for Gaja Kesari Yoga: Jupiter in Kendra from Moon.

    house_positions: dict with planet names and their house number (1 to 12)
    Example:
        {
            'Moon': 4,
            'Jupiter': 7,
            ...
        }

    Returns: True if Yoga is present, else False
    """
    moon_house = house_positions.get('moon')
    jupiter_house = house_positions.get('jupiter')

    kendra_houses = [(moon_house + i - 1) % 12 + 1 for i in [1, 4, 7, 10]]
    return jupiter_house in kendra_houses

def budha_aditya_yoga(house_positions):
    """
    Check for Budha-Aditya Yoga: Sun and Mercury in the same house.
    
    house_positions: dict of planet names and their house numbers (1–12)

    Returns: True if Yoga is present
    """
    return house_positions.get('sun') == house_positions.get('mercury')


def is_mahapurush_yoga(planet, house_num, sign_name):
    exalted_signs = {
        'mars': 'Aries',
        'mercury': 'Gemini',
        'jupiter': 'Sagittarius',
        'venus': 'Libra',
        'saturn': 'Capricorn'
    }

    # Yoga is valid if planet is in Kendra (1, 4, 7, 10) and in its exalted sign
    return house_num in [1, 4, 7, 10] and sign_name == exalted_signs.get(planet)


def check_pitra_dosha(kundli_data):
    dosha_found = []

  
    # Validate that kundli_data is a dict
    if not isinstance(kundli_data, dict):
        return ["Invalid kundli data format"]

    # Rule 1: Sun afflicted by malefics
    sun_data = kundli_data.get('sun', {})
    if isinstance(sun_data, dict):
        aspected_by = sun_data.get('aspected_by', [])
        if any(m in aspected_by for m in malefics):
            dosha_found.append("Sun is afflicted by malefics (Rahu/Ketu/Saturn)")

    # Rule 2: Malefic in 9th house
    house_9 = kundli_data.get('9th_house', {})
    if isinstance(house_9, dict):
        has_planets = house_9.get('has', [])
        if any(p in malefics for p in has_planets):
            dosha_found.append("Malefic planet in 9th house")

    # Rule 3: 9th Lord afflicted
    ninth_lord = kundli_data.get('9th_lord', {})
    if isinstance(ninth_lord, dict) and ninth_lord.get('is_afflicted'):
        dosha_found.append("9th house lord is afflicted")

    return dosha_found if dosha_found else ["No major Pitra Dosha detected."]

def detect_panch_mahapurush_yogas(planet_house_map, houses):
    """
    planet_house_map: dict of planet -> house number (1 to 12)
    houses: list of dicts with 'start_degree' and 'sign' for each house
    """
    yogas = []
    yoga_map = {
        'mars': 'Ruchaka Yoga',
        'mercury': 'Bhadra Yoga',
        'jupiter': 'Hamsa Yoga',
        'venus': 'Malavya Yoga', 
        'saturn': 'Shasha Yoga'
    }

    for planet, house_num in planet_house_map.items():
        if planet in yoga_map:
            # Get the sign name from the house info
            sign_name = houses[house_num - 1]['sign']
            if is_mahapurush_yoga(planet, house_num, sign_name):
                yogas.append(yoga_map[planet])

    return yogas

# Opposite houses are 6 apart
def get_dik_bala(planet_name, planet_house_position):
    max_house = DIK_BALA_HOUSES.get(planet_name)
    if not max_house:
        return 0
    
    diff = (planet_house_position - max_house) % 12

    if diff == 0:
        return 60  # Full strength
    elif diff == 6:
        return 0   # Weakest
    elif diff in [1, 11]:
        return 45
    elif diff in [2, 10]:
        return 30
    elif diff in [3, 9]:
        return 15
    elif diff in [4, 8]:
        return 5
    elif diff in [5, 7]:
        return 2
    else:
        return 0
    
def is_sade_sati(moon_sign, saturn_sign):
    moon_index = ZODIAC_SIGNS.index(moon_sign)
    sade_sati_signs = [
        ZODIAC_SIGNS[(moon_index - 1) % 12],  # Before
        moon_sign,                            # Current
        ZODIAC_SIGNS[(moon_index + 1) % 12],  # After
    ]
    return saturn_sign in sade_sati_signs, sade_sati_signs

def get_zodiac_sign(degree):
    return ZODIAC_SIGNS[int(degree // 30)]

def sade_sati_phases(birth_moon_longitude, birth_date):
    moon_sign = get_zodiac_sign(birth_moon_longitude)
    moon_index = ZODIAC_SIGNS.index(moon_sign)
    
    # Phase signs
    before = ZODIAC_SIGNS[(moon_index - 1) % 12]
    current = moon_sign
    after = ZODIAC_SIGNS[(moon_index + 1) % 12]
    
    # Assume each phase lasts 2.5 years (30 months)
    start_date = birth_date + relativedelta(years=18)  # Saturn return approx after 30 years, adjust as needed
    first_phase_start = start_date
    second_phase_start = first_phase_start + relativedelta(months=30)
    third_phase_start = second_phase_start + relativedelta(months=30)
    end_date = third_phase_start + relativedelta(months=30)

    return {
        "moon_sign": moon_sign,
        "phases": {
            "First Phase (Rising)": {
                "sign": before,
                "start": first_phase_start.isoformat(),
                "end": second_phase_start.isoformat(),
            },
            "Second Phase (Peak)": {
                "sign": current,
                "start": second_phase_start.isoformat(),
                "end": third_phase_start.isoformat(),
            },
            "Third Phase (Setting)": {
                "sign": after,
                "start": third_phase_start.isoformat(),
                "end": end_date.isoformat(),
            }
        }
    }

def sade_sati_check(birth_moon_longitude):
    eph = get_ephemeris()
    planets = eph
    ts = load.timescale()
    now = ts.now()

    # Get Saturn's current position
    saturn = planets['saturn barycenter']
    earth = planets['earth']
    astrometric = earth.at(now).observe(saturn).apparent()
    saturn_lon, _, _ = astrometric.ecliptic_latlon()

    # Moon sign at birth
    moon_sign = get_zodiac_sign(birth_moon_longitude)
    saturn_sign = get_zodiac_sign(saturn_lon.degrees)

    in_sade_sati, affected_signs = is_sade_sati(moon_sign, saturn_sign)
    return {
        "moon_sign": moon_sign,
        "saturn_sign": saturn_sign,
        "is_in_sade_sati": in_sade_sati,
        "affected_signs": affected_signs
    }

def build_kundli_data(planet_positions, house_data):
    kundli_data = {}

    # Sort house data by start_degree for easy house determination
    sorted_houses = sorted(house_data, key=lambda h: h['start_degree'])

    # Prepare house ranges (360-degree wrap handled)
    house_ranges = []
    for i, house in enumerate(sorted_houses):
        start = house['start_degree']
        end = sorted_houses[(i + 1) % 12]['start_degree']
        if end <= start:
            end += 360
        house_ranges.append((house['house'], house['sign'], start, end))

    # Map each planet to its house and sign
    house_planets = {i: [] for i in range(1, 13)}
    for planet, degree in planet_positions.items():
        original_deg = degree
        if degree < house_ranges[0][2]:  # handle wraparound
            degree += 360
        for house, sign, start, end in house_ranges:
            if start <= degree < end:
                kundli_data[planet] = {
                    'degree': original_deg,
                    'house': house,
                    'sign': sign,
                }
                house_planets[house].append(planet)
                break

    # Add info for each house: its sign, planets in it (optional)
    for house, sign, start, end in house_ranges:
        kundli_data[f'{house}th_house'] = {
            'sign': sign,
            'start_degree': start % 360,
            'planets': house_planets[house],
        }

    return kundli_data




def clean_lagna_chart(planet_positions):
    """
    Cleans the given Lagna chart by replacing long-form planet names 
    like 'SATURN BARYCENTER' with short names like 'Saturn'.
    
    Args:
        planet_positions (dict): Dictionary with house numbers as keys and
                                 {'sign': str, 'planets': list[str]} as values.

    Returns:
        dict: Cleaned version of the Lagna chart.
    """
    planet_name_map = {
        'MARS BARYCENTER': 'Mars',
        'SATURN BARYCENTER': 'Saturn',
        'JUPITER BARYCENTER': 'Jupiter',
        # Add more mappings if needed
    }

    cleaned_chart = {}

    for house, details in planet_positions.items():
        # Replace planet names with cleaned versions
        cleaned_planets = [planet_name_map.get(p, p) for p in details['planets']]
        
        # Assign cleaned data
        cleaned_chart[house] = {
            'sign': details['sign'],
            'planets': cleaned_planets
        }

    return cleaned_chart




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


import os
import svgwrite
from datetime import datetime
import math

def rotate_point(x, y, cx, cy, angle_deg):
    angle_rad = math.radians(angle_deg)
    dx = x - cx
    dy = y - cy
    qx = cx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    qy = cy + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    return qx, qy

def generate_kundli_svg_and_return_url(house_data, static_dir="media/kundli_svgs", base_url="/media/kundli_svgs/"):
    print(house_data)
    os.makedirs(static_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kundli_chart_{timestamp}.svg"
    filepath = os.path.join(static_dir, filename)

    dwg = svgwrite.Drawing(filepath, size=("500px", "500px"))
    center = 250
    size = 400
    half = size // 2

    # Original square corners (not rotated)
    square = [
        (center - half, center - half),
        (center + half, center - half),
        (center + half, center + half),
        (center - half, center + half)
    ]

    # Rotate corners around center by 45°
    rotated_corners = [rotate_point(x, y, center, center, 90) for x, y in square]
    dwg.add(dwg.polygon(rotated_corners, fill="white", stroke="black", stroke_width=2))

    # Draw diagonals
    dwg.add(dwg.line(rotated_corners[0], rotated_corners[2], stroke="black", stroke_width=2))
    dwg.add(dwg.line(rotated_corners[1], rotated_corners[3], stroke="black", stroke_width=2))

    # Midpoints for center square (diamond)
    midpoints = [
        ((rotated_corners[0][0] + rotated_corners[1][0]) / 2, (rotated_corners[0][1] + rotated_corners[1][1]) / 2),
        ((rotated_corners[1][0] + rotated_corners[2][0]) / 2, (rotated_corners[1][1] + rotated_corners[2][1]) / 2),
        ((rotated_corners[2][0] + rotated_corners[3][0]) / 2, (rotated_corners[2][1] + rotated_corners[3][1]) / 2),
        ((rotated_corners[3][0] + rotated_corners[0][0]) / 2, (rotated_corners[3][1] + rotated_corners[0][1]) / 2),
    ]

    for i in range(4):
        dwg.add(dwg.line(midpoints[i], midpoints[(i + 1) % 4], stroke="black", stroke_width=2))

    # House positions mapped to center
    inner_offset = half * 0.9   # 50% inward for corner triangles
    center_offset = half * 0.330  # About 17.5% inward for center squares

    house_text_styles = {
        1:  {"x": 150, "y": 80, "anchor": "middle", "angle": 0},
        2:  {"x": 340, "y": 80, "anchor": "middle", "angle": 0},
        3:  {"x": 430, "y": 140, "anchor": "middle", "angle": 90},
        4:  {"x": 430, "y": 320, "anchor": "middle", "angle": 0},
        5:  {"x": 360, "y": 400, "anchor": "middle", "angle": 0},
        6:  {"x": 150, "y": 400, "anchor": "middle", "angle": 0},
        7:  {"x": 80, "y": 320, "anchor": "middle", "angle": 0},
        8:  {"x": 80, "y": 140, "anchor": "middle", "angle": 315},
        9:  {"x": 150, "y": 250, "anchor": "middle", "angle": 0},
        10: {"x": 250, "y": 150, "anchor": "middle", "angle": 0},
        11: {"x": 340, "y": 240, "anchor": "middle", "angle": 0},
        12: {"x": 250, "y": 340, "anchor": "middle", "angle": 0},
    }
    
    house_positions = {
        1:  (center, center - inner_offset),
        2:  (center + inner_offset, center - inner_offset),
        3:  (center + inner_offset, center),
        4:  (center + inner_offset, center + inner_offset),
        5:  (center, center + inner_offset),
        6:  (center - inner_offset, center + inner_offset),
        7:  (center - inner_offset, center),
        8:  (center - inner_offset, center - inner_offset),
        9:  (center - center_offset, center - center_offset),
        10: (center + center_offset, center - center_offset),
        11: (center + center_offset, center + center_offset),
        12: (center - center_offset, center + center_offset),
    }

    for house, (x, y) in house_positions.items():

        sign = house_data[house]["sign"]
        planets = house_data[house]["planets"]
     
        style = house_text_styles[house]

        dwg.add(dwg.text(
            f'{house} {sign}',
            insert=(style["x"], style["y"]),
            text_anchor=style["anchor"],
            font_size="11px",
            fill="black",
            transform=f"rotate({style['angle']},{style['x']},{style['y']})"
        ))
        if planets:
            dwg.add(dwg.text(
                ', '.join(planets),
                insert=(style["x"], style["y"] + 14),
                text_anchor=style["anchor"],
                font_size="10px",
                fill="blue",
                transform=f"rotate({style['angle']},{style['x']},{style['y'] + 14})"
            ))

    dwg.save()
    return os.path.join(base_url, filename)