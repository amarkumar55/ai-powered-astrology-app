import os
import pdfkit
import environ
from pathlib import Path
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env()

SECRET_KEY = 'django-insecure-(aoqsk*es*)vlb7r6ydwht$5zm_c!nekyn^1j5$hu1%093&*8!'

PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp', 
    'compressor',
    'captcha',
    'django_crontab',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'social_django',
    'phonenumber_field',
    'django_ratelimit',
    'csp',
    'home',
    'authentication',
    'numberlogy',
    'compatibility',
    'dasha',
    'horoscope',
    'kundli',
    'loshugrid',
    'panchang', 
    'dashboard',
    'commands',
    'subscription',
    'invoice',
    'blogs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    "csp.middleware.CSPMiddleware", 
    "django_otp.middleware.OTPMiddleware",
    "authentication.middleware.BlockUnverifiedUserMiddleware",
]

ROOT_URLCONF = 'astro.urls'


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'axes.backends.AxesStandaloneBackend',
    'social_core.backends.google.GoogleOAuth2',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.global_env_variables',
            ],
        },
    },
 
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

# Config for security

SECURE_SSL_REDIRECT = True 
SECURE_HSTS_SECONDS = 31536000  # Enable HTTP Strict Transport Security (1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True  # Enables X-XSS-Protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Enables X-Content-Type-Options: nosniff
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"  # Restricts referrer info
X_FRAME_OPTIONS = "DENY"  # Prevents clickjacking

CSP_IMG_SRC = ["'self'", "data:"]  # Allow images from self and data URIs
CSP_FONT_SRC = ("'self'", "https://fonts.googleapis.com", "https://fonts.gstatic.com")
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)

INSTALLED_APPS += ['axes']

MIDDLEWARE.insert(0, 'axes.middleware.AxesMiddleware')

AUTH_USER_MODEL = 'authentication.CustomUser'


# AXES Config 
AXES_LOCKOUT_TEMPLATE = 'home/lockout.html'  
AXES_ENABLED = not DEBUG
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=10)
AXES_LOCK_OUT_AT_FAILURE = True
AXES_USE_USER_AGENT = True


# SESSION Config
SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  
SESSION_COOKIE_AGE = 1800  

CSRF_COOKIE_SECURE = True 



# Account Config
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGOUT_REDIRECT_URL = '/authentication/login'
ACCOUNT_LOGOUT_ON_GET = True



# Login Config
LOGIN_URL = '/authentication/login'
LOGIN_REDIRECT_URL = '/dashboard/index'


# Log Config
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    },
}


# SERVER Config
WSGI_APPLICATION = 'astro.wsgi.application'


# Database config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache Config
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # adjust if Redis is hosted elsewhere
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


# Local config
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True



TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.fake.Fake'



# Config for serve static and media content

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
COMPRESS_ROOT = BASE_DIR / 'static'
COMPRESS_ENABLED = True
STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',   
                       'django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                     )





# Email Config
DEFAULT_FROM_EMAIL="eramarinfo@gmail.com"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'admin@example.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025  
EMAIL_USE_TLS = False  
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'info@astrolive.com'  




CRONJOBS = [
    ('10 0 * * *', 'django.core.management.call_command', ['generate_panchang']),
    ('15 0 * * *', 'django.core.management.call_command', ['generate_horoscopes']),
]