import os 
import base64
import datetime

def global_env_variables(request):
    return {
        'APP_NAME': os.getenv("APP_NAME", "production"),
        'APP_ENV': os.getenv("APP_ENV", "production"),
        'currentYear' :datetime.datetime.now().year,
        'days': [str(i).zfill(2) for i in range(1, 31)],
        'months': { 1:"January", 2:"February", 3: "March", 4: "April", 5: "May", 6:"June",7:"July", 8:"August",9: "September",10:"October", 11:"November", 12:"December"},
        'hours': [str(i).zfill(2) for i in range(1, 13)],
        'minutes': [str(i).zfill(2) for i in range(0, 60)],
        'years': [i for i  in range(1954, datetime.datetime.now().year + 1)],
        'nonce' : base64.b64encode(os.urandom(16)).decode('utf-8'),
        "year": datetime.datetime.now().year,
        "social_icons": ["facebook", "twitter", "linkedin", "github"],
        "time_format":["AM","PM"],
    }


