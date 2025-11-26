"""
WSGI config for CMMS project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Use Railway settings by default, fallback to production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

application = get_wsgi_application()
