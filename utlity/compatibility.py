VARNA_MAPPING = [
    'Brahmin', 'Kshatriya', 'Vaishya', 'Shudra',
    'Kshatriya', 'Vaishya', 'Shudra', 'Brahmin',
    'Vaishya', 'Shudra', 'Brahmin', 'Kshatriya',
    'Shudra', 'Brahmin', 'Kshatriya', 'Vaishya',
    'Brahmin', 'Kshatriya', 'Vaishya', 'Shudra',
    'Kshatriya', 'Vaishya', 'Shudra', 'Brahmin',
    'Vaishya', 'Shudra', 'Brahmin'
]


VASHYA_MAPPING = {
    'Chatushpada': [1, 2, 8, 25],  # Ashwini, Bharani, Pushya, Purva Bhadrapada
    'Dwipada': [6, 7, 15, 24],     # Ardra, Punarvasu, Swati, Shatabhisha
    'Jalchar': [27, 26],           # Revati, Uttarabhadrapada
    'Vanchar': [10, 14],           # Magha, Chitra
    'Keet': [4],                   # Rohini
}


YONI_COMPATIBILITY = {
    ('Horse', 'Horse'): 4, ('Horse', 'Elephant'): 4, ('Horse', 'Lion'): 0, ('Horse', 'Buffalo'): 0,
    ('Elephant', 'Elephant'): 4, ('Elephant', 'Horse'): 4, ('Elephant', 'Dog'): 0, ('Elephant', 'Cat'): 0,
    ('Lion', 'Lion'): 4, ('Lion', 'Tiger'): 4, ('Lion', 'Rabbit'): 0, ('Lion', 'Horse'): 0,
    ('Buffalo', 'Buffalo'): 4, ('Buffalo', 'Cow'): 4, ('Buffalo', 'Tiger'): 0, ('Buffalo', 'Horse'): 0,
    ('Dog', 'Dog'): 4, ('Dog', 'Cat'): 4, ('Dog', 'Elephant'): 0, ('Dog', 'Rabbit'): 0,
    ('Cat', 'Cat'): 4, ('Cat', 'Dog'): 4, ('Cat', 'Elephant'): 0, ('Cat', 'Snake'): 0,
    ('Rat', 'Rat'): 4, ('Rat', 'Monkey'): 4, ('Rat', 'Snake'): 0, ('Rat', 'Cat'): 0,
    ('Snake', 'Snake'): 4, ('Snake', 'Rat'): 4, ('Snake', 'Cat'): 0, ('Snake', 'Dog'): 0,
    ('Cow', 'Cow'): 4, ('Cow', 'Buffalo'): 4, ('Cow', 'Lion'): 0, ('Cow', 'Tiger'): 0,
    ('Tiger', 'Tiger'): 4, ('Tiger', 'Lion'): 4, ('Tiger', 'Cow'): 0, ('Tiger', 'Buffalo'): 0,
    ('Rabbit', 'Rabbit'): 4, ('Rabbit', 'Goat'): 4, ('Rabbit', 'Lion'): 0, ('Rabbit', 'Dog'): 0,
    ('Goat', 'Goat'): 4, ('Goat', 'Rabbit'): 4, ('Goat', 'Tiger'): 0, ('Goat', 'Elephant'): 0,
    ('Monkey', 'Monkey'): 4, ('Monkey', 'Rat'): 4, ('Monkey', 'Snake'): 0, ('Monkey', 'Lion'): 0,
}


YONI_MAPPING = [
    'Horse', 'Elephant', 'Horse', 'Horse', 'Elephant', 'Dog', 'Dog', 'Cat', 'Cat',
    'Rat', 'Rat', 'Snake', 'Snake', 'Cow', 'Tiger', 'Tiger', 'Rabbit', 'Goat', 'Goat',
    'Monkey', 'Monkey', 'Snake', 'Dog', 'Cat', 'Horse', 'Lion', 'Buffalo', 'Lion'
]


