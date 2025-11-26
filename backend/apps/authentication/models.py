"""
Authentication models for CMMS system.
Implements 3-tier role system: ADMIN, SUPERVISOR, OPERADOR
"""
import uuid
from datetime import date, timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    """
    User roles with specific permissions.
    Only 3 roles: ADMIN, SUPERVISOR, OPERADOR
    """
    ADMIN = 'ADMIN'
    SUPERVISOR = 'SUPERVISOR'
    OPERADOR = 'OPERADOR'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (SUPERVISOR, 'Supervisor'),
        (OPERADOR, 'Operador'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_name_display()


class Permission(models.Model):
    """
    Granular permissions for role-based access control
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=50)  # assets, work_orders, etc.
    
    roles = models.ManyToManyField(Role, related_name='permissions')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['module', 'code']
    
    def __str__(self):
        return f"{self.module}.{self.code}"


class User(AbstractUser):
    """
    Custom user model with role-based permissions and license management
    """
    # License types
    LICENSE_MUNICIPAL = 'MUNICIPAL'
    LICENSE_INTERNAL = 'INTERNAL'
    LICENSE_OTHER = 'OTHER'
    
    LICENSE_TYPE_CHOICES = [
        (LICENSE_MUNICIPAL, 'Licencia Municipal'),
        (LICENSE_INTERNAL, 'Licencia Interna'),
        (LICENSE_OTHER, 'Otra'),
    ]
    
    # Employee status
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_ON_LEAVE = 'ON_LEAVE'
    
    EMPLOYEE_STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Activo'),
        (STATUS_INACTIVE, 'Inactivo'),
        (STATUS_ON_LEAVE, 'Con Licencia'),
    ]
    
    # Override username to use email
    username = None
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name='Rol'
    )
    
    # Personal information
    rut = models.CharField(max_length=12, unique=True, verbose_name='RUT')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    employee_status = models.CharField(
        max_length=20,
        choices=EMPLOYEE_STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Estado de Empleado'
    )
    
    # License information (required for OPERADOR role)
    license_type = models.CharField(
        max_length=50,
        choices=LICENSE_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Tipo de Licencia'
    )
    license_expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento de Licencia'
    )
    license_photo_url = models.URLField(
        null=True,
        blank=True,
        verbose_name='URL de Foto de Licencia'
    )
    
    # Telegram integration
    telegram_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Telegram ID'
    )
    
    # Firebase integration
    firebase_uid = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Firebase UID',
        help_text='Unique identifier from Firebase Authentication',
        db_index=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'rut']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def clean(self):
        """Validate user data"""
        super().clean()
        
        # OPERADOR must have license information
        if self.role and self.role.name == Role.OPERADOR:
            if not self.license_type:
                raise ValidationError({
                    'license_type': 'Los operadores deben tener un tipo de licencia'
                })
            if not self.license_expiration_date:
                raise ValidationError({
                    'license_expiration_date': 'Los operadores deben tener fecha de vencimiento de licencia'
                })
            if not self.license_photo_url:
                raise ValidationError({
                    'license_photo_url': 'Los operadores deben tener foto de licencia'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    # License validation methods
    def has_valid_license(self):
        """Check if user has a valid, non-expired license"""
        if not self.license_type or not self.license_expiration_date:
            return False
        return self.license_expiration_date >= date.today()
    
    def license_expires_soon(self, days=30):
        """Check if license expires within specified days"""
        if not self.license_expiration_date:
            return False
        days_until_expiration = (self.license_expiration_date - date.today()).days
        return 0 <= days_until_expiration <= days
    
    def days_until_license_expiration(self):
        """Get number of days until license expires"""
        if not self.license_expiration_date:
            return None
        return (self.license_expiration_date - date.today()).days
    
    # Role checking methods
    def is_admin(self):
        """Check if user is ADMIN"""
        return self.role and self.role.name == Role.ADMIN
    
    def is_supervisor(self):
        """Check if user is SUPERVISOR"""
        return self.role and self.role.name == Role.SUPERVISOR
    
    def is_operador(self):
        """Check if user is OPERADOR"""
        return self.role and self.role.name == Role.OPERADOR
    
    # Permission checking methods
    def can_view_all_resources(self):
        """Check if user can view all resources (ADMIN or SUPERVISOR)"""
        return self.is_admin() or self.is_supervisor()
    
    def can_manage_users(self):
        """Check if user can manage other users (ADMIN only)"""
        return self.is_admin()
    
    def can_create_work_orders(self):
        """Check if user can create work orders (ADMIN or SUPERVISOR)"""
        return self.can_view_all_resources()
    
    def can_create_maintenance_plans(self):
        """Check if user can create maintenance plans (ADMIN or SUPERVISOR)"""
        return self.can_view_all_resources()
    
    def can_view_predictions(self):
        """Check if user can view ML predictions (ADMIN or SUPERVISOR)"""
        return self.can_view_all_resources()
    
    def can_view_reports(self):
        """Check if user can view reports (ADMIN or SUPERVISOR)"""
        return self.can_view_all_resources()
    
    def can_manage_inventory(self):
        """Check if user can manage inventory (ADMIN or SUPERVISOR)"""
        return self.can_view_all_resources()
    
    def has_permission(self, permission_code):
        """Check if user has specific permission"""
        if not self.role:
            return False
        return self.role.permissions.filter(code=permission_code).exists()
