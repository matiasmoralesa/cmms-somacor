"""
OpenAPI Schema Examples for Authentication Endpoints
"""
from drf_spectacular.utils import OpenApiExample

# Login Examples
LOGIN_REQUEST_EXAMPLE = OpenApiExample(
    'Login Request',
    value={
        'email': 'admin@cmms.com',
        'password': 'SecurePassword123!'
    },
    request_only=True,
)

LOGIN_RESPONSE_EXAMPLE = OpenApiExample(
    'Login Response',
    value={
        'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
        'user': {
            'id': '123e4567-e89b-12d3-a456-426614174000',
            'email': 'admin@cmms.com',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'role': 'ADMIN',
            'role_name': 'Administrador'
        }
    },
    response_only=True,
    status_codes=['200'],
)

# User Profile Examples
USER_PROFILE_EXAMPLE = OpenApiExample(
    'User Profile',
    value={
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'operador@cmms.com',
        'first_name': 'Carlos',
        'last_name': 'González',
        'full_name': 'Carlos González',
        'rut': '12345678-9',
        'phone': '+56912345678',
        'role': '456e7890-e89b-12d3-a456-426614174000',
        'role_name': 'Operador',
        'employee_status': 'ACTIVE',
        'license_type': 'MUNICIPAL',
        'license_expiration_date': '2025-12-31',
        'license_photo_url': 'https://storage.googleapis.com/bucket/licenses/photo.jpg',
        'license_status': 'valid',
        'days_until_license_expiration': 365,
        'telegram_id': '123456789',
        'is_active': True,
        'created_at': '2024-01-15T10:30:00Z',
        'updated_at': '2024-11-13T14:20:00Z'
    },
    response_only=True,
)

# Password Change Examples
PASSWORD_CHANGE_REQUEST_EXAMPLE = OpenApiExample(
    'Password Change Request',
    value={
        'old_password': 'OldPassword123!',
        'new_password': 'NewSecurePassword456!',
        'confirm_password': 'NewSecurePassword456!'
    },
    request_only=True,
)

PASSWORD_CHANGE_RESPONSE_EXAMPLE = OpenApiExample(
    'Password Change Response',
    value={
        'message': 'Contraseña cambiada exitosamente'
    },
    response_only=True,
    status_codes=['200'],
)

# Password Reset Request Examples
PASSWORD_RESET_REQUEST_EXAMPLE = OpenApiExample(
    'Password Reset Request',
    value={
        'email': 'usuario@cmms.com'
    },
    request_only=True,
)

PASSWORD_RESET_RESPONSE_EXAMPLE = OpenApiExample(
    'Password Reset Response',
    value={
        'message': 'Se ha enviado un correo con instrucciones para restablecer tu contraseña'
    },
    response_only=True,
    status_codes=['200'],
)

# Error Examples
VALIDATION_ERROR_EXAMPLE = OpenApiExample(
    'Validation Error',
    value={
        'email': ['Este campo es requerido'],
        'password': ['La contraseña debe tener al menos 8 caracteres']
    },
    response_only=True,
    status_codes=['400'],
)

AUTHENTICATION_ERROR_EXAMPLE = OpenApiExample(
    'Authentication Error',
    value={
        'detail': 'Credenciales inválidas'
    },
    response_only=True,
    status_codes=['401'],
)

PERMISSION_ERROR_EXAMPLE = OpenApiExample(
    'Permission Error',
    value={
        'detail': 'No tienes permisos para realizar esta acción'
    },
    response_only=True,
    status_codes=['403'],
)
