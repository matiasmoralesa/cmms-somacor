"""
Django management command to initialize system roles and permissions
Usage: python manage.py init_roles_permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.authentication.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize system roles (ADMIN, SUPERVISOR, OPERADOR)'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing system roles...'))
        
        roles_data = [
            {
                'name': 'ADMIN',
                'description': 'Administrador del sistema con acceso completo'
            },
            {
                'name': 'SUPERVISOR',
                'description': 'Supervisor de mantenimiento con acceso a gestión operativa'
            },
            {
                'name': 'OPERADOR',
                'description': 'Técnico/Operador con acceso limitado a tareas asignadas'
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role.name}')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'- Role already exists: {role.name}')
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS(f'Roles created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Roles already existing: {existing_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total roles: {Role.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ System roles initialized successfully!'))