GRAHA_RELATIONSHIP = {
    'Sun': {'Friends': ['Moon', 'Mars', 'Jupiter'], 'Neutral': ['Mercury'], 'Enemies': ['Venus', 'Saturn']},
    'Moon': {'Friends': ['Sun', 'Mercury'], 'Neutral': [], 'Enemies': ['Mars', 'Saturn', 'Venus']},
    'Mars': {'Friends': ['Sun', 'Moon', 'Jupiter'], 'Neutral': ['Venus', 'Saturn'], 'Enemies': ['Mercury']},
    'Mercury': {'Friends': ['Sun', 'Venus'], 'Neutral': ['Mars', 'Jupiter', 'Saturn'], 'Enemies': ['Moon']},
    'Jupiter': {'Friends': ['Sun', 'Moon', 'Mars'], 'Neutral': ['Saturn'], 'Enemies': ['Mercury', 'Venus']},
    'Venus': {'Friends': ['Mercury', 'Saturn'], 'Neutral': ['Mars', 'Jupiter'], 'Enemies': ['Sun', 'Moon']},
    'Saturn': {'Friends': ['Mercury', 'Venus'], 'Neutral': ['Jupiter'], 'Enemies': ['Sun', 'Moon', 'Mars']},
}

# Mapping Nakshatra to ruling planet
PLANET_MAPPING = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
]

GAN_MAPPING = {
    'Deva': [1, 5, 7, 8, 13, 15, 17, 27],       # Nakshatra numbers for Deva
    'Manushya': [2, 4, 6, 10, 11, 16, 20, 21, 25],  # Nakshatra numbers for Manushya
    'Rakshasa': [3, 9, 12, 14, 18, 19, 22, 23, 24],  # Nakshatra numbers for Rakshasa
}


RASHI_MAPPING = {
    1: 'Aries', 2: 'Aries', 3: 'Aries',             # Ashwini, Bharani, Krittika (part 1)
    4: 'Taurus', 5: 'Taurus', 6: 'Taurus',           # Krittika (part 2), Rohini, Mrigashira (part 1)
    7: 'Gemini', 8: 'Gemini', 9: 'Gemini',           # Mrigashira (part 2), Ardra, Punarvasu (part 1)
    10: 'Cancer', 11: 'Cancer', 12: 'Cancer',        # Punarvasu (part 2), Pushya, Ashlesha
    13: 'Leo', 14: 'Leo', 15: 'Leo',                 # Magha, Purva Phalguni, Uttara Phalguni (part 1)
    16: 'Virgo', 17: 'Virgo', 18: 'Virgo',           # Uttara Phalguni (part 2), Hasta, Chitra (part 1)
    19: 'Libra', 20: 'Libra', 21: 'Libra',           # Chitra (part 2), Swati, Vishakha (part 1)
    22: 'Scorpio', 23: 'Scorpio', 24: 'Scorpio',     # Vishakha (part 2), Anuradha, Jyeshtha
    25: 'Sagittarius', 26: 'Sagittarius', 27: 'Sagittarius', # Moola, Purva Ashadha, Uttara Ashadha (part 1)
    28: 'Capricorn', 29: 'Capricorn', 30: 'Capricorn',       # Uttara Ashadha (part 2), Shravana, Dhanishta (part 1)
    31: 'Aquarius', 32: 'Aquarius', 33: 'Aquarius',          # Dhanishta (part 2), Shatabhisha, Purva Bhadrapada (part 1)
    34: 'Pisces', 35: 'Pisces', 36: 'Pisces'                 # Purva Bhadrapada (part 2), Uttara Bhadrapada, Revati
}


