#!/usr/bin/env python
"""
Script to test the firebase_uid migration.
This script will:
1. Check if migration can be applied
2. Apply the migration
3. Verify the field was added correctly
4. Test rollback
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.core.management import call_command
from django.db import connection
from apps.authentication.models import User
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

def check_migration_status():
    """Check if migration is already applied."""
    print_info("Checking migration status...")
    
    try:
        # Check if firebase_uid field exists in User model
        user_fields = [f.name for f in User._meta.get_fields()]
        
        if 'firebase_uid' in user_fields:
            print_success("firebase_uid field exists in User model")
            return True
        else:
            print_warning("firebase_uid field does not exist in User model")
            return False
    except Exception as e:
        print_error(f"Error checking migration status: {str(e)}")
        return False

def check_database_column():
    """Check if firebase_uid column exists in database."""
    print_info("Checking database column...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'firebase_uid'
            """)
            result = cursor.fetchone()
            
            if result:
                print_success(f"firebase_uid column exists in database")
                print_info(f"  Column: {result[0]}")
                print_info(f"  Type: {result[1]}")
                print_info(f"  Nullable: {result[2]}")
                print_info(f"  Default: {result[3]}")
                return True
            else:
                print_warning("firebase_uid column does not exist in database")
                return False
    except Exception as e:
        # If using SQLite, try a different approach
        try:
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                
                for col in columns:
                    if col[1] == 'firebase_uid':
                        print_success(f"firebase_uid column exists in database (SQLite)")
                        print_info(f"  Column: {col[1]}")
                        print_info(f"  Type: {col[2]}")
                        print_info(f"  Nullable: {col[3] == 0}")
                        return True
                
                print_warning("firebase_uid column does not exist in database")
                return False
        except Exception as e2:
            print_error(f"Error checking database column: {str(e2)}")
            return False

def apply_migration():
    """Apply the migration."""
    print_info("\nApplying migration...")
    
    try:
        call_command('migrate', 'authentication', verbosity=2)
        print_success("Migration applied successfully")
        return True
    except Exception as e:
        print_error(f"Error applying migration: {str(e)}")
        return False

def test_field_operations():
    """Test CRUD operations with firebase_uid field."""
    print_info("\nTesting field operations...")
    
    try:
        # Test 1: Create user with firebase_uid
        print_info("Test 1: Creating user with firebase_uid...")
        
        from apps.authentication.models import Role
        
        # Get or create a test role
        admin_role, _ = Role.objects.get_or_create(
            name=Role.ADMIN,
            defaults={'description': 'Administrator role'}
        )
        
        test_user = User.objects.create_user(
            email='firebase-test@example.com',
            password='testpass123',
            first_name='Firebase',
            last_name='Test',
            rut='11111111-1',
            role=admin_role,
            firebase_uid='test-firebase-uid-12345'
        )
        print_success(f"User created with firebase_uid: {test_user.firebase_uid}")
        
        # Test 2: Query user by firebase_uid
        print_info("Test 2: Querying user by firebase_uid...")
        found_user = User.objects.get(firebase_uid='test-firebase-uid-12345')
        print_success(f"User found: {found_user.email}")
        
        # Test 3: Update firebase_uid
        print_info("Test 3: Updating firebase_uid...")
        found_user.firebase_uid = 'updated-firebase-uid-67890'
        found_user.save()
        print_success(f"firebase_uid updated to: {found_user.firebase_uid}")
        
        # Test 4: Test unique constraint
        print_info("Test 4: Testing unique constraint...")
        try:
            duplicate_user = User.objects.create_user(
                email='duplicate@example.com',
                password='testpass123',
                first_name='Duplicate',
                last_name='User',
                rut='22222222-2',
                role=admin_role,
                firebase_uid='updated-firebase-uid-67890'  # Same as above
            )
            print_error("Unique constraint not working - duplicate firebase_uid allowed!")
            duplicate_user.delete()
        except Exception as e:
            print_success("Unique constraint working - duplicate firebase_uid rejected")
        
        # Test 5: Test null values
        print_info("Test 5: Testing null firebase_uid...")
        null_user = User.objects.create_user(
            email='null-firebase@example.com',
            password='testpass123',
            first_name='Null',
            last_name='Firebase',
            rut='33333333-3',
            role=admin_role,
            firebase_uid=None
        )
        print_success(f"User created with null firebase_uid: {null_user.email}")
        
        # Cleanup
        print_info("\nCleaning up test users...")
        test_user.delete()
        null_user.delete()
        print_success("Test users deleted")
        
        return True
        
    except Exception as e:
        print_error(f"Error testing field operations: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_migration_rollback():
    """Test rolling back the migration."""
    print_info("\nTesting migration rollback...")
    print_warning("This will rollback the migration to test reversibility")
    
    response = input("Do you want to test rollback? (y/N): ")
    if response.lower() != 'y':
        print_info("Skipping rollback test")
        return True
    
    try:
        # Rollback to previous migration
        call_command('migrate', 'authentication', '0004', verbosity=2)
        print_success("Migration rolled back successfully")
        
        # Check if field is gone
        if not check_database_column():
            print_success("firebase_uid column removed from database")
        else:
            print_error("firebase_uid column still exists after rollback!")
            return False
        
        # Re-apply migration
        print_info("\nRe-applying migration...")
        call_command('migrate', 'authentication', verbosity=2)
        print_success("Migration re-applied successfully")
        
        return True
        
    except Exception as e:
        print_error(f"Error testing rollback: {str(e)}")
        return False

def main():
    """Main test function."""
    print("\n" + "="*60)
    print("Firebase UID Migration Test")
    print("="*60 + "\n")
    
    # Check current status
    model_has_field = check_migration_status()
    db_has_column = check_database_column()
    
    # If migration not applied, apply it
    if not db_has_column:
        if not apply_migration():
            print_error("\nMigration test failed!")
            return False
        
        # Verify migration was applied
        if not check_database_column():
            print_error("\nMigration applied but column not found!")
            return False
    
    # Test field operations
    if not test_field_operations():
        print_error("\nField operations test failed!")
        return False
    
    # Test rollback (optional)
    if not test_migration_rollback():
        print_error("\nRollback test failed!")
        return False
    
    # Summary
    print("\n" + "="*60)
    print_success("All migration tests passed successfully!")
    print("="*60 + "\n")
    
    print_info("Migration details:")
    print("  - Field name: firebase_uid")
    print("  - Field type: CharField(max_length=128)")
    print("  - Constraints: unique=True, null=True, blank=True")
    print("  - Index: db_index=True")
    print("  - Migration file: 0005_add_firebase_uid.py")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
