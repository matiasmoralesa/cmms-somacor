"""
Management command to create test users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.authentication.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test users for development and testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users...')

        # Create superuser
        if not User.objects.filter(email='admin@cmms.com').exists():
            admin = User.objects.create_superuser(
                email='admin@cmms.com',
                password='admin123',
                first_name='Admin',
                last_name='Sistema',
                role=Role.ADMIN
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Superuser created: {admin.email}'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Superuser already exists'))

        # Create manager
        if not User.objects.filter(email='manager@cmms.com').exists():
            manager = User.objects.create_user(
                email='manager@cmms.com',
                password='manager123',
                first_name='Manager',
                last_name='Test',
                role=Role.MANAGER
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Manager created: {manager.email}'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Manager already exists'))

        # Create technician
        if not User.objects.filter(email='tech@cmms.com').exists():
            tech = User.objects.create_user(
                email='tech@cmms.com',
                password='tech123',
                first_name='Technician',
                last_name='Test',
                role=Role.TECHNICIAN
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Technician created: {tech.email}'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Technician already exists'))

        # Create operator
        if not User.objects.filter(email='operator@cmms.com').exists():
            operator = User.objects.create_user(
                email='operator@cmms.com',
                password='operator123',
                first_name='Operator',
                last_name='Test',
                role=Role.OPERATOR
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Operator created: {operator.email}'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Operator already exists'))

        self.stdout.write(self.style.SUCCESS('\n=== Test Users Created ==='))
        self.stdout.write('Admin:      admin@cmms.com / admin123')
        self.stdout.write('Manager:    manager@cmms.com / manager123')
        self.stdout.write('Technician: tech@cmms.com / tech123')
        self.stdout.write('Operator:   operator@cmms.com / operator123')