BHAKOOT_DOSHA_COMBINATIONS = [
    ('Aries', 'Taurus'), ('Taurus', 'Aries'),   # 2-12
    ('Leo', 'Virgo'), ('Virgo', 'Leo'),         # 2-12
    ('Cancer', 'Aquarius'), ('Aquarius', 'Cancer'), # 6-8
    ('Scorpio', 'Aries'), ('Aries', 'Scorpio'), # 6-8
    ('Sagittarius', 'Cancer'), ('Cancer', 'Sagittarius'), # 5-9
    ('Capricorn', 'Leo'), ('Leo', 'Capricorn'), # 5-9
]


NADI_MAPPING = {
    1: 'Adi', 2: 'Madhya', 3: 'Antya',    # Ashwini, Bharani, Krittika
    4: 'Antya', 5: 'Madhya', 6: 'Adi',    # Rohini, Mrigashira, Ardra
    7: 'Adi', 8: 'Madhya', 9: 'Adi',      # Punarvasu, Pushya, Ashlesha
    10: 'Antya', 11: 'Antya', 12: 'Adi',  # Magha, Purvaphalguni, Uttaraphalguni
    13: 'Madhya', 14: 'Adi', 15: 'Antya', # Hasta, Chitra, Swati
    16: 'Madhya', 17: 'Adi', 18: 'Madhya',# Vishakha, Anuradha, Jyeshtha
    19: 'Antya', 20: 'Madhya', 21: 'Adi', # Moola, Purvashada, Uttarashada
    22: 'Antya', 23: 'Madhya', 24: 'Adi', # Shravana, Dhanishta, Shatabhisha
    25: 'Adi', 26: 'Antya', 27: 'Madhya', # Purvabhadrapada, Uttarabhadrapada, Revati
}


def calculate_varna_score(nakshatra_boy, nakshatra_girl):
    varna_boy = VARNA_MAPPING[nakshatra_boy - 1]
    varna_girl = VARNA_MAPPING[nakshatra_girl - 1]
   
    if varna_boy == varna_girl:
        return 1
    elif varna_boy == 'Brahmin' or (varna_boy == 'Kshatriya' and varna_girl != 'Brahmin'):
        return 0.5
    else:
        return 0


def calculate_vashya_score(nakshatra_boy, nakshatra_girl):
    boy_vashya = None
    girl_vashya = None

    # Identify Vashya for boy
    for vashya, nakshatras in VASHYA_MAPPING.items():
        if nakshatra_boy in nakshatras:
            boy_vashya = vashya
            break

    # Identify Vashya for girl
    for vashya, nakshatras in VASHYA_MAPPING.items():
        if nakshatra_girl in nakshatras:
            girl_vashya = vashya
            break

    # Check compatibility
    if boy_vashya == girl_vashya:
        return 2
    elif (boy_vashya in ['Chatushpada', 'Vanchar'] and girl_vashya in ['Chatushpada', 'Vanchar']) or \
         (boy_vashya in ['Dwipada', 'Jalchar'] and girl_vashya in ['Dwipada', 'Jalchar']):
        return 1
    else:
        return 0
    

def calculate_tara_score(nakshatra_boy, nakshatra_girl):
    tara_boy = (nakshatra_boy - 1) % 9 + 1
    tara_girl = (nakshatra_girl - 1) % 9 + 1

    # Check if the difference is even or odd
    if abs(tara_boy - tara_girl) % 2 == 0:
        return 3  # Compatible
    else:
        return 0  # Incompatible

def calculate_yoni_score(nakshatra_boy, nakshatra_girl):
    yoni_boy = YONI_MAPPING[nakshatra_boy - 1]
    yoni_girl = YONI_MAPPING[nakshatra_girl - 1]

    # Check the compatibility between the yonis
    score = YONI_COMPATIBILITY.get((yoni_boy, yoni_girl), 0)
    return score 

