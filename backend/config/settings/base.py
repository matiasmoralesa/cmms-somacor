"""
Django settings for CMMS project.
Base settings shared across all environments.
"""
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    
    # Local apps
    'apps.core',
    'apps.authentication',
    'apps.assets',
    'apps.work_orders',
    'apps.maintenance',
    'apps.inventory',
    'apps.checklists',
    'apps.predictions',
    'apps.notifications',
    'apps.reports',
    'apps.machine_status',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'apps.core.middleware.RequestIDMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.InputSanitizationMiddleware',
    'apps.core.middleware.RateLimitHeadersMiddleware',
    'apps.core.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework - Optimizado para Free Tier
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'apps.core.throttling.SustainedRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    # Límites reducidos para capa gratuita
    'DEFAULT_THROTTLE_RATES': {
        'user': '60/minute',  # Reducido de 100 a 60
        'anon': '10/minute',  # Reducido de 20 a 10
        'burst': '5/min',     # Reducido de 10 a 5
        'sustained': '60/min', # Reducido de 100 a 60
        'daily': '5000/day',  # Reducido de 10000 a 5000
        'webhook': '20/hour', # Reducido de 30 a 20
        'report': '5/hour',   # Reducido de 10 a 5
        'upload': '30/hour',  # Reducido de 50 a 30
        'anon_strict': '3/min', # Reducido de 5 a 3
    }
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Add token blacklist app (commented for initial setup)
# INSTALLED_APPS += ['rest_framework_simplejwt.token_blacklist']

# Email Configuration (for password reset)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@cmms.com')

# Frontend URL (for password reset links)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# DRF Spectacular (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'CMMS API',
    'DESCRIPTION': 'Sistema de Gestión de Mantenimiento Computarizado - API REST completa para gestión de activos, órdenes de trabajo, mantenimiento preventivo y predictivo',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'Equipo CMMS',
        'email': 'soporte@cmms.com',
    },
    'LICENSE': {
        'name': 'Propietario',
    },
    'TAGS': [
        {'name': 'Autenticación', 'description': 'Endpoints de autenticación y gestión de usuarios'},
        {'name': 'Activos', 'description': 'Gestión de activos y vehículos'},
        {'name': 'Órdenes de Trabajo', 'description': 'Creación y seguimiento de órdenes de trabajo'},
        {'name': 'Mantenimiento', 'description': 'Planes de mantenimiento preventivo y predictivo'},
        {'name': 'Inventario', 'description': 'Gestión de repuestos y stock'},
        {'name': 'Checklists', 'description': 'Plantillas y respuestas de checklists'},
        {'name': 'Predicciones', 'description': 'Predicciones de fallas con ML'},
        {'name': 'Notificaciones', 'description': 'Sistema de notificaciones en tiempo real'},
        {'name': 'Reportes', 'description': 'Generación de reportes y KPIs'},
        {'name': 'Configuración', 'description': 'Datos maestros y parámetros del sistema'},
    ],
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
    },
}

# GCP Settings
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', '')
GCP_STORAGE_BUCKET_NAME = os.getenv('GCP_STORAGE_BUCKET_NAME', '')
GCP_PUBSUB_TOPIC_NOTIFICATIONS = os.getenv('GCP_PUBSUB_TOPIC_NOTIFICATIONS', 'notifications')
GCP_PUBSUB_TOPIC_EVENTS = os.getenv('GCP_PUBSUB_TOPIC_EVENTS', 'events')
GCP_PUBSUB_TOPIC_ALERTS = os.getenv('GCP_PUBSUB_TOPIC_ALERTS', 'alerts')

# Vehicle Types (5 predefined types)
VEHICLE_TYPES = [
    ('CAMION_SUPERSUCKER', 'Camión Supersucker'),
    ('CAMIONETA_MDO', 'Camioneta MDO'),
    ('RETROEXCAVADORA_MDO', 'Retroexcavadora MDO'),
    ('CARGADOR_FRONTAL_MDO', 'Cargador Frontal MDO'),
    ('MINICARGADOR_MDO', 'Minicargador MDO'),
]

# Checklist Template Codes
CHECKLIST_CODES = {
    'CAMION_SUPERSUCKER': 'SUPERSUCKER-CH01',
    'CAMIONETA_MDO': 'F-PR-020-CH01',
    'RETROEXCAVADORA_MDO': 'F-PR-034-CH01',
    'CARGADOR_FRONTAL_MDO': 'F-PR-037-CH01',
    'MINICARGADOR_MDO': 'F-PR-040-CH01',
}


# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session Security
SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 86400  # 24 hours

# CSRF Security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False

# Password Validation - Enhanced
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Create logs directory if it doesn't exist
import os
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)


# Cache Configuration - Optimizado para Free Tier
# Usar cache local en desarrollo, Redis opcional en producción
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cmms-dev-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 500,
        }
    }
}

# Sesiones en base de datos para evitar dependencia de Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'
