# Requirements Document

## Introduction

Este documento especifica los requisitos para migrar el sistema de autenticación actual basado en JWT (JSON Web Tokens) y Django REST Framework a Firebase Authentication. La migración permitirá aprovechar las capacidades de autenticación gestionada de Firebase, incluyendo autenticación por email/contraseña, proveedores sociales, y gestión de sesiones, mientras se mantiene la compatibilidad con el sistema de roles y permisos existente en el backend Django.

## Glossary

- **Firebase Authentication**: Servicio de autenticación gestionado por Google Firebase que proporciona backend de autenticación, SDKs fáciles de usar y bibliotecas de UI listas para usar
- **CMMS Backend**: Sistema backend Django REST Framework que gestiona usuarios, roles, permisos y lógica de negocio
- **JWT Token**: JSON Web Token utilizado actualmente para autenticación stateless
- **Firebase ID Token**: Token JWT emitido por Firebase Authentication que contiene información del usuario autenticado
- **Custom Claims**: Datos personalizados que se pueden agregar a los Firebase ID Tokens para incluir información como roles y permisos
- **Frontend Application**: Aplicación React/TypeScript que proporciona la interfaz de usuario
- **User Sync**: Proceso de sincronización entre usuarios de Firebase y usuarios en la base de datos Django
- **Role System**: Sistema de roles existente (ADMIN, SUPERVISOR, OPERADOR) en el backend Django
- **Authentication Middleware**: Middleware Django que valida Firebase ID Tokens en las peticiones HTTP

## Requirements

### Requirement 1

**User Story:** Como usuario del sistema, quiero iniciar sesión usando Firebase Authentication, para que pueda acceder al sistema de manera segura con autenticación gestionada por Google.

#### Acceptance Criteria

1. WHEN a user provides valid email and password THEN the Frontend Application SHALL authenticate with Firebase Authentication and obtain a Firebase ID Token
2. WHEN Firebase Authentication succeeds THEN the Frontend Application SHALL store the Firebase ID Token and use it for subsequent API requests
3. WHEN a user session expires THEN the Frontend Application SHALL automatically refresh the Firebase ID Token without requiring re-login
4. WHEN a user logs out THEN the Frontend Application SHALL revoke the Firebase session and clear all stored authentication tokens
5. WHERE Firebase Authentication fails THEN the Frontend Application SHALL display appropriate error messages to the user

### Requirement 2

**User Story:** Como desarrollador del backend, quiero validar Firebase ID Tokens en el backend Django, para que pueda verificar la identidad de los usuarios en cada petición API.

#### Acceptance Criteria

1. WHEN the CMMS Backend receives an API request with a Firebase ID Token THEN the Authentication Middleware SHALL verify the token signature using Firebase Admin SDK
2. WHEN a Firebase ID Token is valid THEN the Authentication Middleware SHALL extract the user UID and attach the corresponding Django User object to the request
3. WHEN a Firebase ID Token is invalid or expired THEN the Authentication Middleware SHALL reject the request with HTTP 401 Unauthorized
4. WHEN the Authentication Middleware processes a token THEN the CMMS Backend SHALL cache token validation results to minimize Firebase API calls
5. WHERE a Firebase UID does not correspond to a Django User THEN the Authentication Middleware SHALL reject the request with HTTP 403 Forbidden

### Requirement 3

**User Story:** Como administrador del sistema, quiero que los usuarios se sincronicen automáticamente entre Firebase y Django, para que la información de usuarios esté consistente en ambos sistemas.

#### Acceptance Criteria

1. WHEN a new user is created in Django THEN the CMMS Backend SHALL create a corresponding Firebase Authentication user with the same email
2. WHEN a Firebase user is created THEN the CMMS Backend SHALL store the Firebase UID in the Django User model
3. WHEN a user password is changed in Django THEN the CMMS Backend SHALL update the password in Firebase Authentication
4. WHEN a user is deactivated in Django THEN the CMMS Backend SHALL disable the corresponding Firebase Authentication account
5. WHEN a user is reactivated in Django THEN the CMMS Backend SHALL enable the corresponding Firebase Authentication account

### Requirement 4

**User Story:** Como usuario con un rol específico, quiero que mis permisos se incluyan en mi token de autenticación, para que el frontend pueda mostrar u ocultar funcionalidades según mis permisos sin consultar el backend.

#### Acceptance Criteria

1. WHEN a user logs in successfully THEN the CMMS Backend SHALL set Custom Claims in the Firebase ID Token with the user's role and permissions
2. WHEN Custom Claims are set THEN the Firebase ID Token SHALL include the user's role name, role display name, and permission codes
3. WHEN the Frontend Application receives a Firebase ID Token THEN the Frontend Application SHALL decode the Custom Claims to determine user permissions
4. WHEN a user's role or permissions change in Django THEN the CMMS Backend SHALL update the Custom Claims in Firebase
5. WHERE Custom Claims are updated THEN the changes SHALL take effect on the next token refresh

