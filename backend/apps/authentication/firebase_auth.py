"""
Firebase Authentication backend for Django REST Framework.
Validates Firebase ID tokens and authenticates users.
"""
import logging
from typing import Optional, Tuple

from django.core.cache import cache
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.request import Request

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

from apps.authentication.models import User

logger = logging.getLogger(__name__)


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Custom DRF authentication class that validates Firebase ID tokens.
    
    This class:
    1. Extracts the Firebase ID token from the Authorization header
    2. Validates the token using Firebase Admin SDK
    3. Retrieves the Django User by firebase_uid
    4. Caches token validation results to reduce Firebase API calls
    
    Usage:
        Add to REST_FRAMEWORK settings:
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'apps.authentication.firebase_auth.FirebaseAuthentication',
        ]
    """
    
    keyword = 'Bearer'
    
    def __init__(self):
        """Initialize Firebase Admin SDK if not already initialized."""
        super().__init__()
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with service account credentials."""
        if firebase_admin._apps:
            # Already initialized
            return
        
        try:
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
            
            if not cred_path:
                logger.warning("FIREBASE_CREDENTIALS_PATH not configured. Firebase authentication will not work.")
                return
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': getattr(settings, 'FIREBASE_DATABASE_URL', None),
                'storageBucket': getattr(settings, 'FIREBASE_STORAGE_BUCKET', None),
            })
            
            logger.info("Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            raise
    
    def authenticate(self, request: Request) -> Optional[Tuple[User, str]]:
        """
        Authenticate the request using Firebase ID token.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Tuple of (User, token) if authentication succeeds
            None if no authentication credentials provided
            
        Raises:
            AuthenticationFailed: If token is invalid or user not found
        """
        # Extract token from header
        token = self.get_token_from_header(request)
        
        if not token:
            return None
        
        # Verify token and get Firebase UID
        firebase_uid = self.verify_firebase_token(token)
        
        if not firebase_uid:
            raise exceptions.AuthenticationFailed('Invalid or expired token')
        
        # Get Django user by firebase_uid
        user = self.get_user_by_firebase_uid(firebase_uid)
        
        if not user:
            raise exceptions.AuthenticationFailed('User not found')
        
        # Check if user is active
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled')
        
        return (user, token)
    
    def authenticate_header(self, request: Request) -> str:
        """
        Return the authentication header for 401 responses.
        
        Args:
            request: The HTTP request object
            
        Returns:
            String to be used as WWW-Authenticate header value
        """
        return self.keyword
    
    def get_token_from_header(self, request: Request) -> Optional[str]:
        """
        Extract Firebase ID token from Authorization header.
        
        Expected format: "Bearer <token>"
        
        Args:
            request: The HTTP request object
            
        Returns:
            Token string if found, None otherwise
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2:
            return None
        
        if parts[0].lower() != self.keyword.lower():
            return None
        
        return parts[1]
    
    def verify_firebase_token(self, token: str) -> Optional[str]:
        """
        Verify Firebase ID token and return Firebase UID.
        
        This method:
        1. Checks cache for previously validated token
        2. If not cached, validates with Firebase Admin SDK
        3. Caches the result for future requests
        
        Args:
            token: Firebase ID token string
            
        Returns:
            Firebase UID if token is valid, None otherwise
        """
        # Check cache first
        cache_key = f'firebase_token:{token[:50]}'  # Use first 50 chars as key
        cached_uid = cache.get(cache_key)
        
        if cached_uid:
            logger.debug(f"Token validation cache hit for UID: {cached_uid}")
            return cached_uid
        
        # Validate with Firebase
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            firebase_uid = decoded_token.get('uid')
            
            if not firebase_uid:
                logger.warning("Token validation succeeded but no UID found")
                return None
            
            # Cache the result
            cache_ttl = getattr(settings, 'FIREBASE_TOKEN_CACHE_TTL', 300)  # 5 minutes default
            cache.set(cache_key, firebase_uid, cache_ttl)
            
            logger.debug(f"Token validated successfully for UID: {firebase_uid}")
            return firebase_uid
            
        except firebase_auth.InvalidIdTokenError as e:
            logger.warning(f"Invalid Firebase token: {str(e)}")
            return None
        except firebase_auth.ExpiredIdTokenError as e:
            logger.warning(f"Expired Firebase token: {str(e)}")
            return None
        except firebase_auth.RevokedIdTokenError as e:
            logger.warning(f"Revoked Firebase token: {str(e)}")
            return None
        except firebase_auth.CertificateFetchError as e:
            logger.error(f"Error fetching Firebase certificates: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error validating Firebase token: {str(e)}")
            return None
    
    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """
        Retrieve Django User by Firebase UID.
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            User object if found, None otherwise
        """
        try:
            user = User.objects.select_related('role').get(
                firebase_uid=firebase_uid,
                is_active=True
            )
            return user
        except User.DoesNotExist:
            logger.warning(f"No Django user found for Firebase UID: {firebase_uid}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by Firebase UID: {str(e)}")
            return None


class FirebaseAuthenticationError(Exception):
    """Base exception for Firebase authentication errors."""
    pass


class InvalidCredentialsError(FirebaseAuthenticationError):
    """Raised when credentials are invalid."""
    pass


class UserNotFoundError(FirebaseAuthenticationError):
    """Raised when Firebase user exists but Django user doesn't."""
    pass


class TokenExpiredError(FirebaseAuthenticationError):
    """Raised when token has expired."""
    pass


class TokenInvalidError(FirebaseAuthenticationError):
    """Raised when token is invalid or malformed."""
    pass
