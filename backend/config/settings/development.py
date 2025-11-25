"""Development settings"""
from .base import *
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ['*']  # Permitir todos los hosts en desarrollo

# Database
# Use SQLite for development if DATABASE_URL is not set or is sqlite
database_url = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
if database_url.startswith('sqlite'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600
        )
    }

# CORS Settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Cache (Local memory for development - no Redis required)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Uncomment below to use Redis if available
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

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
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Vertex AI Configuration (Development - uses local model)
USE_VERTEX_AI = False
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', None)
GCP_LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
VERTEX_AI_ENDPOINT_ID = os.getenv('VERTEX_AI_ENDPOINT_ID', None)
