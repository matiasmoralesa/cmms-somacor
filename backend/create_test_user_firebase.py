#!/usr/bin/env python
"""
Script to create a test user in both Firebase and Django.
This allows testing the complete authentication flow.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from apps.authentication.models import User, Role
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Initialize Firebase
if not firebase_admin._apps:
    import os
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    cred_path = base_dir / 'cmms-somacor-prod-firebase-adminsdk-fbsvc-29f640a5c9.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def create_test_user():
    """Create a test user in both Firebase and Django."""
    print("\n" + "="*70)
    print("Create Test User for Firebase Authentication")
    print("="*70 + "\n")
    
    # Test user credentials
    test_email = "test@cmms.com"
    test_password = "Test123456"
    test_first_name = "Test"
    test_last_name = "User"
    test_rut = "88888888-8"
    
    print_info(f"Creating test user: {test_email}")
    print_info(f"Password: {test_password}")
    print_warning("Remember these credentials for testing!\n")
    
    # Step 1: Check if user already exists in Firebase
    print_info("Step 1: Checking Firebase...")
    firebase_uid = None
    
    try:
        existing_firebase_user = firebase_auth.get_user_by_email(test_email)
        firebase_uid = existing_firebase_user.uid
        print_warning(f"User already exists in Firebase: {firebase_uid}")
    except firebase_auth.UserNotFoundError:
        print_info("User not found in Firebase, creating...")
        
        try:
            firebase_user = firebase_auth.create_user(
                email=test_email,
                password=test_password,
                display_name=f"{test_first_name} {test_last_name}",
                email_verified=True
            )
            firebase_uid = firebase_user.uid
            print_success(f"Firebase user created: {firebase_uid}")
        except Exception as e:
            print_error(f"Failed to create Firebase user: {str(e)}")
            return False
    
    # Step 2: Check if user exists in Django
    print_info("\nStep 2: Checking Django...")
    
    try:
        django_user = User.objects.get(email=test_email)
        print_warning(f"User already exists in Django: {django_user.email}")
        
        # Update firebase_uid if not set
        if not django_user.firebase_uid:
            django_user.firebase_uid = firebase_uid
            django_user.save()
            print_success("Updated Django user with firebase_uid")
        else:
            print_info(f"Django user already has firebase_uid: {django_user.firebase_uid}")
            
    except User.DoesNotExist:
        print_info("User not found in Django, creating...")
        
        # Get or create ADMIN role
        admin_role, _ = Role.objects.get_or_create(
            name=Role.ADMIN,
            defaults={'description': 'Administrator role'}
        )
        
        try:
            django_user = User.objects.create_user(
                email=test_email,
                password=test_password,
                first_name=test_first_name,
                last_name=test_last_name,
                rut=test_rut,
                role=admin_role,
                firebase_uid=firebase_uid
            )
            print_success(f"Django user created: {django_user.email}")
        except Exception as e:
            print_error(f"Failed to create Django user: {str(e)}")
            return False
    
    # Step 3: Set custom claims in Firebase
    print_info("\nStep 3: Setting custom claims in Firebase...")
    
    try:
        custom_claims = {
            'role': django_user.role.name,
            'role_display': django_user.role.get_name_display(),
            'permissions': list(django_user.role.permissions.values_list('code', flat=True)),
            'is_admin': django_user.is_admin(),
            'is_supervisor': django_user.is_supervisor(),
            'is_operador': django_user.is_operador(),
            'employee_status': django_user.employee_status,
        }
        
        firebase_auth.set_custom_user_claims(firebase_uid, custom_claims)
        print_success("Custom claims set successfully")
        print_info(f"Claims: {custom_claims}")
        
    except Exception as e:
        print_error(f"Failed to set custom claims: {str(e)}")
        print_warning("User created but custom claims not set")
    
    # Summary
    print("\n" + "="*70)
    print_success("Test user created successfully!")
    print("="*70 + "\n")
    
    print_info("User Details:")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    print(f"  Firebase UID: {firebase_uid}")
    print(f"  Django ID: {django_user.id}")
    print(f"  Role: {django_user.role.get_name_display()}")
    
    print_info("\nHow to test:")
    print("  1. Go to your frontend application")
    print(f"  2. Login with: {test_email} / {test_password}")
    print("  3. Check browser console for Firebase token")
    print("  4. Make API requests to backend")
    print("  5. Backend should authenticate you automatically")
    
    print_info("\nTest API call:")
    print("  curl -H 'Authorization: Bearer <firebase-token>' \\")
    print("       http://localhost:8000/api/v1/auth/profile/")
    
    return True

if __name__ == '__main__':
    try:
        success = create_test_user()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
