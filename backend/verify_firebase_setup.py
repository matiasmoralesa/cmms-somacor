#!/usr/bin/env python
"""
Script to verify Firebase setup and configuration.
Run this after setting up Firebase credentials to ensure everything is working.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings
import firebase_admin
from firebase_admin import credentials, auth
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def verify_firebase_setup():
    """Verify Firebase configuration and connectivity."""
    print("\n" + "="*60)
    print("Firebase Setup Verification")
    print("="*60 + "\n")
    
    # Check 1: Environment variables
    print_info("Checking environment variables...")
    
    firebase_creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
    firebase_db_url = getattr(settings, 'FIREBASE_DATABASE_URL', None)
    firebase_storage_bucket = getattr(settings, 'FIREBASE_STORAGE_BUCKET', None)
    
    if not firebase_creds_path:
        print_error("FIREBASE_CREDENTIALS_PATH not set in settings")
        return False
    else:
        print_success(f"FIREBASE_CREDENTIALS_PATH: {firebase_creds_path}")
    
    if not firebase_db_url:
        print_warning("FIREBASE_DATABASE_URL not set (optional)")
    else:
        print_success(f"FIREBASE_DATABASE_URL: {firebase_db_url}")
    
    if not firebase_storage_bucket:
        print_warning("FIREBASE_STORAGE_BUCKET not set (optional)")
    else:
        print_success(f"FIREBASE_STORAGE_BUCKET: {firebase_storage_bucket}")
    
    # Check 2: Credentials file exists
    print_info("\nChecking credentials file...")
    
    if not os.path.exists(firebase_creds_path):
        print_error(f"Credentials file not found: {firebase_creds_path}")
        print_info("Please download the service account key from Firebase Console")
        return False
    else:
        print_success(f"Credentials file exists: {firebase_creds_path}")
    
    # Check 3: Initialize Firebase Admin SDK
    print_info("\nInitializing Firebase Admin SDK...")
    
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_creds_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': firebase_db_url,
                'storageBucket': firebase_storage_bucket,
            })
        print_success("Firebase Admin SDK initialized successfully")
    except Exception as e:
        print_error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        return False
    
    # Check 4: Test Firebase Authentication
    print_info("\nTesting Firebase Authentication...")
    
    try:
        # Try to list users (will fail if no users exist, but that's ok)
        users = auth.list_users(max_results=1)
        print_success("Firebase Authentication is accessible")
        
        # Count total users
        user_count = 0
        for user in auth.list_users().iterate_all():
            user_count += 1
        
        print_info(f"Total Firebase users: {user_count}")
        
    except Exception as e:
        print_error(f"Failed to access Firebase Authentication: {str(e)}")
        print_info("Make sure Firebase Authentication is enabled in Firebase Console")
        return False
    
    # Check 5: Test creating a test user (optional)
    print_info("\nTesting user creation (optional)...")
    
    test_email = "firebase-test@example.com"
    test_uid = None
    
    try:
        # Try to create a test user
        test_user = auth.create_user(
            email=test_email,
            password="TestPass123!",
            display_name="Firebase Test User"
        )
        test_uid = test_user.uid
        print_success(f"Test user created successfully: {test_uid}")
        
        # Try to get the user
        retrieved_user = auth.get_user(test_uid)
        print_success(f"Test user retrieved successfully: {retrieved_user.email}")
        
        # Try to update the user
        auth.update_user(
            test_uid,
            display_name="Firebase Test User (Updated)"
        )
        print_success("Test user updated successfully")
        
        # Try to set custom claims
        auth.set_custom_user_claims(test_uid, {
            'role': 'TEST',
            'test': True
        })
        print_success("Custom claims set successfully")
        
        # Verify custom claims
        user_with_claims = auth.get_user(test_uid)
        if user_with_claims.custom_claims:
            print_success(f"Custom claims verified: {user_with_claims.custom_claims}")
        
        # Clean up: delete test user
        auth.delete_user(test_uid)
        print_success("Test user deleted successfully")
        
    except auth.EmailAlreadyExistsError:
        print_warning(f"Test user already exists: {test_email}")
        print_info("Skipping user creation test")
    except Exception as e:
        print_error(f"User creation test failed: {str(e)}")
        # Try to clean up if user was created
        if test_uid:
            try:
                auth.delete_user(test_uid)
                print_info("Cleaned up test user")
            except:
                pass
        return False
    
    # Summary
    print("\n" + "="*60)
    print_success("Firebase setup verification completed successfully!")
    print("="*60 + "\n")
    
    print_info("Next steps:")
    print("  1. Run database migration to add firebase_uid field")
    print("  2. Implement FirebaseAuthentication class")
    print("  3. Update frontend to use Firebase Authentication")
    
    return True

if __name__ == '__main__':
    try:
        success = verify_firebase_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
