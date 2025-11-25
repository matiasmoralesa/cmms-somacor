"""Admin configuration for authentication models"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Role, Permission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'permission_count', 'user_count', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = []
    readonly_fields = ['created_at', 'updated_at']
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permisos'
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Usuarios'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'module', 'role_list', 'created_at']
    list_filter = ['module', 'roles']
    search_fields = ['code', 'name', 'description']
    filter_horizontal = ['roles']
    readonly_fields = ['created_at']
    
    def role_list(self, obj):
        return ', '.join([role.get_name_display() for role in obj.roles.all()])
    role_list.short_description = 'Roles'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email',
        'full_name',
        'rut',
        'role',
        'employee_status',
        'license_status',
        'is_active',
        'created_at'
    ]
    list_filter = ['role', 'employee_status', 'is_active', 'license_type']
    search_fields = ['email', 'first_name', 'last_name', 'rut']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('email', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'rut', 'phone')
        }),
        ('Rol y Permisos', {
            'fields': ('role', 'employee_status', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Información de Licencia', {
            'fields': ('license_type', 'license_expiration_date', 'license_photo_url'),
            'description': 'Requerido para usuarios con rol OPERADOR'
        }),
        ('Integración Telegram', {
            'fields': ('telegram_id',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Información de Acceso', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'rut', 'phone')
        }),
        ('Rol', {
            'fields': ('role', 'employee_status')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Nombre Completo'
    
    def license_status(self, obj):
        """Display license status with color coding"""
        if obj.role.name != Role.OPERADOR:
            return format_html('<span style="color: gray;">N/A</span>')
        
        if not obj.has_valid_license():
            return format_html('<span style="color: red; font-weight: bold;">❌ Vencida</span>')
        
        if obj.license_expires_soon():
            days = obj.days_until_license_expiration()
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠️ Vence en {} días</span>',
                days
            )
        
        return format_html('<span style="color: green;">✅ Vigente</span>')
    
    license_status.short_description = 'Estado de Licencia'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('role')
