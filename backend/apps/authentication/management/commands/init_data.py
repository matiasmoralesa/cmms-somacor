"""
Management command to initialize basic data (roles and admin user)
"""
from django.core.management.base import BaseCommand
from apps.authentication.models import Role, User


class Command(BaseCommand):
    help = 'Initialize basic data: roles and admin user'

    def handle(self, *args, **options):
        self.stdout.write('Initializing basic data...')
        
        # Create roles
        roles_created = 0
        for role_name, role_display in Role.ROLE_CHOICES:
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': f'Rol de {role_display}'}
            )
            if created:
                roles_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role_display}')
                )
        
        if roles_created == 0:
            self.stdout.write('  Roles already exist')
        
        # Create admin user
        admin_role = Role.objects.get(name=Role.ADMIN)
        admin_email = 'admin@cmms.com'
        
        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_superuser(
                email=admin_email,
                password='admin123',
                first_name='Admin',
                last_name='User',
                rut='11111111-1',
                role=admin_role
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created admin user: {admin_email}')
            )
            self.stdout.write(
                self.style.WARNING(f'  Password: admin123')
            )
        else:
            self.stdout.write('  Admin user already exists')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Initialization complete!'))