### Requirement 5

**User Story:** Como desarrollador, quiero mantener la compatibilidad con el sistema de roles y permisos existente, para que no sea necesario reescribir la lógica de autorización del backend.

#### Acceptance Criteria

1. WHEN the Authentication Middleware validates a token THEN the CMMS Backend SHALL continue using the existing Django User model and Role system
2. WHEN authorization checks are performed THEN the CMMS Backend SHALL use the existing permission methods (can_manage_users, can_view_all_resources, etc.)
3. WHEN API endpoints check permissions THEN the CMMS Backend SHALL use the existing DRF permission classes without modification
4. WHERE license validation is required THEN the CMMS Backend SHALL continue using the existing license validation methods
5. WHEN user management operations occur THEN the CMMS Backend SHALL maintain all existing user fields (RUT, phone, license info, etc.)

### Requirement 6

**User Story:** Como usuario operador, quiero que mi información de licencia se valide correctamente, para que el sistema continúe verificando que tengo una licencia válida para operar equipos.

#### Acceptance Criteria

1. WHEN an OPERADOR user logs in THEN the CMMS Backend SHALL include license status in the Custom Claims
2. WHEN license validation is required THEN the CMMS Backend SHALL check the license expiration date against the current date
3. WHEN a license is about to expire THEN the CMMS Backend SHALL include an expiring_soon flag in the Custom Claims
4. WHERE a license has expired THEN the CMMS Backend SHALL include an expired flag in the Custom Claims
5. WHEN the Frontend Application receives license status THEN the Frontend Application SHALL display appropriate warnings or restrictions

### Requirement 7

**User Story:** Como administrador, quiero gestionar usuarios desde el panel de administración Django, para que pueda crear, modificar y desactivar usuarios con sincronización automática a Firebase.

#### Acceptance Criteria

1. WHEN an ADMIN creates a user through the Django admin or API THEN the CMMS Backend SHALL automatically create the Firebase Authentication account
2. WHEN an ADMIN resets a user password THEN the CMMS Backend SHALL update the password in both Django and Firebase
3. WHEN an ADMIN deactivates a user THEN the CMMS Backend SHALL disable the Firebase Authentication account
4. WHERE Firebase operations fail THEN the CMMS Backend SHALL log the error and notify the administrator
5. WHEN user creation in Firebase fails THEN the CMMS Backend SHALL rollback the Django user creation to maintain consistency

### Requirement 8

**User Story:** Como desarrollador, quiero migrar usuarios existentes a Firebase Authentication, para que los usuarios actuales puedan continuar usando el sistema sin crear nuevas cuentas.

#### Acceptance Criteria

1. WHEN the migration script runs THEN the CMMS Backend SHALL create Firebase Authentication accounts for all existing Django users
2. WHEN creating Firebase accounts during migration THEN the CMMS Backend SHALL generate temporary passwords and store Firebase UIDs
3. WHEN migration completes THEN the CMMS Backend SHALL send password reset emails to all migrated users
4. WHERE a Firebase account already exists for an email THEN the migration script SHALL link the existing Firebase UID to the Django user
5. WHEN migration errors occur THEN the migration script SHALL log detailed error information and continue with remaining users

### Requirement 9

**User Story:** Como usuario del sistema, quiero poder restablecer mi contraseña usando Firebase, para que pueda recuperar el acceso a mi cuenta si olvido mi contraseña.

#### Acceptance Criteria

1. WHEN a user requests password reset THEN the Frontend Application SHALL use Firebase Authentication password reset functionality
2. WHEN password reset is requested THEN Firebase Authentication SHALL send a password reset email to the user
3. WHEN a user clicks the reset link THEN the Frontend Application SHALL display a password reset form
4. WHEN a user submits a new password THEN Firebase Authentication SHALL update the password
5. WHERE password reset succeeds THEN the CMMS Backend SHALL be notified to update any cached user data

### Requirement 10

**User Story:** Como desarrollador, quiero mantener logs de autenticación, para que pueda auditar intentos de acceso y diagnosticar problemas de seguridad.

#### Acceptance Criteria

1. WHEN a user logs in successfully THEN the CMMS Backend SHALL log the authentication event with timestamp, user ID, and IP address
2. WHEN authentication fails THEN the CMMS Backend SHALL log the failed attempt with reason and source IP
3. WHEN a token is validated THEN the Authentication Middleware SHALL log validation failures but not successful validations to reduce log volume
4. WHERE suspicious activity is detected THEN the CMMS Backend SHALL log detailed information for security analysis
5. WHEN logs are written THEN the CMMS Backend SHALL include correlation IDs to track requests across services
