"""
Management command to create admin user
"""
from django.core.management.base import BaseCommand
from apps.authentication.models import User, Role
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create admin user and test users'

    def handle(self, *args, **options):
        self.stdout.write('Creating users...\n')
        
        # Create roles
        admin_role, created = Role.objects.get_or_create(
            name=Role.ADMIN,
            defaults={'description': 'Administrador del sistema'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Rol ADMIN creado'))
        
        supervisor_role, created = Role.objects.get_or_create(
            name=Role.SUPERVISOR,
            defaults={'description': 'Supervisor de mantenimiento'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Rol SUPERVISOR creado'))
        
        operador_role, created = Role.objects.get_or_create(
            name=Role.OPERADOR,
            defaults={'description': 'Operador de equipos'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Rol OPERADOR creado'))
        
        # Create admin user
        if User.objects.filter(email='admin@cmms.com').exists():
            self.stdout.write('- Usuario admin@cmms.com ya existe')
        else:
            User.objects.create_user(
                email='admin@cmms.com',
                password='admin123',
                first_name='Admin',
                last_name='Sistema',
                rut='11111111-1',
                role=admin_role,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuario admin@cmms.com creado'))
        
        # Create supervisor
        if User.objects.filter(email='supervisor@cmms.com').exists():
            self.stdout.write('- Usuario supervisor@cmms.com ya existe')
        else:
            User.objects.create_user(
                email='supervisor@cmms.com',
                password='supervisor123',
                first_name='Juan',
                last_name='Supervisor',
                rut='22222222-2',
                role=supervisor_role
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuario supervisor@cmms.com creado'))
        
        # Create operador
        if User.objects.filter(email='operador@cmms.com').exists():
            self.stdout.write('- Usuario operador@cmms.com ya existe')
        else:
            User.objects.create_user(
                email='operador@cmms.com',
                password='operador123',
                first_name='Pedro',
                last_name='Operador',
                rut='33333333-3',
                role=operador_role,
                license_type='MUNICIPAL',
                license_expiration_date=date.today() + timedelta(days=365),
                license_photo_url='https://example.com/license.jpg'
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuario operador@cmms.com creado'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Proceso completado'))
        self.stdout.write('\nUsuarios disponibles:')
        self.stdout.write('  - admin@cmms.com / admin123 (ADMIN)')
        self.stdout.write('  - supervisor@cmms.com / supervisor123 (SUPERVISOR)')
        self.stdout.write('  - operador@cmms.com / operador123 (OPERADOR)')
