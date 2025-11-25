"""
Custom permission classes for role-based access control
"""
from rest_framework import permissions
from apps.authentication.models import Role


class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if user is ADMIN
    """
    message = 'Solo los administradores pueden realizar esta acción'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin()
        )


class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Permission class to check if user is ADMIN or SUPERVISOR
    """
    message = 'Solo administradores y supervisores pueden realizar esta acción'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_all_resources()
        )


class IsOperador(permissions.BasePermission):
    """
    Permission class to check if user is OPERADOR
    """
    message = 'Solo los operadores pueden realizar esta acción'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_operador()
        )


class HasValidLicense(permissions.BasePermission):
    """
    Permission class to check if OPERADOR has valid license
    """
    message = 'Tu licencia está vencida. No puedes realizar operaciones hasta renovarla'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only check license for OPERADOR
        if request.user.is_operador():
            return request.user.has_valid_license()
        
        # Non-operadores don't need license
        return True


class CanViewAllResources(permissions.BasePermission):
    """
    Permission to view all resources (ADMIN or SUPERVISOR)
    """
    message = 'No tienes permisos para ver todos los recursos'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_all_resources()
        )


class CanManageUsers(permissions.BasePermission):
    """
    Permission to manage users (ADMIN only)
    """
    message = 'Solo los administradores pueden gestionar usuarios'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_manage_users()
        )


class CanCreateWorkOrders(permissions.BasePermission):
    """
    Permission to create work orders (ADMIN or SUPERVISOR)
    """
    message = 'No tienes permisos para crear órdenes de trabajo'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_create_work_orders()
        )


class CanCreateMaintenancePlans(permissions.BasePermission):
    """
    Permission to create maintenance plans (ADMIN or SUPERVISOR)
    """
    message = 'No tienes permisos para crear planes de mantenimiento'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_create_maintenance_plans()
        )


class IsOwnerOrAdminOrSupervisor(permissions.BasePermission):
    """
    Permission to check if user is owner of object or ADMIN/SUPERVISOR
    """
    message = 'No tienes permisos para acceder a este recurso'
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # ADMIN and SUPERVISOR can access all
        if request.user.can_view_all_resources():
            return True
        
        # Check if user is owner (works for objects with 'user' or 'assigned_to' field)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class HasPermission(permissions.BasePermission):
    """
    Generic permission class to check if user has specific permission code
    Usage: permission_classes = [HasPermission]
    Set permission_required attribute in view
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required permission from view
        permission_required = getattr(view, 'permission_required', None)
        
        if not permission_required:
            return True  # No specific permission required
        
        return request.user.has_permission(permission_required)


class ReadOnly(permissions.BasePermission):
    """
    Permission class for read-only access
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class: ADMIN can do anything, others read-only
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin()
        )


class CanAccessDashboard(permissions.BasePermission):
    """
    Permission to access dashboard (ADMIN or SUPERVISOR only)
    """
    message = 'No tienes acceso al dashboard'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_all_resources()
        )


class CanAccessCalendar(permissions.BasePermission):
    """
    Permission to access calendar (ADMIN or SUPERVISOR only)
    """
    message = 'No tienes acceso al calendario'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_all_resources()
        )


class CanViewReports(permissions.BasePermission):
    """
    Permission to view reports (ADMIN or SUPERVISOR only)
    """
    message = 'No tienes acceso a los reportes'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_all_resources()
        )


class CanManageInventory(permissions.BasePermission):
    """
    Permission to manage inventory (ADMIN or SUPERVISOR only)
    """
    message = 'No tienes permisos para gestionar el inventario'
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_all_resources()
        )
