"""
Django management command to generate demo data for UAT
Usage: python manage.py generate_demo_data
"""
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.authentication.models import User, Role
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
from apps.maintenance.models import MaintenancePlan
from apps.inventory.models import SparePart
from apps.checklists.models import ChecklistTemplate
from apps.predictions.models import FailurePrediction, Alert
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = 'Generate comprehensive demo data for user acceptance testing'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Generating demo data...'))
        
        # Import and run the generator
        from tests.fixtures.demo_data import DemoDataGenerator
        generator = DemoDataGenerator()
        generator.generate_all()
        
        self.stdout.write(self.style.SUCCESS('Demo data generation complete!'))
