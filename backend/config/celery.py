"""
Celery configuration for CMMS project.
Configures task queues, routing, and worker settings.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Create Celery app
app = Celery('cmms')

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Configure task routes for priority queues
app.conf.task_routes = {
    # High priority - Critical image analysis
    'apps.images.tasks.process_inspection_photo': {'queue': 'high_priority'},
    'apps.images.tasks.analyze_critical_anomaly': {'queue': 'high_priority'},
    
    # Normal priority - Standard processing
    'apps.images.tasks.analyze_anomalies': {'queue': 'normal'},
    'apps.images.tasks.extract_text_ocr': {'queue': 'normal'},
    'apps.images.tasks.classify_damage': {'queue': 'normal'},
    'apps.images.tasks.generate_image_report': {'queue': 'normal'},
    
    # Batch processing - Non-urgent bulk operations
    'apps.images.tasks.batch_process_images': {'queue': 'batch'},
    'apps.images.tasks.generate_comparison_report': {'queue': 'batch'},
    'apps.images.tasks.archive_old_messages': {'queue': 'batch'},
    'apps.images.tasks.cleanup_old_images': {'queue': 'batch'},
    
    # ML training - Long-running model training
    'apps.images.tasks.retrain_anomaly_model': {'queue': 'ml_training'},
    'apps.images.tasks.retrain_damage_model': {'queue': 'ml_training'},
    'apps.images.tasks.evaluate_model_performance': {'queue': 'ml_training'},
}

# Configure periodic tasks (Celery Beat)
app.conf.beat_schedule = {
    # Archive old chat messages daily at 2 AM
    'archive-old-messages': {
        'task': 'apps.images.tasks.archive_old_messages',
        'schedule': crontab(hour=2, minute=0),
    },
    # Cleanup old cached images weekly on Sunday at 3 AM
    'cleanup-old-images': {
        'task': 'apps.images.tasks.cleanup_old_images',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
    },
    # Generate daily analytics report at 6 AM
    'generate-daily-analytics': {
        'task': 'apps.images.tasks.generate_daily_analytics',
        'schedule': crontab(hour=6, minute=0),
    },
    # Check budget usage every 6 hours
    'check-budget-usage': {
        'task': 'apps.images.tasks.check_budget_usage',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}

# Task execution settings
app.conf.task_default_priority = 5
app.conf.task_queue_max_priority = 10

# Result backend settings
app.conf.result_extended = True
app.conf.result_backend_transport_options = {
    'master_name': 'mymaster',
    'visibility_timeout': 3600,
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
