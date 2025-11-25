import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.authentication.models import User, Role

try:
    # Check if admin user exists
    admin_user = User.objects.filter(email='admin@cmms.com').first()
    if admin_user:
        print(f"✓ Admin user exists: {admin_user.email}")
        print(f"  - Active: {admin_user.is_active}")
        print(f"  - Role: {admin_user.role.name if admin_user.role else 'No role'}")
    else:
        print("✗ Admin user does not exist")
        
        # Check if ADMIN role exists
        admin_role = Role.objects.filter(name='ADMIN').first()
        if not admin_role:
            print("Creating ADMIN role...")
            admin_role = Role.objects.create(name='ADMIN', description='Administrator')
        
        # Create admin user
        print("Creating admin user...")
        admin_user = User.objects.create_superuser(
            email='admin@cmms.com',
            password='admin123',
            first_name='Admin',
            last_name='Sistema',
            rut='11111111-1',
            role=admin_role
        )
        print(f"✓ Admin user created: {admin_user.email}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
