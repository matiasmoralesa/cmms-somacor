"""
Images app configuration.
"""
from django.apps import AppConfig


class ImagesConfig(AppConfig):
    """Configuration for the images app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.images'
    verbose_name = 'Image Processing'
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.images.signals  # noqa
