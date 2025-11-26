#!/usr/bin/env python
"""
Script to connect and verify Firebase configuration.
Run this after downloading the service account key.
"""
import os
import sys

# Check if .env file exists
if not os.path.exists('.env'):
    print("❌ .env file not found!")
    print("Please create a .env file based on .env.example")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
except Exception as e:
    print(f"❌ Error setting up Django: {e}")
    sys.exit(1)

from django.conf import settings
import firebase_admin
from firebase_admin import credentials, auth
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def main():
    print("\n" + "="*70)
    print("Firebase Connection Setup")
    print("="*70 + "\n")
    
    # Step 1: Check environment variables
    print_info("Step 1: Checking environment variables...")
    
    creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
    db_url = getattr(settings, 'FIREBASE_DATABASE_URL', None)
    storage_bucket = getattr(settings, 'FIREBASE_STORAGE_BUCKET', None)
    
    if not creds_path:
        print_error("FIREBASE_CREDENTIALS_PATH not set in .env")
        print_info("\nTo fix this:")
        print("  1. Download service account key from Firebase Console")
        print("  2. Save it to a secure location")
        print("  3. Update FIREBASE_CREDENTIALS_PATH in backend/.env")
        return False
    
    print_success(f"FIREBASE_CREDENTIALS_PATH: {creds_path}")
    
    if db_url:
        print_success(f"FIREBASE_DATABASE_URL: {db_url}")
    else:
        print_warning("FIREBASE_DATABASE_URL not set (optional)")
    
    if storage_bucket:
        print_success(f"FIREBASE_STORAGE_BUCKET: {storage_bucket}")
    else:
        print_warning("FIREBASE_STORAGE_BUCKET not set (optional)")
    
    # Step 2: Check if credentials file exists
    print_info("\nStep 2: Checking credentials file...")
    
    if not os.path.exists(creds_path):
        print_error(f"Credentials file not found: {creds_path}")
        print_info("\nTo fix this:")
        print("  1. Go to Firebase Console: https://console.firebase.google.com/")
        print("  2. Select your project")
        print("  3. Go to Project Settings > Service accounts")
        print("  4. Click 'Generate new private key'")
        print(f"  5. Save the downloaded file to: {creds_path}")
        return False
    
    print_success(f"Credentials file found: {creds_path}")
    
    # Step 3: Initialize Firebase
    print_info("\nStep 3: Initializing Firebase Admin SDK...")
    
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': db_url,
                'storageBucket': storage_bucket,
            })
        print_success("Firebase Admin SDK initialized successfully!")
    except Exception as e:
        print_error(f"Failed to initialize Firebase: {str(e)}")
        print_info("\nPossible issues:")
        print("  - Invalid service account key")
        print("  - Incorrect file path")
        print("  - Corrupted JSON file")
        return False
    
    # Step 4: Test Firebase Authentication
    print_info("\nStep 4: Testing Firebase Authentication...")
    
    try:
        # List users (just to test connection)
        page = auth.list_users(max_results=1)
        print_success("Successfully connected to Firebase Authentication!")
        
        # Count users
        user_count = 0
        for user in auth.list_users().iterate_all():
            user_count += 1
        
        print_info(f"Total users in Firebase: {user_count}")
        
        if user_count == 0:
            print_warning("No users found in Firebase Authentication")
            print_info("You can create users from your frontend or Firebase Console")
        
    except Exception as e:
        print_error(f"Failed to access Firebase Authentication: {str(e)}")
        print_info("\nMake sure:")
        print("  - Firebase Authentication is enabled in Firebase Console")
        print("  - Service account has proper permissions")
        return False
    
    # Step 5: Get project info
    print_info("\nStep 5: Getting project information...")
    
    try:
        # Try to get a user to extract project info
        if user_count > 0:
            users = auth.list_users(max_results=1)
            for user in users.iterate_all():
                print_info(f"Sample user UID: {user.uid}")
                print_info(f"Sample user email: {user.email}")
                break
    except:
        pass
    
    # Success summary
    print("\n" + "="*70)
    print_success("Firebase connection successful!")
    print("="*70 + "\n")
    
    print_info("Configuration summary:")
    print(f"  ✓ Credentials file: {creds_path}")
    print(f"  ✓ Firebase users: {user_count}")
    print(f"  ✓ Authentication: Working")
    
    print_info("\nNext steps:")
    print("  1. Run migrations: python manage.py migrate")
    print("  2. Test authentication: python test_firebase_authentication.py")
    print("  3. Update frontend to use Firebase Authentication")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nConnection test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
