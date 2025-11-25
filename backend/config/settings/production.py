"""Production settings for GCP Cloud Run - Optimized for Free Tier"""
from .base import *
import dj_database_url
import os

DEBUG = False

# Permitir todos los hosts de Cloud Run
ALLOWED_HOSTS = [
    '*',  # Permitir todos los hosts
    'cmms-backend-service-888881509782.us-central1.run.app',
    'cmms-backend-ufxpd3tbia-uc.a.run.app',
    'localhost',
    '127.0.0.1',
]

# Database - Cloud SQL Free Tier (db-f1-micro)
# Optimizado para capa gratuita con límites de conexión reducidos
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=300,  # Reducido a 5 minutos para capa gratuita
            conn_health_checks=True,
        )
    }
elif os.getenv('DB_HOST', '').startswith('/cloudsql'):
    # Conexión via Unix Socket (Cloud Run) - Optimizado para Free Tier
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'cmms_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),  # /cloudsql/PROJECT:REGION:INSTANCE
            'OPTIONS': {
                'connect_timeout': 10,
                'options': '-c statement_timeout=30000'  # 30 segundos timeout
            },
            'CONN_MAX_AGE': 300,  # 5 minutos para capa gratuita
            'ATOMIC_REQUESTS': True,
        }
    }
else:
    # Fallback a configuración normal
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=300,
            conn_health_checks=True,
        )
    }

# Optimización de pool de conexiones para Free Tier
# db-f1-micro soporta máximo 25 conexiones simultáneas
DATABASES['default']['CONN_MAX_AGE'] = 300  # 5 minutos
if 'OPTIONS' not in DATABASES['default']:
    DATABASES['default']['OPTIONS'] = {}
DATABASES['default']['OPTIONS']['connect_timeout'] = 10

# Security Settings (Cloud Run maneja SSL)
SECURE_SSL_REDIRECT = False  # Cloud Run ya maneja HTTPS
SESSION_COOKIE_SECURE = False  # Temporalmente deshabilitado para admin
CSRF_COOKIE_SECURE = False  # Temporalmente deshabilitado para admin
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Permitir iframe en mismo origen
SECURE_HSTS_SECONDS = 0  # Temporalmente deshabilitado
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# CSRF Settings - Configuración permisiva temporal
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://cmms-backend-ufxpd3tbia-uc.a.run.app',
    'https://cmms-backend-888881509782.us-central1.run.app',
    'https://cmms-somacor.web.app',
    'https://cmms-somacor.firebaseapp.com',
    'https://cmms-somacor-prod.web.app',
    'https://cmms-somacor-prod.firebaseapp.com',
    'https://cmms-somacor-produccion.web.app',
]

# CORS Settings - Permitir acceso desde Cloud Storage
CORS_ALLOWED_ORIGINS = [
    'https://cmms-somacor.web.app',
    'https://cmms-somacor.firebaseapp.com',
    'https://cmms-somacor-prod.web.app',
    'https://cmms-somacor-prod.firebaseapp.com',
    'https://cmms-somacor-produccion.web.app',
    'https://storage.googleapis.com',
    'https://storage.cloud.google.com',
]
CORS_ALLOW_ALL_ORIGINS = True  # Permitir todos los orígenes
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Cloud Storage)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME', 'argon-edge-478500-i8-cmms-documents')
GS_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'argon-edge-478500-i8')

# Cache - Optimizado para Free Tier
# Usar cache local en memoria para evitar costos de Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cmms-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Límite de entradas para no consumir mucha RAM
        }
    }
}

# Desactivar cache de sesiones para reducir uso de memoria
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Usar DB en lugar de cache

# Cloud Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
