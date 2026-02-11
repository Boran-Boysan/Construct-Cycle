# Sonradan eklenmesi gerekenler
#  Redis/Channels kaldÄ±rÄ±ldÄ±
#  Production gÃ¼venlik ayarlarÄ± kaldÄ±rÄ±ldÄ±

import os
import sys
from pathlib import Path # Path (pathlib): Dosya ve klasÃ¶r yollarÄ±nÄ± iÅŸletim sisteminden baÄŸÄ±msÄ±z ÅŸekilde yÃ¶netmek iÃ§in kullanÄ±lÄ±r.
from decouple import config # config (decouple): .env dosyasÄ±ndaki gizli ayarlarÄ± (SECRET_KEY, DB bilgileri vb.) gÃ¼venli ÅŸekilde okumak iÃ§in kullanÄ±lÄ±r.
import dj_database_url # dj_database_url: VeritabanÄ± baÄŸlantÄ± bilgisini tek bir URL'den Django'nun anlayacaÄŸÄ± formata Ã§evirir.

#  Django projesinin ana klasÃ¶rÃ¼nÃ¼ temsil eder
BASE_DIR = Path(__file__).resolve().parent.parent

# Apps klasÃ¶rÃ¼nÃ¼ Python path'ine ekle
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

SECRET_KEY = config('SECRET_KEY', default='django-insecure-replace-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # PostgreSQL Ã¶zel Ã¶zellikler
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.companies',
    'apps.products',
    'apps.orders',
    'apps.conversations',
    'apps.stock',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'construct_cycle_project.middleware.SecurityHeadersMiddleware',
    'construct_cycle_project.middleware.RateLimitMiddleware',
    'construct_cycle_project.middleware.RequestLoggingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'construct_cycle_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'construct_cycle_project.wsgi.application'

# Database - PostgreSQL (LOCAL)
# Database - PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='constructcycle_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='berat0159'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
            'client_encoding': 'UTF8',
        }
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# UluslararasÄ±laÅŸtÄ±rma
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Statik dosyalar
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Medya dosyalarÄ±
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
     #'DEFAULT_THROTTLE_CLASSES': [
      #  'rest_framework.throttling.AnonRateThrottle',
       # 'rest_framework.throttling.UserRateThrottle'
    #],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT AyarlarÄ±
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# DRF Spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'ConstructCycle API',
    'DESCRIPTION': 'Ä°nÅŸaat Malzemesi Pazaryeri - SÃ¼rdÃ¼rÃ¼lebilir Ticaret Platformu',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# CORS (Local development iÃ§in)
CORS_ALLOW_ALL_ORIGINS = True  # Local'de tÃ¼m originlere izin ver
CORS_ALLOW_CREDENTIALS = True

# Cache (Local - basit memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'constructcycle-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Email (Local - console'a yazdÄ±r)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Loglama
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',  # Local'de DEBUG seviyesi
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

os.makedirs(BASE_DIR / 'logs', exist_ok=True)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'herberry619@gmail.com'  # âš ï¸ BURAYA KENDÄ° GMAÄ°L ADRESÄ°NÄ°ZÄ° YAZIN
EMAIL_HOST_PASSWORD = 'kgrz tjhp ydyt jagz'  # âš ï¸ BURAYA 16 HANELÄ° APP PASSWORD YAZIN (boÅŸluksuz)
DEFAULT_FROM_EMAIL = 'ConstructCycle <herberry619@gmail.com>'  # GÃ¶nderen ismi
SERVER_EMAIL = EMAIL_HOST_USER


# Frontend URL (email iÃ§indeki linkler iÃ§in)
FRONTEND_URL = 'http://localhost:8000'  # Production'da domain adresiniz olacak

# Oturum
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_NAME = 'constructcycle_sessionid'

# AI Servisi (ileride kullanÄ±lacak)
AI_SERVICE_URL = config('AI_SERVICE_URL', default='http://localhost:8001')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')