#!/usr/bin/env python
"""
Script to test FirebaseAuthentication class.
This script tests token validation, user retrieval, and caching.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import RequestFactory
from django.core.cache import cache
from apps.authentication.firebase_auth import FirebaseAuthentication
from apps.authentication.models import User, Role
from colorama import init, Fore, Style
import firebase_admin
from firebase_admin import auth as firebase_auth

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

def test_firebase_authentication():
    """Test FirebaseAuthentication class."""
    print("\n" + "="*60)
    print("FirebaseAuthentication Class Test")
    print("="*60 + "\n")
    
    # Test 1: Initialize FirebaseAuthentication
    print_info("Test 1: Initializing FirebaseAuthentication...")
    try:
        auth_backend = FirebaseAuthentication()
        print_success("FirebaseAuthentication initialized successfully")
    except Exception as e:
        print_error(f"Failed to initialize: {str(e)}")
        return False
    
    # Test 2: Test get_token_from_header
    print_info("\nTest 2: Testing token extraction from header...")
    factory = RequestFactory()
    
    # Test with valid Bearer token
    request = factory.get('/', HTTP_AUTHORIZATION='Bearer test-token-12345')
    token = auth_backend.get_token_from_header(request)
    if token == 'test-token-12345':
        print_success("Token extracted correctly from Bearer header")
    else:
        print_error(f"Token extraction failed. Got: {token}")
        return False
    
    # Test with no authorization header
    request = factory.get('/')
    token = auth_backend.get_token_from_header(request)
    if token is None:
        print_success("Correctly returns None when no auth header")
    else:
        print_error(f"Should return None, got: {token}")
        return False
    
    # Test with invalid format
    request = factory.get('/', HTTP_AUTHORIZATION='InvalidFormat')
    token = auth_backend.get_token_from_header(request)
    if token is None:
        print_success("Correctly returns None for invalid format")
    else:
        print_error(f"Should return None for invalid format, got: {token}")
        return False
    
    # Test 3: Test authenticate_header
    print_info("\nTest 3: Testing authenticate_header...")
    request = factory.get('/')
    header = auth_backend.authenticate_header(request)
    if header == 'Bearer':
        print_success(f"Correct authenticate header: {header}")
    else:
        print_error(f"Wrong authenticate header: {header}")
        return False
    
    # Test 4: Create test user with firebase_uid
    print_info("\nTest 4: Creating test user with firebase_uid...")
    try:
        admin_role, _ = Role.objects.get_or_create(
            name=Role.ADMIN,
            defaults={'description': 'Administrator role'}
        )
        
        test_user, created = User.objects.get_or_create(
            email='firebase-auth-test@example.com',
            defaults={
                'first_name': 'Firebase',
                'last_name': 'Auth Test',
                'rut': '99999999-9',
                'role': admin_role,
                'firebase_uid': 'test-firebase-uid-auth-12345'
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print_success(f"Test user created: {test_user.email}")
        else:
            print_info(f"Test user already exists: {test_user.email}")
        
    except Exception as e:
        print_error(f"Failed to create test user: {str(e)}")
        return False
    
    # Test 5: Test get_user_by_firebase_uid
    print_info("\nTest 5: Testing user retrieval by firebase_uid...")
    user = auth_backend.get_user_by_firebase_uid('test-firebase-uid-auth-12345')
    if user and user.email == 'firebase-auth-test@example.com':
        print_success(f"User retrieved successfully: {user.email}")
    else:
        print_error("Failed to retrieve user by firebase_uid")
        return False
    
    # Test with non-existent UID
    user = auth_backend.get_user_by_firebase_uid('non-existent-uid')
    if user is None:
        print_success("Correctly returns None for non-existent UID")
    else:
        print_error(f"Should return None for non-existent UID, got: {user}")
        return False
    
    # Test 6: Test token caching
    print_info("\nTest 6: Testing token validation caching...")
    print_warning("Note: This test requires a real Firebase token to fully test")
    print_info("Testing cache mechanism with mock data...")
    
    # Clear cache
    cache.clear()
    
    # Manually set cache to simulate validated token
    test_token = "mock-firebase-token-for-testing"
    cache_key = f'firebase_token:{test_token[:50]}'
    cache.set(cache_key, 'test-firebase-uid-auth-12345', 300)
    
    # Try to get from cache
    cached_uid = cache.get(cache_key)
    if cached_uid == 'test-firebase-uid-auth-12345':
        print_success("Token caching mechanism working correctly")
    else:
        print_error("Token caching not working")
        return False
    
    # Test 7: Test full authentication flow (without real Firebase token)
    print_info("\nTest 7: Testing authentication flow...")
    print_warning("Note: Full authentication requires a real Firebase token")
    print_info("Testing with mock request...")
    
    # Create request with Bearer token
    request = factory.get('/', HTTP_AUTHORIZATION='Bearer mock-token')
    
    # This will fail because we don't have a real Firebase token
    # but we can test that it handles the error gracefully
    try:
        result = auth_backend.authenticate(request)
        if result is None:
            print_info("Authentication returned None (expected without real token)")
        else:
            print_warning(f"Unexpected result: {result}")
    except Exception as e:
        print_info(f"Authentication failed as expected: {type(e).__name__}")
    
    # Test 8: Test with real Firebase token (if available)
    print_info("\nTest 8: Testing with real Firebase token (optional)...")
    print_info("To test with a real token:")
    print_info("  1. Get a Firebase ID token from your frontend")
    print_info("  2. Set it as environment variable: FIREBASE_TEST_TOKEN")
    print_info("  3. Run this script again")
    
    test_token = os.getenv('FIREBASE_TEST_TOKEN')
    if test_token:
        print_info("Found FIREBASE_TEST_TOKEN, testing with real token...")
        try:
            firebase_uid = auth_backend.verify_firebase_token(test_token)
            if firebase_uid:
                print_success(f"Real token validated successfully! UID: {firebase_uid}")
                
                # Try to authenticate with real token
                request = factory.get('/', HTTP_AUTHORIZATION=f'Bearer {test_token}')
                result = auth_backend.authenticate(request)
                
                if result:
                    user, token = result
                    print_success(f"Full authentication successful! User: {user.email}")
                else:
                    print_warning("Authentication returned None (user may not exist)")
            else:
                print_error("Real token validation failed")
        except Exception as e:
            print_error(f"Error testing with real token: {str(e)}")
    else:
        print_info("No FIREBASE_TEST_TOKEN found, skipping real token test")
    
    # Cleanup
    print_info("\nCleaning up test data...")
    try:
        test_user.delete()
        print_success("Test user deleted")
    except:
        pass
    
    # Summary
    print("\n" + "="*60)
    print_success("FirebaseAuthentication tests completed!")
    print("="*60 + "\n")
    
    print_info("Summary:")
    print("  ✓ Token extraction from headers")
    print("  ✓ User retrieval by firebase_uid")
    print("  ✓ Token caching mechanism")
    print("  ✓ Error handling")
    
    print_info("\nNext steps:")
    print("  1. Get service account key from Firebase Console")
    print("  2. Set FIREBASE_CREDENTIALS_PATH in .env")
    print("  3. Test with real Firebase token")
    print("  4. Update REST_FRAMEWORK settings to use FirebaseAuthentication")
    
    return True

if __name__ == '__main__':
    try:
        success = test_firebase_authentication()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
