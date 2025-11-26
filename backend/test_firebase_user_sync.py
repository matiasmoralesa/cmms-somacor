"""
Test script for Firebase user synchronization.
Tests user creation, updates, and custom claims.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Load .env file
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings
from apps.authentication.models import Role
from apps.authentication.firebase_user_service import FirebaseUserService
from apps.authentication.firebase_custom_claims import CustomClaimsService

import firebase_admin
from firebase_admin import credentials

User = get_user_model()

# Initialize Firebase
if not firebase_admin._apps:
    # Get credentials path from environment
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
    
    if not cred_path:
        print("ERROR: FIREBASE_CREDENTIALS_PATH not set in .env file")
        sys.exit(1)
    
    if not os.path.isabs(cred_path):
        # Convert relative path to absolute (relative to backend directory)
        base_dir = Path(__file__).parent
        cred_path = str(base_dir / cred_path)
    
    if not os.path.exists(cred_path):
        print(f"ERROR: Firebase credentials file not found at: {cred_path}")
        sys.exit(1)
    
    database_url = os.getenv('FIREBASE_DATABASE_URL', '')
    storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET', '')
    
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': database_url,
        'storageBucket': storage_bucket,
    })
    print(f"✓ Firebase Admin SDK initialized")
    print(f"  Credentials: {cred_path}")
    print(f"  Database: {database_url}")
    print(f"  Storage: {storage_bucket}")


def test_user_creation():
    """Test creating a new user and syncing to Firebase."""
    print("\n" + "="*80)
    print("TEST 1: User Creation and Firebase Sync")
    print("="*80)
    
    try:
        # Get or create OPERADOR role
        operador_role, _ = Role.objects.get_or_create(
            name=Role.OPERADOR,
            defaults={'description': 'Operador de vehículos'}
        )
        
        # Create a test user
        random_suffix = os.urandom(4).hex()
        test_email = f"test_operador_{random_suffix}@example.com"
        test_rut = f"{random_suffix}-9"
        print(f"\n1. Creating Django user: {test_email}")
        
        user = User.objects.create_user(
            email=test_email,
            password='TestPassword123!',
            first_name='Test',
            last_name='Operador',
            rut=test_rut,
            role=operador_role,
            license_type=User.LICENSE_MUNICIPAL,
            license_expiration_date='2025-12-31',
            license_photo_url='https://example.com/license.jpg'
        )
        
        print(f"   ✓ Django user created with ID: {user.id}")
        
        # Check if Firebase UID was set
        if user.firebase_uid:
            print(f"   ✓ Firebase UID assigned: {user.firebase_uid}")
        else:
            print(f"   ✗ Firebase UID not assigned")
            return False
        
        # Verify Firebase user exists
        print(f"\n2. Verifying Firebase user...")
        firebase_user = FirebaseUserService.get_firebase_user(user.firebase_uid)
        
        if firebase_user:
            print(f"   ✓ Firebase user found:")
            print(f"     - Email: {firebase_user['email']}")
            print(f"     - Display Name: {firebase_user['display_name']}")
            print(f"     - Disabled: {firebase_user['disabled']}")
        else:
            print(f"   ✗ Firebase user not found")
            return False
        
        # Check custom claims
        print(f"\n3. Checking custom claims...")
        claims = CustomClaimsService.get_user_claims(user.firebase_uid)
        
        if claims:
            print(f"   ✓ Custom claims found:")
            print(f"     - Role: {claims.get('role')}")
            print(f"     - Is Operador: {claims.get('is_operador')}")
            print(f"     - License Valid: {claims.get('license', {}).get('is_valid')}")
            print(f"     - Permissions: {len(claims.get('permissions', []))} permissions")
        else:
            print(f"   ✗ Custom claims not found")
            return False
        
        print(f"\n✓ TEST 1 PASSED")
        return user
        
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_user_update(user):
    """Test updating a user and syncing to Firebase."""
    print("\n" + "="*80)
    print("TEST 2: User Update and Firebase Sync")
    print("="*80)
    
    try:
        print(f"\n1. Updating user email...")
        new_email = f"updated_{os.urandom(4).hex()}@example.com"
        user.email = new_email
        user.save()
        
        print(f"   ✓ Django user email updated to: {new_email}")
        
        # Verify Firebase user was updated
        print(f"\n2. Verifying Firebase user update...")
        firebase_user = FirebaseUserService.get_firebase_user(user.firebase_uid)
        
        if firebase_user and firebase_user['email'] == new_email:
            print(f"   ✓ Firebase user email updated: {firebase_user['email']}")
        else:
            print(f"   ✗ Firebase user email not updated")
            return False
        
        print(f"\n✓ TEST 2 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_role_change(user):
    """Test changing user role and updating custom claims."""
    print("\n" + "="*80)
    print("TEST 3: Role Change and Custom Claims Update")
    print("="*80)
    
    try:
        # Get or create SUPERVISOR role
        supervisor_role, _ = Role.objects.get_or_create(
            name=Role.SUPERVISOR,
            defaults={'description': 'Supervisor de operaciones'}
        )
        
        print(f"\n1. Changing user role to SUPERVISOR...")
        user.role = supervisor_role
        user.save()
        
        print(f"   ✓ Django user role updated")
        
        # Check updated custom claims
        print(f"\n2. Checking updated custom claims...")
        claims = CustomClaimsService.get_user_claims(user.firebase_uid)
        
        if claims:
            print(f"   ✓ Custom claims updated:")
            print(f"     - Role: {claims.get('role')}")
            print(f"     - Is Supervisor: {claims.get('is_supervisor')}")
            print(f"     - Can View All Resources: {claims.get('can_view_all_resources')}")
        else:
            print(f"   ✗ Custom claims not found")
            return False
        
        print(f"\n✓ TEST 3 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_user_deactivation(user):
    """Test deactivating a user and syncing to Firebase."""
    print("\n" + "="*80)
    print("TEST 4: User Deactivation and Firebase Sync")
    print("="*80)
    
    try:
        print(f"\n1. Deactivating user...")
        user.is_active = False
        user.save()
        
        print(f"   ✓ Django user deactivated")
        
        # Verify Firebase user was disabled
        print(f"\n2. Verifying Firebase user disabled...")
        firebase_user = FirebaseUserService.get_firebase_user(user.firebase_uid)
        
        if firebase_user and firebase_user['disabled']:
            print(f"   ✓ Firebase user disabled: {firebase_user['disabled']}")
        else:
            print(f"   ✗ Firebase user not disabled")
            return False
        
        print(f"\n✓ TEST 4 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST 4 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_user(user):
    """Clean up test user."""
    print("\n" + "="*80)
    print("CLEANUP: Deleting Test User")
    print("="*80)
    
    try:
        firebase_uid = user.firebase_uid
        user_id = user.id
        
        print(f"\n1. Deleting Django user...")
        user.delete()
        print(f"   ✓ Django user deleted")
        
        # Verify Firebase user was deleted
        print(f"\n2. Verifying Firebase user deleted...")
        firebase_user = FirebaseUserService.get_firebase_user(firebase_uid)
        
        if firebase_user is None:
            print(f"   ✓ Firebase user deleted")
        else:
            print(f"   ✗ Firebase user still exists")
            return False
        
        print(f"\n✓ CLEANUP COMPLETED")
        return True
        
    except Exception as e:
        print(f"\n✗ CLEANUP FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("FIREBASE USER SYNCHRONIZATION TESTS")
    print("="*80)
    
    # Test 1: User creation
    user = test_user_creation()
    if not user:
        print("\n✗ Tests failed at user creation")
        return
    
    # Test 2: User update
    if not test_user_update(user):
        print("\n✗ Tests failed at user update")
        cleanup_test_user(user)
        return
    
    # Test 3: Role change
    if not test_role_change(user):
        print("\n✗ Tests failed at role change")
        cleanup_test_user(user)
        return
    
    # Test 4: User deactivation
    if not test_user_deactivation(user):
        print("\n✗ Tests failed at user deactivation")
        cleanup_test_user(user)
        return
    
    # Cleanup
    cleanup_test_user(user)
    
    print("\n" + "="*80)
    print("✓ ALL TESTS PASSED")
    print("="*80)


if __name__ == '__main__':
    main()
