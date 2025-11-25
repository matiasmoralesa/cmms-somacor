#!/usr/bin/env python
"""
Script to fix admin user by adding RUT
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.authentication.models import User
from django.contrib.auth.hashers import make_password

def fix_admin_user():
    """Fix admin user by adding RUT"""
    print("Fixing admin user...")
    
    try:
        # Try to get existing admin
        admin = User.objects.get(email='admin@cmms.com')
        print(f"Found existing admin: {admin.email}")
        
        # Update RUT if missing
        if not admin.rut:
            admin.rut = '11111111-1'
            admin.save()
            print("✓ RUT added to admin user")
        else:
            print(f"✓ Admin already has RUT: {admin.rut}")
            
    except User.DoesNotExist:
        print("⚠️  Admin user not found")
        print("Creating new admin user...")
        
        from apps.authentication.models import Role
        
        # Get or create ADMIN role
        admin_role, _ = Role.objects.get_or_create(
            name='ADMIN',
            defaults={'description': 'Administrator role'}
        )
        
        # Create admin user
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
        print("✓ Admin user created with RUT")
    
    print("\nDone!")

if __name__ == '__main__':
    fix_admin_user()
