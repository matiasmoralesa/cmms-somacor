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
    'apps.images',  # Image processing and Firebase integration
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
        'apps.authentication.firebase_auth.FirebaseAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Backward compatibility
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


# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

# Celery Broker (Redis)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Celery Task Settings
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'America/Santiago'
CELERY_ENABLE_UTC = True

# Task execution settings
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_TIME_LIMIT = 1800  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 1500  # 25 minutes

# Worker settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_CONCURRENCY = 5  # Max 5 concurrent tasks per worker

# Retry settings
CELERY_TASK_AUTORETRY_FOR = (Exception,)
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_RETRY_BACKOFF = True
CELERY_TASK_RETRY_BACKOFF_MAX = 600  # 10 minutes
CELERY_TASK_RETRY_JITTER = True

# Result expiration
CELERY_RESULT_EXPIRES = 3600  # 1 hour

# ============================================================================
# FIREBASE CONFIGURATION
# ============================================================================

# Firebase credentials
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL', '')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', '')

# Firebase authentication settings
FIREBASE_TOKEN_CACHE_TTL = int(os.getenv('FIREBASE_TOKEN_CACHE_TTL', '300'))  # 5 minutes default

# ============================================================================
# GOOGLE CLOUD VISION AI CONFIGURATION
# ============================================================================

# Vision AI settings
VISION_AI_ENABLED = os.getenv('VISION_AI_ENABLED', 'True').lower() == 'true'
VISION_AI_MAX_RESULTS = int(os.getenv('VISION_AI_MAX_RESULTS', '10'))

# ============================================================================
# IMAGE PROCESSING CONFIGURATION
# ============================================================================

# Image upload settings
MAX_IMAGE_SIZE_MB = 10  # Maximum upload size
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
COMPRESSED_IMAGE_SIZE_MB = 2  # Target compression size
COMPRESSED_IMAGE_SIZE_BYTES = COMPRESSED_IMAGE_SIZE_MB * 1024 * 1024

# Supported image formats
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# Image processing timeouts
IMAGE_PROCESSING_TIMEOUT = 30  # seconds
IMAGE_ANALYSIS_TIMEOUT = 60  # seconds

# ML Model settings
ANOMALY_DETECTION_THRESHOLD = 0.70  # 70% confidence
DAMAGE_CLASSIFICATION_THRESHOLD = 0.75  # 75% confidence
OCR_CONFIDENCE_THRESHOLD = 0.80  # 80% confidence

# Anomaly types
ANOMALY_TYPES = [
    ('CORROSION', 'Corrosión'),
    ('CRACK', 'Grieta'),
    ('LEAK', 'Fuga'),
    ('WEAR', 'Desgaste'),
    ('DEFORMATION', 'Deformación'),
    ('OTHER', 'Otro'),
]

# Damage types
DAMAGE_TYPES = [
    ('CORROSION', 'Corrosión'),
    ('MECHANICAL_WEAR', 'Desgaste Mecánico'),
    ('ELECTRICAL_FAILURE', 'Falla Eléctrica'),
    ('HYDRAULIC_LEAK', 'Fuga Hidráulica'),
    ('STRUCTURAL_CRACK', 'Grieta Estructural'),
    ('THERMAL_DAMAGE', 'Daño Térmico'),
]

# Severity levels
SEVERITY_LEVELS = [
    ('LOW', 'Bajo'),
    ('MEDIUM', 'Medio'),
    ('HIGH', 'Alto'),
    ('CRITICAL', 'Crítico'),
]

# ============================================================================
# COST OPTIMIZATION CONFIGURATION
# ============================================================================

# Budget limits
MONTHLY_BUDGET_LIMIT_USD = int(os.getenv('MONTHLY_BUDGET_LIMIT_USD', '1000'))
BUDGET_WARNING_THRESHOLD = 0.80  # Alert at 80%
BUDGET_THROTTLE_THRESHOLD = 0.90  # Throttle at 90%

# Caching settings
VISION_AI_CACHE_DAYS = 30
IMAGE_RESULT_CACHE_HOURS = 24

# Batch processing
BATCH_SIZE_IMAGES = 10
BATCH_PROCESSING_ENABLED = True
OFF_PEAK_HOURS_START = 22  # 10 PM
OFF_PEAK_HOURS_END = 6  # 6 AM
