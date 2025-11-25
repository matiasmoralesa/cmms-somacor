"""
Custom decorators for permission checking
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from apps.authentication.models import Role


def admin_required(view_func):
    """
    Decorator to require ADMIN role
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Autenticación requerida'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not request.user.is_admin():
            return Response(
                {'error': 'Solo los administradores pueden realizar esta acción'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_or_supervisor_required(view_func):
    """
    Decorator to require ADMIN or SUPERVISOR role
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Autenticación requerida'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not request.user.can_view_all_resources():
            return Response(
                {'error': 'Solo administradores y supervisores pueden realizar esta acción'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def valid_license_required(view_func):
    """
    Decorator to require valid license for OPERADOR
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Autenticación requerida'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Only check license for OPERADOR
        if request.user.is_operador():
            if not request.user.has_valid_license():
                return Response(
                    {
                        'error': 'Tu licencia está vencida',
                        'detail': 'No puedes realizar operaciones hasta renovar tu licencia',
                        'expiration_date': request.user.license_expiration_date.isoformat() if request.user.license_expiration_date else None
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def permission_required(permission_code):
    """
    Decorator to require specific permission
    Usage: @permission_required('view_all_assets')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Autenticación requerida'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not request.user.has_permission(permission_code):
                return Response(
                    {'error': f'No tienes el permiso requerido: {permission_code}'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def role_required(*roles):
    """
    Decorator to require specific role(s)
    Usage: @role_required(Role.ADMIN, Role.SUPERVISOR)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Autenticación requerida'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if request.user.role.name not in roles:
                return Response(
                    {'error': 'No tienes el rol requerido para esta acción'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def check_license_expiration(view_func):
    """
    Decorator to check if OPERADOR license is expiring soon and add warning
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        # Add license warning to response if applicable
        if request.user.is_authenticated and request.user.is_operador():
            if request.user.license_expires_soon():
                days = request.user.days_until_license_expiration()
                
                # Add warning header
                if hasattr(response, 'data'):
                    if isinstance(response.data, dict):
                        response.data['license_warning'] = {
                            'message': f'Tu licencia vence en {days} días',
                            'days_remaining': days,
                            'expiration_date': request.user.license_expiration_date.isoformat()
                        }
        
        return response
    
    return wrapper
