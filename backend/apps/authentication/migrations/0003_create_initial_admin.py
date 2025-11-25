# Generated migration to create initial admin user

from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_initial_admin(apps, schema_editor):
    """Create initial admin user if it doesn't exist"""
    User = apps.get_model('authentication', 'User')
    Role = apps.get_model('authentication', 'Role')
    
    # Get or create ADMIN role
    admin_role, _ = Role.objects.get_or_create(
        name='ADMIN',
        defaults={'description': 'Administrator role'}
    )
    
    # Check if any admin exists
    if not User.objects.filter(email='admin@cmms.com').exists():
        User.objects.create(
            email='admin@cmms.com',
            password=make_password('admin123'),
            first_name='Admin',
            last_name='Sistema',
            rut='11111111-1',
            role=admin_role,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        print("✓ Usuario admin creado: admin@cmms.com / admin123")
    else:
        print("⚠ Ya existe un usuario admin")


def reverse_migration(apps, schema_editor):
    """Remove initial admin user"""
    User = apps.get_model('authentication', 'User')
    User.objects.filter(email='admin@cmms.com').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_add_telegram_chat_id'),
    ]

    operations = [
        migrations.RunPython(create_initial_admin, reverse_migration),
    ]
