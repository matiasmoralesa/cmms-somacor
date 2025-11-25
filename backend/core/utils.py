"""
Utility functions for permission checking and role management
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from apps.authentication.models import Role


def check_user_permission(user, permission_code):
    """
    Check if user has specific permission
    
    Args:
        user: User instance
        permission_code: Permission code string
    
    Returns:
        bool: True if user has permission
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.has_permission(permission_code)


def check_user_role(user, *roles):
    """
    Check if user has one of the specified roles
    
    Args:
        user: User instance
        *roles: Role names to check
    
    Returns:
        bool: True if user has one of the roles
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.role.name in roles


def get_user_permissions(user):
    """
    Get list of all permissions for user
    
    Args:
        user: User instance
    
    Returns:
        list: List of permission codes
    """
    if not user or not user.is_authenticated:
        return []
    
    return list(user.role.permissions.values_list('code', flat=True))


def can_user_access_resource(user, resource):
    """
    Check if user can access a specific resource
    
    Args:
        user: User instance
        resource: Resource object (WorkOrder, Asset, etc.)
    
    Returns:
        bool: True if user can access resource
    """
    if not user or not user.is_authenticated:
        return False
    
    # ADMIN and SUPERVISOR can access all resources
    if user.can_view_all_resources():
        return True
    
    # OPERADOR can only access assigned resources
    if hasattr(resource, 'assigned_to'):
        return resource.assigned_to == user
    
    if hasattr(resource, 'user'):
        return resource.user == user
    
    if hasattr(resource, 'created_by'):
        return resource.created_by == user
    
    return False


def filter_queryset_by_role(queryset, user, assigned_field='assigned_to'):
    """
    Filter queryset based on user role
    
    Args:
        queryset: Django queryset
        user: User instance
        assigned_field: Field name for assignment (default: 'assigned_to')
    
    Returns:
        Filtered queryset
    """
    if not user or not user.is_authenticated:
        return queryset.none()
    
    # ADMIN and SUPERVISOR see all
    if user.can_view_all_resources():
        return queryset
    
    # OPERADOR sees only assigned
    filter_kwargs = {assigned_field: user}
    return queryset.filter(**filter_kwargs)


def get_role_display_name(role_name):
    """
    Get display name for role
    
    Args:
        role_name: Role name constant
    
    Returns:
        str: Display name
    """
    role_map = {
        Role.ADMIN: 'Administrador',
        Role.SUPERVISOR: 'Supervisor',
        Role.OPERADOR: 'Operador'
    }
    return role_map.get(role_name, role_name)


def validate_license_for_operation(user):
    """
    Validate that OPERADOR has valid license for operations
    
    Args:
        user: User instance
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not user or not user.is_authenticated:
        return False, 'Usuario no autenticado'
    
    # Only check for OPERADOR
    if not user.is_operador():
        return True, None
    
    if not user.has_valid_license():
        return False, 'Tu licencia está vencida. No puedes realizar operaciones.'
    
    if user.license_expires_soon(days=7):
        days = user.days_until_license_expiration()
        return True, f'Advertencia: Tu licencia vence en {days} días'
    
    return True, None


def get_accessible_assets(user):
    """
    Get assets accessible to user based on role
    
    Args:
        user: User instance
    
    Returns:
        QuerySet: Accessible assets
    """
    from apps.assets.models import Asset
    
    if not user or not user.is_authenticated:
        return Asset.objects.none()
    
    # ADMIN and SUPERVISOR see all
    if user.can_view_all_resources():
        return Asset.objects.all()
    
    # OPERADOR sees only assigned assets (through work orders)
    from apps.work_orders.models import WorkOrder
    assigned_asset_ids = WorkOrder.objects.filter(
        assigned_to=user
    ).values_list('asset_id', flat=True).distinct()
    
    return Asset.objects.filter(id__in=assigned_asset_ids)


def get_accessible_work_orders(user):
    """
    Get work orders accessible to user based on role
    
    Args:
        user: User instance
    
    Returns:
        QuerySet: Accessible work orders
    """
    from apps.work_orders.models import WorkOrder
    
    if not user or not user.is_authenticated:
        return WorkOrder.objects.none()
    
    # ADMIN and SUPERVISOR see all
    if user.can_view_all_resources():
        return WorkOrder.objects.all()
    
    # OPERADOR sees only assigned
    return WorkOrder.objects.filter(assigned_to=user)


def log_permission_check(user, permission_code, granted):
    """
    Log permission check for audit
    
    Args:
        user: User instance
        permission_code: Permission code checked
        granted: Whether permission was granted
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(
        f"Permission check: user={user.email if user else 'Anonymous'}, "
        f"permission={permission_code}, granted={granted}"
    )


class PermissionChecker:
    """
    Helper class for checking multiple permissions
    """
    
    def __init__(self, user):
        self.user = user
        self._permissions_cache = None
    
    @property
    def permissions(self):
        """Cached permissions list"""
        if self._permissions_cache is None:
            self._permissions_cache = get_user_permissions(self.user)
        return self._permissions_cache
    
    def has(self, permission_code):
        """Check if user has permission"""
        return permission_code in self.permissions
    
    def has_any(self, *permission_codes):
        """Check if user has any of the permissions"""
        return any(code in self.permissions for code in permission_codes)
    
    def has_all(self, *permission_codes):
        """Check if user has all of the permissions"""
        return all(code in self.permissions for code in permission_codes)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.user.is_admin()
    
    def is_supervisor(self):
        """Check if user is supervisor"""
        return self.user.is_supervisor()
    
    def is_operador(self):
        """Check if user is operador"""
        return self.user.is_operador()
    
    def can_view_all(self):
        """Check if user can view all resources"""
        return self.user.can_view_all_resources()
