"""
Firebase User Service for managing Firebase Authentication users.
Handles user creation, updates, deletion, and password management.
"""
import logging
import time
from typing import Optional, Dict, Any
from django.conf import settings

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)


class FirebaseUserService:
    """
    Service class for managing Firebase Authentication users.
    
    This service provides methods to:
    - Create Firebase user accounts
    - Update user information (email, password, display name)
    - Enable/disable user accounts
    - Delete user accounts
    - Send password reset emails
    
    All methods include error handling and retry logic with exponential backoff.
    """
    
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1  # seconds
    MAX_BACKOFF = 10  # seconds
    
    @staticmethod
    def _retry_with_backoff(func, *args, **kwargs):
        """
        Execute a function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            FirebaseError: If all retries fail
        """
        backoff = FirebaseUserService.INITIAL_BACKOFF
        last_exception = None
        
        for attempt in range(FirebaseUserService.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except FirebaseError as e:
                last_exception = e
                if attempt < FirebaseUserService.MAX_RETRIES - 1:
                    logger.warning(
                        f"Firebase operation failed (attempt {attempt + 1}/{FirebaseUserService.MAX_RETRIES}): {str(e)}. "
                        f"Retrying in {backoff} seconds..."
                    )
                    time.sleep(backoff)
                    backoff = min(backoff * 2, FirebaseUserService.MAX_BACKOFF)
                else:
                    logger.error(f"Firebase operation failed after {FirebaseUserService.MAX_RETRIES} attempts: {str(e)}")
        
        raise last_exception
    
    @classmethod
    def create_firebase_user(
        cls,
        email: str,
        password: str,
        display_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a new Firebase user account.
        
        Args:
            email: User's email address
            password: User's password
            display_name: Optional display name
            **kwargs: Additional user properties
            
        Returns:
            Firebase UID of the created user
            
        Raises:
            FirebaseError: If user creation fails
        """
        try:
            user_data = {
                'email': email,
                'password': password,
                'email_verified': False,
            }
            
            if display_name:
                user_data['display_name'] = display_name
            
            # Add any additional properties
            user_data.update(kwargs)
            
            # Create user with retry logic
            firebase_user = cls._retry_with_backoff(
                firebase_auth.create_user,
                **user_data
            )
            
            logger.info(f"Successfully created Firebase user: {firebase_user.uid} ({email})")
            return firebase_user.uid
            
        except FirebaseError as e:
            logger.error(f"Failed to create Firebase user for {email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating Firebase user for {email}: {str(e)}")
            raise
    
    @classmethod
    def update_firebase_user(
        cls,
        firebase_uid: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Update an existing Firebase user.
        
        Args:
            firebase_uid: Firebase user ID
            email: New email address (optional)
            password: New password (optional)
            display_name: New display name (optional)
            **kwargs: Additional properties to update
            
        Raises:
            FirebaseError: If update fails
        """
        try:
            update_data = {}
            
            if email is not None:
                update_data['email'] = email
            
            if password is not None:
                update_data['password'] = password
            
            if display_name is not None:
                update_data['display_name'] = display_name
            
            # Add any additional properties
            update_data.update(kwargs)
            
            if not update_data:
                logger.warning(f"No update data provided for Firebase user {firebase_uid}")
                return
            
            # Update user with retry logic
            cls._retry_with_backoff(
                firebase_auth.update_user,
                firebase_uid,
                **update_data
            )
            
            logger.info(f"Successfully updated Firebase user: {firebase_uid}")
            
        except firebase_auth.UserNotFoundError:
            logger.error(f"Firebase user not found: {firebase_uid}")
            raise
        except FirebaseError as e:
            logger.error(f"Failed to update Firebase user {firebase_uid}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating Firebase user {firebase_uid}: {str(e)}")
            raise
    
    @classmethod
    def disable_firebase_user(cls, firebase_uid: str) -> None:
        """
        Disable a Firebase user account.
        
        Args:
            firebase_uid: Firebase user ID
            
        Raises:
            FirebaseError: If disable operation fails
        """
        try:
            cls._retry_with_backoff(
                firebase_auth.update_user,
                firebase_uid,
                disabled=True
            )
            
            logger.info(f"Successfully disabled Firebase user: {firebase_uid}")
            
        except firebase_auth.UserNotFoundError:
            logger.error(f"Firebase user not found: {firebase_uid}")
            raise
        except FirebaseError as e:
            logger.error(f"Failed to disable Firebase user {firebase_uid}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error disabling Firebase user {firebase_uid}: {str(e)}")
            raise
    
    @classmethod
    def enable_firebase_user(cls, firebase_uid: str) -> None:
        """
        Enable a Firebase user account.
        
        Args:
            firebase_uid: Firebase user ID
            
        Raises:
            FirebaseError: If enable operation fails
        """
        try:
            cls._retry_with_backoff(
                firebase_auth.update_user,
                firebase_uid,
                disabled=False
            )
            
            logger.info(f"Successfully enabled Firebase user: {firebase_uid}")
            
        except firebase_auth.UserNotFoundError:
            logger.error(f"Firebase user not found: {firebase_uid}")
            raise
        except FirebaseError as e:
            logger.error(f"Failed to enable Firebase user {firebase_uid}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error enabling Firebase user {firebase_uid}: {str(e)}")
            raise
    
    @classmethod
    def delete_firebase_user(cls, firebase_uid: str) -> None:
        """
        Delete a Firebase user account.
        
        Args:
            firebase_uid: Firebase user ID
            
        Raises:
            FirebaseError: If deletion fails
        """
        try:
            cls._retry_with_backoff(
                firebase_auth.delete_user,
                firebase_uid
            )
            
            logger.info(f"Successfully deleted Firebase user: {firebase_uid}")
            
        except firebase_auth.UserNotFoundError:
            logger.warning(f"Firebase user not found (already deleted?): {firebase_uid}")
            # Not raising error since the end result is the same
        except FirebaseError as e:
            logger.error(f"Failed to delete Firebase user {firebase_uid}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting Firebase user {firebase_uid}: {str(e)}")
            raise
    
    @classmethod
    def send_password_reset_email(cls, email: str) -> None:
        """
        Send a password reset email to a user.
        
        Args:
            email: User's email address
            
        Raises:
            FirebaseError: If sending email fails
        """
        try:
            # Generate password reset link
            link = cls._retry_with_backoff(
                firebase_auth.generate_password_reset_link,
                email
            )
            
            logger.info(f"Successfully generated password reset link for: {email}")
            logger.debug(f"Password reset link: {link}")
            
            # Note: Firebase automatically sends the email if email templates are configured
            # in the Firebase Console. Otherwise, you need to send the link manually.
            
        except firebase_auth.UserNotFoundError:
            logger.error(f"No Firebase user found with email: {email}")
            raise
        except FirebaseError as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending password reset email to {email}: {str(e)}")
            raise
    
    @classmethod
    def get_firebase_user(cls, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get Firebase user information.
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            Dictionary with user information or None if not found
        """
        try:
            user = cls._retry_with_backoff(
                firebase_auth.get_user,
                firebase_uid
            )
            
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'email_verified': user.email_verified,
                'disabled': user.disabled,
                'custom_claims': user.custom_claims or {},
            }
            
        except firebase_auth.UserNotFoundError:
            logger.warning(f"Firebase user not found: {firebase_uid}")
            return None
        except FirebaseError as e:
            logger.error(f"Failed to get Firebase user {firebase_uid}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Firebase user {firebase_uid}: {str(e)}")
            return None
    
    @classmethod
    def get_firebase_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """
        Get Firebase user information by email.
        
        Args:
            email: User's email address
            
        Returns:
            Dictionary with user information or None if not found
        """
        try:
            user = cls._retry_with_backoff(
                firebase_auth.get_user_by_email,
                email
            )
            
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'email_verified': user.email_verified,
                'disabled': user.disabled,
                'custom_claims': user.custom_claims or {},
            }
            
        except firebase_auth.UserNotFoundError:
            logger.warning(f"No Firebase user found with email: {email}")
            return None
        except FirebaseError as e:
            logger.error(f"Failed to get Firebase user by email {email}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Firebase user by email {email}: {str(e)}")
            return None


class FirebaseUserServiceError(Exception):
    """Base exception for Firebase user service errors."""
    pass


class UserCreationError(FirebaseUserServiceError):
    """Raised when user creation fails."""
    pass


class UserUpdateError(FirebaseUserServiceError):
    """Raised when user update fails."""
    pass


class UserDeletionError(FirebaseUserServiceError):
    """Raised when user deletion fails."""
    pass


class PasswordResetError(FirebaseUserServiceError):
    """Raised when password reset fails."""
    pass
