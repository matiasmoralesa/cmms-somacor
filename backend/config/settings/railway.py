"""
Railway.app specific settings
Simplified configuration without Google Cloud dependencies
"""
from .base import *
import dj_database_url
import os

DEBUG = False

# Hosts
ALLOWED_HOSTS = ['*']

# Database - Railway provides DATABASE_URL automatically
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Security Settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# CSRF Settings
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://cmms-somacor-prod.web.app',
    'https://cmms-somacor-prod.firebaseapp.com',
]

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    'https://cmms-somacor-prod.web.app',
    'https://cmms-somacor-prod.firebaseapp.com',
]
CORS_ALLOW_CREDENTIALS = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files - Local filesystem only
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Cache - Local memory
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cmms-cache',
    }
}

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Firebase credentials from environment variable
if os.getenv('FIREBASE_CREDENTIALS'):
    import json
    FIREBASE_CREDENTIALS = json.loads(os.getenv('FIREBASE_CREDENTIALS'))

# Logging
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
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
