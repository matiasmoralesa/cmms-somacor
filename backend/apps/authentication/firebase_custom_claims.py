"""
Firebase Custom Claims Service for managing user claims in Firebase tokens.
Custom claims include role, permissions, license status, and other user metadata.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import date

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError

from apps.authentication.models import User, Role

logger = logging.getLogger(__name__)


class CustomClaimsService:
    """
    Service class for managing Firebase custom claims.
    
    Custom claims are stored in the Firebase ID token and can be accessed
    by the frontend without additional API calls. They include:
    - User role and role display name
    - Permissions list
    - Role flags (is_admin, is_supervisor, is_operador)
    - Employee status
    - License status (for operador users)
    """
    
    MAX_RETRIES = 3
    
    @classmethod
    def build_claims_for_user(cls, user: User) -> Dict[str, Any]:
        """
        Build custom claims dictionary for a user.
        
        Args:
            user: Django User instance
            
        Returns:
            Dictionary of custom claims to set in Firebase
        """
        claims = {
            # User identification
            'user_id': str(user.id),
            'email': user.email,
            'rut': user.rut,
            
            # Role information
            'role': user.role.name if user.role else None,
            'role_display': user.role.get_name_display() if user.role else None,
            
            # Role flags for easy frontend checks
            'is_admin': user.is_admin(),
            'is_supervisor': user.is_supervisor(),
            'is_operador': user.is_operador(),
            
            # Employee status
            'employee_status': user.employee_status,
            'is_active': user.is_active,
            
            # Permissions
            'permissions': cls._get_permissions_for_user(user),
            
            # Capability flags
            'can_view_all_resources': user.can_view_all_resources(),
            'can_manage_users': user.can_manage_users(),
            'can_create_work_orders': user.can_create_work_orders(),
            'can_create_maintenance_plans': user.can_create_maintenance_plans(),
            'can_view_predictions': user.can_view_predictions(),
            'can_view_reports': user.can_view_reports(),
            'can_manage_inventory': user.can_manage_inventory(),
        }
        
        # Add license information for operador users
        if user.is_operador():
            license_status = cls._get_license_status(user)
            claims['license'] = license_status
        
        return claims
    
    @classmethod
    def _get_permissions_for_user(cls, user: User) -> List[str]:
        """
        Get list of permission codes for a user.
        
        Args:
            user: Django User instance
            
        Returns:
            List of permission codes
        """
        if not user.role:
            return []
        
        permissions = user.role.permissions.all().values_list('code', flat=True)
        return list(permissions)
    
    @classmethod
    def _get_license_status(cls, user: User) -> Dict[str, Any]:
        """
        Get license status information for operador users.
        
        Args:
            user: Django User instance
            
        Returns:
            Dictionary with license status information
        """
        if not user.license_type or not user.license_expiration_date:
            return {
                'has_license': False,
                'is_valid': False,
                'expires_soon': False,
                'days_until_expiration': None,
            }
        
        has_valid_license = user.has_valid_license()
        expires_soon = user.license_expires_soon(days=30)
        days_until_expiration = user.days_until_license_expiration()
        
        return {
            'has_license': True,
            'is_valid': has_valid_license,
            'expires_soon': expires_soon,
            'days_until_expiration': days_until_expiration,
            'license_type': user.license_type,
            'expiration_date': user.license_expiration_date.isoformat() if user.license_expiration_date else None,
        }
    
    @classmethod
    def update_user_claims(cls, user: User) -> bool:
        """
        Update custom claims for a user in Firebase.
        
        Args:
            user: Django User instance
            
        Returns:
            True if successful, False otherwise
        """
        if not user.firebase_uid:
            logger.warning(f"Cannot update claims for user {user.id}: no firebase_uid")
            return False
        
        try:
            claims = cls.build_claims_for_user(user)
            
            # Set custom claims in Firebase
            firebase_auth.set_custom_user_claims(user.firebase_uid, claims)
            
            logger.info(f"Successfully updated custom claims for user {user.id} (Firebase UID: {user.firebase_uid})")
            return True
            
        except firebase_auth.UserNotFoundError:
            logger.error(f"Firebase user not found for user {user.id} (Firebase UID: {user.firebase_uid})")
            return False
        except FirebaseError as e:
            logger.error(f"Failed to update custom claims for user {user.id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating custom claims for user {user.id}: {str(e)}")
            return False
    
    @classmethod
    def update_claims_for_role_change(cls, user: User) -> bool:
        """
        Update custom claims when a user's role changes.
        
        This is a convenience method that calls update_user_claims but logs
        specifically for role changes.
        
        Args:
            user: Django User instance
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Updating claims for user {user.id} due to role change to {user.role.name if user.role else 'None'}")
        return cls.update_user_claims(user)
    
    @classmethod
    def update_claims_for_license_change(cls, user: User) -> bool:
        """
        Update custom claims when a user's license information changes.
        
        This is a convenience method that calls update_user_claims but logs
        specifically for license changes.
        
        Args:
            user: Django User instance
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Updating claims for user {user.id} due to license information change")
        return cls.update_user_claims(user)
    
    @classmethod
    def get_user_claims(cls, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get current custom claims for a Firebase user.
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            Dictionary of custom claims or None if user not found
        """
        try:
            user = firebase_auth.get_user(firebase_uid)
            return user.custom_claims or {}
            
        except firebase_auth.UserNotFoundError:
            logger.warning(f"Firebase user not found: {firebase_uid}")
            return None
        except FirebaseError as e:
            logger.error(f"Failed to get custom claims for Firebase user {firebase_uid}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting custom claims for Firebase user {firebase_uid}: {str(e)}")
            return None
    
    @classmethod
    def clear_user_claims(cls, firebase_uid: str) -> bool:
        """
        Clear all custom claims for a Firebase user.
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            firebase_auth.set_custom_user_claims(firebase_uid, None)
            logger.info(f"Successfully cleared custom claims for Firebase user: {firebase_uid}")
            return True
            
        except firebase_auth.UserNotFoundError:
            logger.error(f"Firebase user not found: {firebase_uid}")
            return False
        except FirebaseError as e:
            logger.error(f"Failed to clear custom claims for Firebase user {firebase_uid}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error clearing custom claims for Firebase user {firebase_uid}: {str(e)}")
            return False


class CustomClaimsError(Exception):
    """Base exception for custom claims errors."""
    pass


class ClaimsUpdateError(CustomClaimsError):
    """Raised when updating custom claims fails."""
    pass


class ClaimsRetrievalError(CustomClaimsError):
    """Raised when retrieving custom claims fails."""
    pass
