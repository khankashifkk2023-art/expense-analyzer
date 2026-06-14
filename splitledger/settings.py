"""
Django settings for splitledger project.

Loads sensitive config from .env file via python-dotenv.
See .env.example for the full list of environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# ── Paths ───────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root
load_dotenv(BASE_DIR / '.env')

# ── Security ────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')


DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1'
).split(',')

# ── Application definition ─────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Our app
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'splitledger.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Look for templates in the project-level 'templates/' directory
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'splitledger.wsgi.application'

# If DATABASE_URL is not provided, try to build it from MySQL env variables,
# or fall back to SQLite for local development.
db_url = os.getenv('DATABASE_URL')
if not db_url:
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_port = os.getenv('DB_PORT', '3306')
    if db_name and db_user:
        # Encode password to handle special characters in connection URL
        from urllib.parse import quote_plus
        db_password_encoded = quote_plus(db_password)
        db_url = f"mysql://{db_user}:{db_password_encoded}@{db_host}:{db_port}/{db_name}"
    else:
        db_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

DATABASES = {
    "default": dj_database_url.parse(db_url)
}

# ── Password validation ────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalization ───────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── Static files ───────────────────────────────────────────────────────────

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# For collectstatic in production
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = (
"whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ── Media files (CSV uploads) ──────────────────────────────────────────────

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Auth settings ──────────────────────────────────────────────────────────

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/groups/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# ── Default primary key type ───────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── App-specific settings ──────────────────────────────────────────────────

# Default USD to INR conversion rate. Used when the Frankfurter API is
# unavailable. Can be overridden via the admin or the .env file.
USD_TO_INR_RATE = float(os.getenv('USD_TO_INR_RATE', '83.50'))
