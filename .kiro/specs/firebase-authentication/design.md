# Design Document

## Overview

Este documento describe el diseño técnico para migrar el sistema de autenticación actual basado en JWT (JSON Web Tokens) y Django REST Framework Simple JWT a Firebase Authentication. La migración mantendrá toda la funcionalidad existente del sistema de roles y permisos mientras aprovecha las capacidades de autenticación gestionada de Firebase.

### Objetivos

1. Reemplazar el sistema de autenticación JWT actual con Firebase Authentication
2. Mantener compatibilidad completa con el sistema de roles (ADMIN, SUPERVISOR, OPERADOR) y permisos existente
3. Sincronizar automáticamente usuarios entre Firebase y Django
4. Preservar toda la funcionalidad de validación de licencias para operadores
5. Minimizar cambios en el código del frontend y backend existente
6. Proporcionar una ruta de migración clara para usuarios existentes

### Beneficios

- **Seguridad mejorada**: Firebase maneja la autenticación con las mejores prácticas de Google
- **Escalabilidad**: Firebase Authentication escala automáticamente
- **Funcionalidades adicionales**: Soporte para autenticación social (Google, Facebook, etc.) en el futuro
- **Gestión de sesiones**: Firebase maneja automáticamente la renovación de tokens
- **Recuperación de contraseñas**: Sistema de recuperación integrado y probado
- **Auditoría**: Logs de autenticación integrados en Firebase Console

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Firebase SDK                                             │  │
│  │  - signInWithEmailAndPassword()                          │  │
│  │  - onAuthStateChanged()                                  │  │
│  │  - getIdToken()                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Firebase ID Token
                             │ (in Authorization header)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Django Backend (DRF)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FirebaseAuthentication (Custom DRF Auth Class)          │  │
│  │  - Validates Firebase ID Token                           │  │
│  │  - Extracts Firebase UID                                 │  │
│  │  - Loads Django User by firebase_uid                     │  │
│  │  - Attaches User to request                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  User Model (Extended)                                    │  │
│  │  - firebase_uid: CharField (unique)                      │  │
│  │  - All existing fields preserved                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Firebase Admin SDK                                       │  │
│  │  - verify_id_token()                                     │  │
│  │  - create_user()                                         │  │
│  │  - update_user()                                         │  │
│  │  - set_custom_user_claims()                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Firebase Authentication                       │
│  - User accounts                                                 │
│  - Password management                                           │
│  - Token generation/validation                                   │
│  - Custom claims (roles, permissions)                            │
└─────────────────────────────────────────────────────────────────┘
```


### Authentication Flow

#### Login Flow

```
1. User enters email/password in frontend
2. Frontend calls Firebase SDK: signInWithEmailAndPassword(email, password)
3. Firebase validates credentials and returns Firebase ID Token
4. Frontend stores token and makes API request with token in Authorization header
5. Backend FirebaseAuthentication class validates token with Firebase Admin SDK
6. Backend extracts firebase_uid from token
7. Backend loads Django User by firebase_uid
8. Backend attaches User to request.user
9. Backend processes request with full access to User model and permissions
```

#### Token Refresh Flow

```
1. Firebase SDK automatically detects token expiration
2. Firebase SDK refreshes token using refresh token
3. Frontend receives new ID token automatically
4. Frontend uses new token for subsequent requests
```

#### Logout Flow

```
1. User clicks logout
2. Frontend calls Firebase SDK: signOut()
3. Frontend clears local storage
4. Firebase revokes session
```

## Components and Interfaces

### Backend Components

#### 1. FirebaseAuthentication (DRF Authentication Class)

**Location**: `backend/apps/authentication/firebase_auth.py`

**Purpose**: Custom Django REST Framework authentication class that validates Firebase ID Tokens

**Interface**:
```python
class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[User, str]]:
        """
        Authenticate request using Firebase ID Token.
        
        Returns:
            Tuple of (User, token) if authentication succeeds
            None if no authentication credentials provided
            
        Raises:
            AuthenticationFailed if token is invalid
        """
        pass
    
    def authenticate_header(self, request: Request) -> str:
        """Return authentication header for 401 responses."""
        return 'Bearer'