def calculate_graha_maitri_score(nakshatra_boy, nakshatra_girl):
    planet_boy = PLANET_MAPPING[nakshatra_boy - 1]
    planet_girl = PLANET_MAPPING[nakshatra_girl - 1]


    relationship = GRAHA_RELATIONSHIP.get(planet_boy)

    if planet_girl in relationship['Friends']:
        return 5
    elif planet_girl in relationship['Neutral']:
        return 4
    elif planet_girl in relationship['Enemies']:
        return 0
    else:
        return 3  # Default for unlisted relationships


def get_gan(nakshatra):
  
    for gan, nakshatras in GAN_MAPPING.items():
        if nakshatra in nakshatras:
            return gan
    return None

def get_yogi(nakshatra):
    return  YONI_MAPPING[int(nakshatra)-1]

def get_varna(nakshatra):
    return VARNA_MAPPING[int(nakshatra)-1]


def calculate_gana_score(nakshatra_boy, nakshatra_girl):
    gan_boy = get_gan(nakshatra_boy)
    gan_girl = get_gan(nakshatra_girl)

    if gan_boy == gan_girl:
        return 6  # Same Gana
    elif (gan_boy == 'Deva' and gan_girl == 'Manushya') or (gan_boy == 'Manushya' and gan_girl == 'Deva'):
        return 5  # Deva-Manushya combination
    elif (gan_boy == 'Rakshasa' and gan_girl == 'Manushya') or (gan_boy == 'Manushya' and gan_girl == 'Rakshasa'):
        return 1  # Manushya-Rakshasa combination
    else:
        return 0  # Deva-Rakshasa combination

def get_rashi(nakshatra):
    return RASHI_MAPPING.get(nakshatra, None)


def calculate_bhakoot_score(nakshatra_boy, nakshatra_girl):
    rashi_boy = get_rashi(nakshatra_boy)
    rashi_girl = get_rashi(nakshatra_girl)

    if (rashi_boy, rashi_girl) in BHAKOOT_DOSHA_COMBINATIONS:
        return 0  # Bhakoot Dosha
    else:
        return 7  # No Dosha


def get_nadi(nakshatra):
    return NADI_MAPPING.get(nakshatra, None)


def calculate_nadi_score(nakshatra_boy, nakshatra_girl):
    nadi_boy = get_nadi(nakshatra_boy)
    nadi_girl = get_nadi(nakshatra_girl)

    # Check for Nadi Dosha
    if nadi_boy == nadi_girl:
        return 0  # Nadi Dosha (same Nadi)
    else:
        return 8  # No Dosha (different Nadis)

# Compatibility calculation
def ashtakoot_compatibility(nakshatra_boy, nakshatra_girl):
    
    data = {
        "varna_score":0,
        "vasha_score":0,
        "tara_score":0,
        "yoni_score":0,
        "graha_maitry_score":0,
        "gana_score":0,
        "bhakoot_score":0,
        "nadi_score":0,
        "total_score":0,
    }
    score = 0
    data['varna_score']  = calculate_varna_score(nakshatra_boy,nakshatra_girl)
    score += data['varna_score']
    data['vasha_score']  = calculate_vashya_score(nakshatra_boy, nakshatra_girl)
    score += data['vasha_score']
    data['tara_score']  = calculate_tara_score(nakshatra_boy, nakshatra_girl)
    score += data['tara_score']
    data['yoni_score'] = calculate_yoni_score(nakshatra_boy, nakshatra_girl)
    score += data['yoni_score']
    data['graha_maitry_score'] = calculate_graha_maitri_score(nakshatra_boy, nakshatra_girl)
    score += data['graha_maitry_score']
    data['gana_score'] = calculate_gana_score(nakshatra_boy, nakshatra_girl)
    score += data['gana_score']
    data['bhakoot_score']  = calculate_bhakoot_score(nakshatra_boy, nakshatra_girl)
    score += data['bhakoot_score']
    data['nadi_score']  = calculate_nadi_score(nakshatra_boy, nakshatra_girl)
    score += data['nadi_score']

    data['total_score'] = score
    return data

