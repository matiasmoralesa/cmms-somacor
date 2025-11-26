"""
Django signals for synchronizing User model changes with Firebase Authentication.

These signals ensure that:
1. When a Django user is created, a Firebase account is created
2. When a Django user is updated, the Firebase account is updated
3. When a Django user is deleted, the Firebase account is deleted
4. Custom claims are updated when role or permissions change
"""
import logging
from django.db import transaction
from django.db.models.signals import post_save, pre_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.authentication.firebase_user_service import FirebaseUserService
from apps.authentication.firebase_custom_claims import CustomClaimsService
from apps.authentication.models import Role

User = get_user_model()
logger = logging.getLogger(__name__)

# Dictionary to store old user state before save
_user_pre_save_state = {}


@receiver(pre_save, sender=User)
def capture_user_state(sender, instance, **kwargs):
    """
    Capture user state before save to detect changes.
    
    Args:
        sender: The User model class
        instance: The User instance being saved
        **kwargs: Additional keyword arguments
    """
    # Skip if this is being called during a migration or fixture loading
    if kwargs.get('raw', False):
        return
    
    # Only capture state for existing users
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            _user_pre_save_state[instance.pk] = {
                'email': old_user.email,
                'first_name': old_user.first_name,
                'last_name': old_user.last_name,
                'is_active': old_user.is_active,
                'role_id': old_user.role_id,
                'license_type': old_user.license_type,
                'license_expiration_date': old_user.license_expiration_date,
            }
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def sync_user_to_firebase(sender, instance, created, **kwargs):
    """
    Sync Django User changes to Firebase Authentication.
    
    This signal handles:
    - User creation: Create Firebase account and store UID
    - User updates: Update Firebase email, display name, disabled status
    - Role changes: Update custom claims
    
    Args:
        sender: The User model class
        instance: The User instance being saved
        created: Boolean indicating if this is a new user
        **kwargs: Additional keyword arguments
    """
    # Skip if this is being called during a migration or fixture loading
    if kwargs.get('raw', False):
        return
    
    try:
        if created:
            # New user - create Firebase account
            _handle_user_creation(instance)
        else:
            # Existing user - update Firebase account
            _handle_user_update(instance)
            
    except Exception as e:
        logger.error(f"Error syncing user {instance.id} to Firebase: {str(e)}")
        # Don't raise the exception to avoid breaking the Django save
        # The user will be created in Django but not in Firebase
        # This can be fixed later with a migration script
    finally:
        # Clean up pre-save state
        if instance.pk in _user_pre_save_state:
            del _user_pre_save_state[instance.pk]


def _handle_user_creation(user):
    """
    Handle creation of a new user by creating Firebase account.
    
    Args:
        user: User instance
    """
    # Skip if user already has a firebase_uid (e.g., from migration)
    if user.firebase_uid:
        logger.info(f"User {user.id} already has firebase_uid: {user.firebase_uid}")
        return
    
    try:
        # Generate a temporary password for Firebase
        # User will need to reset password via email
        temp_password = User.objects.make_random_password(length=20)
        
        # Create Firebase user
        display_name = user.get_full_name() or user.email
        firebase_uid = FirebaseUserService.create_firebase_user(
            email=user.email,
            password=temp_password,
            display_name=display_name,
            disabled=not user.is_active
        )
        
        # Store Firebase UID in Django user
        # Use update() to avoid triggering this signal again
        User.objects.filter(pk=user.pk).update(firebase_uid=firebase_uid)
        
        # Reload the user instance to get the updated firebase_uid
        user.refresh_from_db()
        
        # Set custom claims
        CustomClaimsService.update_user_claims(user)
        
        logger.info(f"Successfully created Firebase account for user {user.id}: {firebase_uid}")
        
    except Exception as e:
        logger.error(f"Failed to create Firebase account for user {user.id}: {str(e)}")
        raise