```

**Key Methods**:
- `get_token_from_header()`: Extract token from Authorization header
- `verify_firebase_token()`: Validate token with Firebase Admin SDK
- `get_or_create_user()`: Get Django user by firebase_uid
- `cache_token_validation()`: Cache validation results to reduce Firebase API calls


#### 2. FirebaseUserService

**Location**: `backend/apps/authentication/services/firebase_user_service.py`

**Purpose**: Service class for managing Firebase user accounts and synchronization with Django

**Interface**:
```python
class FirebaseUserService:
    def create_firebase_user(self, email: str, password: str, display_name: str) -> str:
        """Create Firebase user and return UID."""
        pass
    
    def update_firebase_user(self, firebase_uid: str, email: str = None, 
                            password: str = None, display_name: str = None) -> bool:
        """Update Firebase user properties."""
        pass
    
    def disable_firebase_user(self, firebase_uid: str) -> bool:
        """Disable Firebase user account."""
        pass
    
    def enable_firebase_user(self, firebase_uid: str) -> bool:
        """Enable Firebase user account."""
        pass
    
    def set_custom_claims(self, firebase_uid: str, claims: Dict[str, Any]) -> bool:
        """Set custom claims in Firebase ID token."""
        pass
    
    def delete_firebase_user(self, firebase_uid: str) -> bool:
        """Delete Firebase user account."""
        pass
    
    def send_password_reset_email(self, email: str) -> bool:
        """Send password reset email via Firebase."""
        pass
```

#### 3. User Model Extension

**Location**: `backend/apps/authentication/models.py`

**Changes**: Add firebase_uid field to existing User model

```python
class User(AbstractUser):
    # ... existing fields ...
    
    # NEW FIELD
    firebase_uid = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Firebase UID',
        help_text='Unique identifier from Firebase Authentication'
    )
    
    # ... existing methods ...
```

**Migration**: Create Django migration to add firebase_uid field

#### 4. User Signals

**Location**: `backend/apps/authentication/signals.py`

**Purpose**: Automatically sync Django user changes to Firebase

```python
@receiver(post_save, sender=User)
def sync_user_to_firebase(sender, instance, created, **kwargs):
    """Sync user changes to Firebase after save."""
    pass

@receiver(pre_delete, sender=User)
def delete_firebase_user_on_delete(sender, instance, **kwargs):
    """Delete Firebase user when Django user is deleted."""
    pass
```


#### 5. Custom Claims Manager

**Location**: `backend/apps/authentication/services/custom_claims_service.py`

**Purpose**: Manage custom claims in Firebase ID tokens for roles and permissions

**Interface**:
```python
class CustomClaimsService:
    def build_claims_for_user(self, user: User) -> Dict[str, Any]:
        """Build custom claims dictionary from Django user."""
        return {
            'role': user.role.name,
            'role_display': user.role.get_name_display(),
            'permissions': list(user.role.permissions.values_list('code', flat=True)),
            'is_admin': user.is_admin(),
            'is_supervisor': user.is_supervisor(),
            'is_operador': user.is_operador(),
            'employee_status': user.employee_status,
            'license_status': self._get_license_status(user) if user.is_operador() else None,
        }
    
    def update_user_claims(self, user: User) -> bool:
        """Update custom claims in Firebase for user."""
        pass
    
    def _get_license_status(self, user: User) -> Dict[str, Any]:
        """Get license status for operador users."""
        return {
            'valid': user.has_valid_license(),
            'expires_soon': user.license_expires_soon(),
            'days_until_expiration': user.days_until_license_expiration(),
        }
```

### Frontend Components

#### 1. Firebase Configuration

**Location**: `frontend/src/config/firebase.ts`

**Purpose**: Initialize Firebase SDK

```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

#### 2. Updated AuthService

**Location**: `frontend/src/services/authService.ts`

**Changes**: Replace JWT authentication with Firebase Authentication

```typescript
import { 
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User as FirebaseUser
} from 'firebase/auth';
import { auth } from '../config/firebase';
import api from './api';

class AuthService {
  async login(email: string, password: string): Promise<LoginResponse> {
    // Sign in with Firebase
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    
    // Get ID token
    const idToken = await userCredential.user.getIdToken();
    
    // Store token
    localStorage.setItem('firebaseToken', idToken);
    
    // Get user profile from backend (includes Django user data)
    const profile = await this.getProfile();
    
    return {
      user: profile,
      token: idToken,
    };
  }
  
  async logout(): Promise<void> {
    await signOut(auth);
    localStorage.removeItem('firebaseToken');
    localStorage.removeItem('user');
  }
  
  async getIdToken(): Promise<string | null> {
    const user = auth.currentUser;
    if (user) {
      return await user.getIdToken();
    }
    return null;
  }
  
  onAuthStateChanged(callback: (user: FirebaseUser | null) => void) {
    return onAuthStateChanged(auth, callback);
  }
}
```


