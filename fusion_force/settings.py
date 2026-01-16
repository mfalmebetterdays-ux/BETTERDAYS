# settings.py - ADD/UPDATE THESE SETTINGS
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-123')

# Keep DEBUG as True for now
DEBUG = True

# ALLOWED_HOSTS - Add your Railway URL
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'fusionforcellc-production.up.railway.app',
    '.railway.app',
    '.pamela-fusionforce.com',
]

# ========== CRITICAL FIX: CSRF_TRUSTED_ORIGINS ==========
CSRF_TRUSTED_ORIGINS = [
    'https://fusionforcellc-production.up.railway.app',
    'https://*.railway.app',
    'https://*.pamela-fusionforce.com',
]

# Also add HTTP for local development
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:8080',
        'http://127.0.0.1:8080',
    ])

print(f"✅ CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")

# Database
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fusion_force.urls'

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

WSGI_APPLICATION = 'fusion_force.wsgi.application'

# ========== STATIC FILES ==========
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

# ========== MEDIA FILES ==========
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

print(f"✅ MEDIA_URL: {MEDIA_URL}")
print(f"✅ MEDIA_ROOT: {MEDIA_ROOT}")

# Security - Disable temporarily to fix CSRF
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Other settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== STATIC FILES ==========
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ADD THIS LINE - tells Django where to find static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # This is where your CSS, JS, images should be
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

print(f"✅ STATIC_URL: {STATIC_URL}")
print(f"✅ STATIC_ROOT: {STATIC_ROOT}")
print(f"✅ STATICFILES_DIRS: {STATICFILES_DIRS}")