# settings.py - Complete with Cloudinary Integration & Increased Upload Limits
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-123')

# Keep DEBUG as True for now
DEBUG = True

# ========== ALLOWED_HOSTS ==========
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'fusionforcellc-production.up.railway.app',
    '.railway.app',
    '.pamela-fusionforce.com',
    'www.pamela-fusionforce.com',
    'pamela-fusionforce.com',
]

# ========== CSRF_TRUSTED_ORIGINS ==========
CSRF_TRUSTED_ORIGINS = [
    'https://fusionforcellc-production.up.railway.app',
    'https://*.railway.app',
    'https://*.pamela-fusionforce.com',
    'https://www.pamela-fusionforce.com',
    'https://pamela-fusionforce.com',
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

# ========== DATABASE ==========
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

# ========== INSTALLED APPS ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    
    # Cloudinary
    'cloudinary',
    'cloudinary_storage',
    
    # Local apps
    'main',
]

# ========== MIDDLEWARE ==========
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

# ========== TEMPLATES ==========
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
                # Add Cloudinary context processor
                'main.views.cloudinary_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'fusion_force.wsgi.application'

# ========== STATIC FILES ==========
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Your CSS, JS, images
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

print(f"✅ STATIC_URL: {STATIC_URL}")
print(f"✅ STATIC_ROOT: {STATIC_ROOT}")
print(f"✅ STATICFILES_DIRS: {STATICFILES_DIRS}")

# ========== MEDIA FILES - CLOUDINARY ==========
# Use Cloudinary for media storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Cloudinary Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dtunaasgv'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# ========== UPDATED CLOUDINARY SETTINGS WITH INCREASED LIMITS ==========
CLOUDINARY = {
    'PROCESS_URLS': True,
    'EXIF': True,
    'ALLOW_FORMATS': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'mp4', 'mov', 'avi', 'pdf'],
    'DEFAULT_TRANSFORMATIONS': {
        'quality': 'auto:best',
        'fetch_format': 'auto',
    },
    # ========== FIX: INCREASE MAX UPLOAD SIZE ==========
    'MAX_UPLOAD_SIZE': 20971520,  # 20 MB (increased from 10MB)
    'CHUNK_SIZE': 6000000,  # 6MB chunks for large files
    'USE_CHUNKED_ENCODING': True,
    # Auto-resize large images before upload
    'TRANSFORMATION': {
        'width': 1920,
        'height': 1080,
        'crop': 'limit',
        'quality': 'auto:best',
    }
}

print(f"✅ Cloudinary Cloud Name: {CLOUDINARY_STORAGE['CLOUD_NAME']}")
print(f"✅ Cloudinary Configured: {bool(CLOUDINARY_STORAGE['API_KEY'] and CLOUDINARY_STORAGE['API_SECRET'])}")
print(f"✅ Cloudinary Max Upload Size: {CLOUDINARY.get('MAX_UPLOAD_SIZE', 10485760) / 1024 / 1024} MB")

# ========== FILE UPLOAD SETTINGS ==========
# Increase Django's file upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Fallback media settings (in case Cloudinary fails)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

print(f"✅ MEDIA_URL: {MEDIA_URL}")
print(f"✅ MEDIA_ROOT: {MEDIA_ROOT}")
print(f"✅ FILE_UPLOAD_MAX_MEMORY_SIZE: {FILE_UPLOAD_MAX_MEMORY_SIZE / 1024 / 1024} MB")

# ========== SECURITY ==========
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Set to True in production
SESSION_COOKIE_SECURE = False  # Set to True in production
CSRF_COOKIE_SECURE = False  # Set to True in production
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ========== PASSWORD VALIDATORS ==========
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========== INTERNATIONALIZATION ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========== DEFAULT AUTO FIELD ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== LOGGING ==========
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'main': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cloudinary': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

print("="*60)
print("✅ Settings loaded successfully!")
print(f"✅ DEBUG: {DEBUG}")
print(f"✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print("="*60)