#### 3. API Interceptor

**Location**: `frontend/src/services/api.ts`

**Changes**: Update axios interceptor to use Firebase ID token

```typescript
// Request interceptor - attach Firebase ID token
api.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, Firebase SDK will auto-refresh
      const user = auth.currentUser;
      if (user) {
        const newToken = await user.getIdToken(true); // Force refresh
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return api.request(error.config);
      }
    }
    return Promise.reject(error);
  }
);
```

## Data Models

### User Model Changes

**Migration**: `backend/apps/authentication/migrations/XXXX_add_firebase_uid.py`

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='firebase_uid',
            field=models.CharField(
                max_length=128,
                unique=True,
                null=True,
                blank=True,
                verbose_name='Firebase UID'
            ),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['firebase_uid'], name='auth_user_firebase_uid_idx'),
        ),
    ]
```

### Custom Claims Structure

Custom claims stored in Firebase ID tokens:

```json
{
  "role": "ADMIN",
  "role_display": "Administrador",
  "permissions": [
    "users.view",
    "users.create",
    "users.update",
    "users.delete",
    "assets.view",
    "assets.create",
    ...
  ],
  "is_admin": true,
  "is_supervisor": false,
  "is_operador": false,
  "employee_status": "ACTIVE",
  "license_status": null
}
```

For OPERADOR users:

```json
{
  "role": "OPERADOR",
  "role_display": "Operador",
  "permissions": ["assets.view", "checklists.create", ...],
  "is_admin": false,
  "is_supervisor": false,
  "is_operador": true,
  "employee_status": "ACTIVE",
  "license_status": {
    "valid": true,
    "expires_soon": false,
    "days_until_expiration": 45
  }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Frontend Authentication Properties

**Property 1: Successful login returns valid Firebase token**
*For any* valid email and password combination, calling the Firebase login function should return a Firebase ID Token that matches the expected JWT format and contains a valid signature.
**Validates: Requirements 1.1**

**Property 2: Token storage and usage**
*For any* successful login, the Firebase ID Token should be stored in local storage and automatically included in the Authorization header of all subsequent API requests.
**Validates: Requirements 1.2**

**Property 3: Automatic token refresh**
*For any* expired Firebase ID Token, the Firebase SDK should automatically refresh the token without requiring user re-authentication, and the new token should be used for subsequent requests.
**Validates: Requirements 1.3**

**Property 4: Logout clears all authentication state**
*For any* authenticated user, calling logout should clear all tokens from local storage, revoke the Firebase session, and result in subsequent API requests failing with 401 Unauthorized.
**Validates: Requirements 1.4**

**Property 5: Authentication errors display appropriate messages**
*For any* authentication failure (invalid credentials, network error, etc.), the frontend should display an error message that corresponds to the specific failure type.
**Validates: Requirements 1.5**

### Backend Token Validation Properties

**Property 6: Token validation correctness**
*For any* API request with a Firebase ID Token, the authentication middleware should verify the token signature and return success for valid tokens and HTTP 401 for invalid or expired tokens.
**Validates: Requirements 2.1, 2.3**

**Property 7: Valid token attaches correct user**
*For any* valid Firebase ID Token, the authentication middleware should extract the Firebase UID, load the corresponding Django User object, and attach it to request.user with all fields intact.
**Validates: Requirements 2.2**

**Property 8: Token validation caching**
*For any* Firebase ID Token, making multiple requests with the same token within the cache period should result in only one Firebase Admin SDK verification call, with subsequent validations served from cache.
**Validates: Requirements 2.4**


### User Synchronization Properties

**Property 9: User creation creates Firebase account and stores UID**
*For any* new Django user created with email and password, a corresponding Firebase Authentication account should be created with the same email, and the Firebase UID should be stored in the user's firebase_uid field.
**Validates: Requirements 3.1, 3.2**

**Property 10: Password changes sync to Firebase**
*For any* Django user with a firebase_uid, changing the user's password in Django should result in the password being updated in Firebase Authentication.
**Validates: Requirements 3.3**

**Property 11: User deactivation syncs to Firebase**
*For any* Django user with a firebase_uid, setting is_active to False should result in the Firebase Authentication account being disabled, and setting is_active to True should enable it.
**Validates: Requirements 3.4, 3.5, 7.3**

### Custom Claims Properties

**Property 12: Custom claims contain complete user data**
*For any* authenticated user, the Firebase ID Token custom claims should include role, role_display, permissions list, role flags (is_admin, is_supervisor, is_operador), employee_status, and license_status (for operador users).
**Validates: Requirements 4.1, 4.2**

**Property 13: Frontend can decode custom claims**
*For any* Firebase ID Token received by the frontend, decoding the token should successfully extract all custom claims fields and make them available for authorization decisions.
**Validates: Requirements 4.3**

**Property 14: Role changes update custom claims**
*For any* Django user, changing the user's role or permissions should trigger an update to the Firebase custom claims, and the changes should be present in tokens obtained after the next refresh.
**Validates: Requirements 4.4, 4.5**

### Backward Compatibility Properties

**Property 15: Existing user model methods work**
*For any* authenticated request, all existing Django User model methods (is_admin(), can_manage_users(), has_valid_license(), etc.) should continue to work correctly and return the same values as before the migration.
**Validates: Requirements 5.1, 5.2, 5.4**

**Property 16: Existing permission classes work**
*For any* API endpoint with existing DRF permission classes, the permission checks should continue to work correctly with Firebase authentication without modification.
**Validates: Requirements 5.3**

**Property 17: User data integrity**
*For any* user management operation (create, update, deactivate), all existing user fields (RUT, phone, license_type, license_expiration_date, etc.) should be preserved and remain accessible.
**Validates: Requirements 5.5**

### License Validation Properties

**Property 18: License status in custom claims**
*For any* OPERADOR user, logging in should result in custom claims that include license_status with valid, expires_soon, and days_until_expiration fields calculated from the license_expiration_date.
**Validates: Requirements 6.1**

**Property 19: License validation correctness**
*For any* OPERADOR user, the license validation logic should correctly determine if the license is valid (not expired), expiring soon (within 30 days), or expired based on the license_expiration_date compared to the current date.
**Validates: Requirements 6.2, 6.3, 6.4**


### Admin User Management Properties

**Property 20: Admin user creation creates Firebase account**
*For any* user created by an ADMIN through Django admin or API, a Firebase Authentication account should be automatically created, and the operation should succeed or rollback completely if Firebase creation fails.
**Validates: Requirements 7.1, 7.5**

**Property 21: Admin password reset syncs to Firebase**
*For any* user, when an ADMIN resets the password, the new password should be updated in both Django and Firebase Authentication.
**Validates: Requirements 7.2**

**Property 22: Firebase operation failures are logged**
*For any* Firebase operation that fails (user creation, update, disable, etc.), the error should be logged with detailed information including the operation type, user ID, and error message.
**Validates: Requirements 7.4**

### Migration Properties

**Property 23: Migration creates Firebase accounts for all users**
*For any* set of existing Django users without firebase_uid, running the migration script should create Firebase Authentication accounts for all users and store the Firebase UIDs.
**Validates: Requirements 8.1, 8.2**

**Property 24: Migration handles existing Firebase accounts**
*For any* Django user whose email already has a Firebase Authentication account, the migration script should link the existing Firebase UID to the Django user rather than attempting to create a duplicate account.
**Validates: Requirements 8.4**

**Property 25: Migration error resilience**
*For any* migration run where some user migrations fail, the script should log detailed error information for failed users and continue processing remaining users without stopping.
**Validates: Requirements 8.5**

### Audit Logging Properties

**Property 26: Successful authentication is logged**
*For any* successful user login, an audit log entry should be created containing the timestamp, user ID, email, and source IP address.
**Validates: Requirements 10.1**

**Property 27: Failed authentication is logged**
*For any* failed authentication attempt, an audit log entry should be created containing the timestamp, attempted email, failure reason, and source IP address.
**Validates: Requirements 10.2**

**Property 28: Token validation failures are logged**
*For any* invalid or expired token validation attempt, a log entry should be created, but successful token validations should not be logged to reduce log volume.
**Validates: Requirements 10.3**

**Property 29: Logs include correlation IDs**
*For any* request that generates log entries, all log entries for that request should include the same correlation ID to enable tracking across services.
**Validates: Requirements 10.5**

## Error Handling

### Firebase Authentication Errors

**Error Types**:
1. **Invalid Credentials**: Wrong email/password
2. **User Not Found**: Firebase user exists but no Django user
3. **User Disabled**: Firebase account is disabled
4. **Token Expired**: ID token has expired
5. **Token Invalid**: Malformed or tampered token
6. **Network Error**: Cannot reach Firebase services
7. **Quota Exceeded**: Firebase API quota exceeded

**Handling Strategy**:
```python
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

# Error responses
ERROR_RESPONSES = {
    'invalid_credentials': {
        'code': 'auth/invalid-credentials',
        'message': 'Email o contraseña incorrectos',
        'status': 401
    },
    'user_not_found': {
        'code': 'auth/user-not-found',
        'message': 'Usuario no encontrado en el sistema',
        'status': 403
    },
    'token_expired': {
        'code': 'auth/token-expired',
        'message': 'Token expirado, por favor inicia sesión nuevamente',
        'status': 401
    },
    'token_invalid': {
        'code': 'auth/invalid-token',
        'message': 'Token inválido',
        'status': 401
    },
}
```


### Synchronization Error Handling

**Scenarios**:
1. **Firebase User Creation Fails**: Rollback Django user creation
2. **Firebase User Update Fails**: Log error, retry with exponential backoff
3. **Custom Claims Update Fails**: Log error, user can still authenticate but may have stale permissions
4. **Network Timeout**: Retry operation up to 3 times

**Implementation**:
```python
from django.db import transaction

@transaction.atomic
def create_user_with_firebase(email, password, **user_data):
    """Create user with automatic rollback if Firebase fails."""
    try:
        # Create Django user
        user = User.objects.create_user(email=email, password=password, **user_data)
        
        # Create Firebase user
        firebase_uid = firebase_service.create_firebase_user(
            email=email,
            password=password,
            display_name=user.get_full_name()
        )
        
        # Store Firebase UID
        user.firebase_uid = firebase_uid
        user.save()
        
        # Set custom claims
        claims_service.update_user_claims(user)
        
        return user
        
    except FirebaseError as e:
        # Transaction will automatically rollback
        logger.error(f"Failed to create Firebase user: {e}")
        raise
```

## Testing Strategy

### Unit Testing

**Framework**: pytest with pytest-django

**Test Coverage**:
1. **FirebaseAuthentication class**:
   - Test token extraction from headers
   - Test token validation with valid/invalid tokens
   - Test user loading by firebase_uid
   - Test caching behavior

2. **FirebaseUserService**:
   - Test user creation in Firebase
   - Test user updates (email, password, display_name)
   - Test user disable/enable
   - Test custom claims setting
   - Test error handling

3. **CustomClaimsService**:
   - Test claims building for different roles
   - Test license status calculation
   - Test claims updates

4. **User Model**:
   - Test firebase_uid field constraints
   - Test existing methods still work

5. **Signals**:
   - Test user save triggers Firebase sync
   - Test user delete triggers Firebase delete

**Example Unit Test**:
```python
import pytest
from apps.authentication.firebase_auth import FirebaseAuthentication
from apps.authentication.models import User, Role

@pytest.mark.django_db
def test_firebase_authentication_valid_token(mock_firebase_admin):
    """Test that valid Firebase token authenticates user."""
    # Create test user
    role = Role.objects.get(name=Role.ADMIN)
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        rut='12345678-9',
        role=role,
        firebase_uid='test-firebase-uid'
    )
    
    # Mock Firebase token verification
    mock_firebase_admin.auth.verify_id_token.return_value = {
        'uid': 'test-firebase-uid',
        'email': 'test@example.com'
    }
    
    # Create mock request with token
    request = MockRequest()
    request.META['HTTP_AUTHORIZATION'] = 'Bearer valid-token'
    
    # Authenticate
    auth = FirebaseAuthentication()
    result = auth.authenticate(request)
    
    assert result is not None
    authenticated_user, token = result
    assert authenticated_user.id == user.id
    assert authenticated_user.email == user.email
```


### Property-Based Testing

**Framework**: Hypothesis for Python, fast-check for TypeScript

**Configuration**: Each property-based test should run a minimum of 100 iterations to ensure comprehensive coverage of the input space.

**Test Tagging**: Each property-based test must include a comment explicitly referencing the correctness property using the format: `**Feature: firebase-authentication, Property {number}: {property_text}**`

**Property Tests**:

1. **Token Validation Property Test**:
```python
from hypothesis import given, strategies as st
import pytest

@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=128),
)
@pytest.mark.django_db
def test_property_valid_login_returns_token(email, password, mock_firebase):
    """
    **Feature: firebase-authentication, Property 1: Successful login returns valid Firebase token**
    
    For any valid email and password, login should return a valid Firebase ID Token.
    """
    # Mock Firebase authentication
    mock_firebase.auth.sign_in_with_email_and_password.return_value = {
        'idToken': 'valid-firebase-token',
        'refreshToken': 'refresh-token',
        'localId': 'firebase-uid'
    }
    
    # Attempt login
    result = auth_service.login(email, password)
    
    # Verify token is returned and has correct format
    assert 'idToken' in result
    assert isinstance(result['idToken'], str)
    assert len(result['idToken']) > 0
```

2. **User Synchronization Property Test**:
```python
@given(
    email=st.emails(),
    first_name=st.text(min_size=1, max_size=50),
    last_name=st.text(min_size=1, max_size=50),
    rut=st.text(min_size=9, max_size=12),
)
@pytest.mark.django_db
def test_property_user_creation_creates_firebase_account(
    email, first_name, last_name, rut, mock_firebase_admin
):
    """
    **Feature: firebase-authentication, Property 9: User creation creates Firebase account and stores UID**
    
    For any new Django user, a Firebase account should be created and UID stored.
    """
    # Mock Firebase user creation
    expected_uid = f'firebase-{email}'
    mock_firebase_admin.auth.create_user.return_value = MockFirebaseUser(uid=expected_uid)
    
    # Create Django user
    role = Role.objects.get(name=Role.OPERADOR)
    user = User.objects.create_user(
        email=email,
        password='testpass123',
        first_name=first_name,
        last_name=last_name,
        rut=rut,
        role=role
    )
    
    # Verify Firebase user was created
    mock_firebase_admin.auth.create_user.assert_called_once()
    
    # Verify UID was stored
    user.refresh_from_db()
    assert user.firebase_uid == expected_uid
```

3. **Custom Claims Property Test**:
```python
@given(
    role_name=st.sampled_from([Role.ADMIN, Role.SUPERVISOR, Role.OPERADOR]),
)
@pytest.mark.django_db
def test_property_custom_claims_contain_complete_data(role_name, mock_firebase_admin):
    """
    **Feature: firebase-authentication, Property 12: Custom claims contain complete user data**
    
    For any user role, custom claims should include all required fields.
    """
    # Create user with specified role
    role = Role.objects.get(name=role_name)
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        rut='12345678-9',
        role=role,
        firebase_uid='test-uid'
    )
    
    # Build custom claims
    claims_service = CustomClaimsService()
    claims = claims_service.build_claims_for_user(user)
    
    # Verify all required fields are present
    assert 'role' in claims
    assert 'role_display' in claims
    assert 'permissions' in claims
    assert 'is_admin' in claims
    assert 'is_supervisor' in claims
    assert 'is_operador' in claims
    assert 'employee_status' in claims
    
    # Verify role-specific fields
    if role_name == Role.OPERADOR:
        assert 'license_status' in claims
        assert claims['license_status'] is not None
    
    # Verify values match user
    assert claims['role'] == user.role.name
    assert claims['is_admin'] == user.is_admin()
```

4. **License Validation Property Test**:
```python
from datetime import date, timedelta

@given(
    days_until_expiration=st.integers(min_value=-365, max_value=365),
)
@pytest.mark.django_db
def test_property_license_validation_correctness(days_until_expiration):
    """
    **Feature: firebase-authentication, Property 19: License validation correctness**
    
    For any license expiration date, validation should correctly determine status.
    """
    # Create operador user with license
    role = Role.objects.get(name=Role.OPERADOR)
    expiration_date = date.today() + timedelta(days=days_until_expiration)
    
    user = User.objects.create_user(
        email='operador@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Operador',
        rut='12345678-9',
        role=role,
        license_type=User.LICENSE_MUNICIPAL,
        license_expiration_date=expiration_date
    )
    
    # Check validation results
    is_valid = user.has_valid_license()
    expires_soon = user.license_expires_soon()
    days_left = user.days_until_license_expiration()
    
    # Verify correctness
    if days_until_expiration < 0:
        assert not is_valid, "Expired license should be invalid"
        assert not expires_soon, "Expired license should not be 'expiring soon'"
    elif 0 <= days_until_expiration <= 30:
        assert is_valid, "License expiring soon should still be valid"
        assert expires_soon, "License within 30 days should be expiring soon"
    else:
        assert is_valid, "Future license should be valid"
        assert not expires_soon, "License > 30 days away should not be expiring soon"
    
    assert days_left == days_until_expiration
```

5. **Token Caching Property Test**:
```python
@given(
    num_requests=st.integers(min_value=2, max_value=10),
)
def test_property_token_validation_caching(num_requests, mock_firebase_admin):
    """
    **Feature: firebase-authentication, Property 8: Token validation caching**
    
    For any number of requests with the same token, Firebase should only be called once.
    """
    token = 'test-token'
    mock_firebase_admin.auth.verify_id_token.return_value = {
        'uid': 'test-uid',
        'email': 'test@example.com'
    }
    
    auth = FirebaseAuthentication()
    
    # Make multiple requests with same token
    for _ in range(num_requests):
        request = MockRequest()
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        auth.authenticate(request)
    
    # Verify Firebase was only called once (first request)
    assert mock_firebase_admin.auth.verify_id_token.call_count == 1
```

### Integration Testing

**Test Scenarios**:
1. **End-to-end login flow**: Frontend login → Firebase auth → Backend API call → Response
2. **Token refresh flow**: Expired token → Auto refresh → Successful API call
3. **User creation flow**: Admin creates user → Firebase account created → User can login
4. **Password reset flow**: Request reset → Receive email → Reset password → Login with new password
5. **Role change flow**: Admin changes role → Custom claims updated → Frontend sees new permissions

**Example Integration Test**:
```python
@pytest.mark.integration
def test_end_to_end_login_flow(client, mock_firebase):
    """Test complete login flow from frontend to backend."""
    # Setup
    role = Role.objects.get(name=Role.ADMIN)
    user = User.objects.create_user(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        rut='12345678-9',
        role=role,
        firebase_uid='admin-firebase-uid'
    )
    
    # Mock Firebase authentication
    mock_firebase.auth.sign_in_with_email_and_password.return_value = {
        'idToken': 'valid-token',
        'refreshToken': 'refresh-token'
    }
    
    # Mock token verification
    mock_firebase.auth.verify_id_token.return_value = {
        'uid': 'admin-firebase-uid',
        'email': 'admin@example.com'
    }
    
    # Step 1: Login
    response = client.post('/api/v1/auth/login/', {
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    assert response.status_code == 200
    assert 'idToken' in response.json()
    
    # Step 2: Make authenticated API call
    token = response.json()['idToken']
    response = client.get(
        '/api/v1/auth/profile/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert response.status_code == 200
    assert response.json()['email'] == 'admin@example.com'
```

## Migration Strategy

### Phase 1: Preparation (Week 1)

1. **Setup Firebase Project**:
   - Create Firebase project in Google Cloud Console
   - Enable Firebase Authentication
   - Download service account credentials
   - Configure Firebase in backend settings

2. **Database Migration**:
   - Create migration to add firebase_uid field to User model
   - Run migration in development environment
   - Test migration rollback

3. **Install Dependencies**:
   - Backend: `firebase-admin`
   - Frontend: `firebase` SDK

### Phase 2: Backend Implementation (Week 2-3)

1. **Implement Core Components**:
   - FirebaseAuthentication class
   - FirebaseUserService
   - CustomClaimsService
   - User signals for synchronization

2. **Update Settings**:
   - Add Firebase configuration
   - Update REST_FRAMEWORK authentication classes
   - Configure caching for token validation

3. **Testing**:
   - Write unit tests for all components
   - Write property-based tests
   - Run tests in CI/CD pipeline

### Phase 3: Frontend Implementation (Week 3-4)

1. **Setup Firebase SDK**:
   - Initialize Firebase in frontend
   - Create Firebase configuration file

2. **Update AuthService**:
   - Replace JWT login with Firebase login
   - Update token management
   - Implement auto-refresh

3. **Update API Client**:
   - Modify axios interceptors
   - Handle token refresh in error interceptor

4. **Testing**:
   - Test login/logout flows
   - Test token refresh
   - Test error handling

### Phase 4: User Migration (Week 4)

1. **Create Migration Script**:
   - Script to create Firebase accounts for existing users
   - Generate temporary passwords
   - Store Firebase UIDs

2. **Run Migration**:
   - Backup database
   - Run migration script in production
   - Monitor for errors

3. **Send Password Reset Emails**:
   - Send emails to all migrated users
   - Provide instructions for password reset

### Phase 5: Deployment and Monitoring (Week 5)

1. **Deploy Backend**:
   - Deploy updated backend to production
   - Monitor logs for errors
   - Check Firebase usage metrics

2. **Deploy Frontend**:
   - Deploy updated frontend
   - Monitor authentication success rate
   - Check for client-side errors

3. **Monitoring**:
   - Set up alerts for authentication failures
   - Monitor Firebase quota usage
   - Track migration completion rate

### Rollback Plan

If critical issues are discovered:

1. **Immediate Rollback**:
   - Revert frontend to previous version (JWT-based)
   - Revert backend authentication to JWT
   - Users can continue using system with JWT

2. **Data Preservation**:
   - Firebase UIDs remain in database
   - Can retry migration after fixing issues
   - No data loss

3. **Communication**:
   - Notify users of temporary issues
   - Provide timeline for resolution
   - Send update when migration is complete

## Security Considerations

### Token Security

1. **Token Storage**: Store Firebase ID tokens in memory or secure storage, never in cookies without HttpOnly flag
2. **Token Transmission**: Always use HTTPS for token transmission
3. **Token Expiration**: Firebase tokens expire after 1 hour, requiring refresh
4. **Token Validation**: Always validate tokens on backend, never trust client-side validation

### Firebase Security Rules

```javascript
// Firestore security rules for chat and notifications
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated users can read/write
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
    
    // Chat rooms - only participants can access
    match /chat_rooms/{roomId} {
      allow read: if request.auth.uid in resource.data.participants;
      allow write: if request.auth.uid in resource.data.participants;
    }
    
    // User presence - users can only update their own presence
    match /user_presence/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId;
    }
  }
}
```

### Rate Limiting

Implement rate limiting to prevent abuse:
- Login attempts: 5 per minute per IP
- Token refresh: 10 per minute per user
- Password reset: 3 per hour per email

### Audit Logging

Log all authentication events:
- Successful logins
- Failed login attempts
- Token validation failures
- Password changes
- User creation/deletion

## Performance Considerations

### Token Validation Caching

Cache Firebase token validation results to reduce API calls:
- Cache duration: 5 minutes
- Cache key: SHA256 hash of token
- Cache invalidation: On user role/permission change

### Firebase API Quota

Firebase Authentication free tier limits:
- 50,000 verifications per day
- With caching, should support ~10,000 daily active users

### Database Queries

Optimize user lookups:
- Index on firebase_uid field
- Use select_related for role and permissions
- Cache user objects for 5 minutes

## Cost Analysis

### Firebase Authentication Costs

- **Free Tier**: 50,000 monthly active users
- **Paid Tier**: $0.0055 per verification after free tier
- **Expected Cost**: $0 (well within free tier for current user base)

### Firebase Admin SDK Costs

- **Token Verification**: Free (included in Authentication)
- **User Management**: Free (included in Authentication)
- **Custom Claims**: Free (included in Authentication)

### Total Estimated Cost

- **Current**: $0 (using free tier)
- **At Scale (10,000 users)**: $0 (still within free tier)
- **At Scale (100,000 users)**: ~$275/month

## Conclusion

This design provides a comprehensive migration path from JWT-based authentication to Firebase Authentication while maintaining full backward compatibility with the existing system. The migration preserves all functionality including the role-based permission system, license validation for operators, and user management capabilities. The phased approach allows for careful testing and monitoring at each step, with a clear rollback plan if issues arise.