def _handle_user_update(user):
    """
    Handle updates to an existing user by updating Firebase account.
    
    Args:
        user: User instance
    """
    if not user.firebase_uid:
        logger.warning(f"User {user.id} has no firebase_uid, cannot update Firebase account")
        return
    
    # Get old state from pre-save capture
    old_state = _user_pre_save_state.get(user.pk)
    if not old_state:
        logger.warning(f"No pre-save state found for user {user.id}, skipping update")
        return
    
    try:
        update_data = {}
        
        # Check if email changed
        if old_state['email'] != user.email:
            update_data['email'] = user.email
            logger.info(f"Email changed for user {user.id}: {old_state['email']} -> {user.email}")
        
        # Check if name changed
        old_display_name = f"{old_state['first_name']} {old_state['last_name']}".strip()
        new_display_name = user.get_full_name()
        if old_display_name != new_display_name:
            update_data['display_name'] = new_display_name
            logger.info(f"Display name changed for user {user.id}: {old_display_name} -> {new_display_name}")
        
        # Check if active status changed
        if old_state['is_active'] != user.is_active:
            update_data['disabled'] = not user.is_active
            logger.info(f"Active status changed for user {user.id}: {old_state['is_active']} -> {user.is_active}")
        
        # Update Firebase if there are changes
        if update_data:
            FirebaseUserService.update_firebase_user(user.firebase_uid, **update_data)
        
        # Check if role changed or license information changed
        role_changed = old_state['role_id'] != user.role_id
        license_changed = (
            old_state['license_type'] != user.license_type or
            old_state['license_expiration_date'] != user.license_expiration_date
        )
        
        if role_changed or license_changed:
            logger.info(f"Role or license changed for user {user.id}, updating custom claims")
            CustomClaimsService.update_user_claims(user)
        
    except Exception as e:
        logger.error(f"Failed to update Firebase account for user {user.id}: {str(e)}")
        # Don't raise to avoid breaking the Django save


@receiver(pre_delete, sender=User)
def delete_firebase_user(sender, instance, **kwargs):
    """
    Delete Firebase user when Django user is deleted.
    
    Args:
        sender: The User model class
        instance: The User instance being deleted
        **kwargs: Additional keyword arguments
    """
    if not instance.firebase_uid:
        logger.warning(f"User {instance.id} has no firebase_uid, cannot delete Firebase account")
        return
    
    try:
        FirebaseUserService.delete_firebase_user(instance.firebase_uid)
        logger.info(f"Successfully deleted Firebase account for user {instance.id}: {instance.firebase_uid}")
        
    except Exception as e:
        logger.error(f"Failed to delete Firebase account for user {instance.id}: {str(e)}")
        # Don't raise to avoid blocking the Django deletion


@receiver(m2m_changed, sender=Role.permissions.through)
def update_claims_on_permission_change(sender, instance, action, **kwargs):
    """
    Update custom claims for all users with a role when permissions change.
    
    Args:
        sender: The through model for Role.permissions
        instance: The Role instance
        action: The m2m action (pre_add, post_add, pre_remove, post_remove, pre_clear, post_clear)
        **kwargs: Additional keyword arguments
    """
    # Only act on post actions (after the change is committed)
    if action not in ['post_add', 'post_remove', 'post_clear']:
        return
    
    try:
        # Get all users with this role
        users = User.objects.filter(role=instance, firebase_uid__isnull=False)
        
        logger.info(f"Updating custom claims for {users.count()} users with role {instance.name}")
        
        for user in users:
            try:
                CustomClaimsService.update_user_claims(user)
            except Exception as e:
                logger.error(f"Failed to update claims for user {user.id}: {str(e)}")
                # Continue with other users
        
    except Exception as e:
        logger.error(f"Error updating claims for role {instance.name}: {str(e)}")


# Signal to handle password changes
@receiver(post_save, sender=User)
def sync_password_to_firebase(sender, instance, created, update_fields, **kwargs):
    """
    Sync password changes to Firebase.
    
    Note: Django doesn't provide a direct way to detect password changes,
    so this is handled separately in the User model's set_password method.
    
    Args:
        sender: The User model class
        instance: The User instance being saved
        created: Boolean indicating if this is a new user
        update_fields: Set of field names that were updated
        **kwargs: Additional keyword arguments
    """
    # Skip if this is a new user (handled by sync_user_to_firebase)
    if created:
        return
    
    # Skip if no firebase_uid
    if not instance.firebase_uid:
        return
    
    # Check if password field was updated
    # Note: This won't catch password changes made via set_password()
    # For that, we need to override set_password in the User model
    if update_fields and 'password' in update_fields:
        try:
            # We can't get the plain password here, so we can't sync it
            # Password syncing should be done in the view/serializer where
            # the plain password is available
            logger.info(f"Password updated for user {instance.id}, but cannot sync to Firebase from signal")
        except Exception as e:
            logger.error(f"Error handling password change for user {instance.id}: {str(e)}")
