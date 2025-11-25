"""
Serializers for authentication endpoints
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Role, Permission


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    display_name = serializers.CharField(source='get_name_display', read_only=True)
    permission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'permission_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_permission_count(self, obj):
        return obj.permissions.count()


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model"""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'description', 'module']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    license_status = serializers.SerializerMethodField()
    days_until_license_expiration = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'rut', 'phone', 'role', 'role_name', 'employee_status',
            'license_type', 'license_expiration_date', 'license_photo_url',
            'license_status', 'days_until_license_expiration',
            'telegram_id', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'license_photo_url': {'required': False}
        }
    
    def get_license_status(self, obj):
        """Get license status"""
        if obj.role.name != Role.OPERADOR:
            return 'N/A'
        
        if not obj.has_valid_license():
            return 'expired'
        
        if obj.license_expires_soon():
            return 'expiring_soon'
        
        return 'valid'
    
    def get_days_until_license_expiration(self, obj):
        """Get days until license expires"""
        return obj.days_until_license_expiration()
    
    def validate(self, attrs):
        """Validate user data"""
        # Check if OPERADOR has license info
        role = attrs.get('role')
        if role and role.name == Role.OPERADOR:
            if not attrs.get('license_type'):
                raise serializers.ValidationError({
                    'license_type': 'Los operadores deben tener un tipo de licencia'
                })
            if not attrs.get('license_expiration_date'):
                raise serializers.ValidationError({
                    'license_expiration_date': 'Los operadores deben tener fecha de vencimiento'
                })
        
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'rut', 'phone', 'role', 'employee_status',
            'license_type', 'license_expiration_date', 'license_photo_url'
        ]
    
    def validate(self, attrs):
        """Validate passwords match and license info for OPERADOR"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden'
            })
        
        # Check if OPERADOR has license info
        role = attrs.get('role')
        if role and role.name == Role.OPERADOR:
            if not attrs.get('license_type'):
                raise serializers.ValidationError({
                    'license_type': 'Los operadores deben tener un tipo de licencia'
                })
            if not attrs.get('license_expiration_date'):
                raise serializers.ValidationError({
                    'license_expiration_date': 'Los operadores deben tener fecha de vencimiento'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user info"""
    
    def validate(self, attrs):
        """Validate and return token with user data"""
        data = super().validate(attrs)
        
        # Add user information to token response
        user = self.user
        data['user'] = {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': user.role.name if user.role else None,
            'role_display': user.role.get_name_display() if user.role else 'Sin rol',
            'is_admin': user.is_admin(),
            'is_supervisor': user.is_supervisor(),
            'is_operador': user.is_operador(),
            'employee_status': user.employee_status,
        }
        
        # Add license info for OPERADOR
        if user.is_operador():
            data['user']['license_status'] = {
                'valid': user.has_valid_license(),
                'expires_soon': user.license_expires_soon(),
                'days_until_expiration': user.days_until_license_expiration(),
                'expiration_date': user.license_expiration_date.isoformat() if user.license_expiration_date else None
            }
        
        # Add permissions
        if user.role:
            data['user']['permissions'] = list(
                user.role.permissions.values_list('code', flat=True)
            )
        else:
            data['user']['permissions'] = []
        
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate passwords"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden'
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Contraseña actual incorrecta')
        return value
    
    def save(self):
        """Change password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists"""
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError('No existe un usuario activo con este email')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden'
            })
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (current user)"""
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    permissions = serializers.SerializerMethodField()
    license_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'rut', 'phone', 'role', 'role_name', 'employee_status',
            'license_type', 'license_expiration_date', 'license_photo_url',
            'license_status', 'telegram_id', 'permissions',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at']
    
    def get_permissions(self, obj):
        """Get user permissions"""
        return list(obj.role.permissions.values_list('code', flat=True))
    
    def get_license_status(self, obj):
        """Get detailed license status"""
        if obj.role.name != Role.OPERADOR:
            return None
        
        return {
            'valid': obj.has_valid_license(),
            'expires_soon': obj.license_expires_soon(),
            'days_until_expiration': obj.days_until_license_expiration(),
            'expiration_date': obj.license_expiration_date.isoformat() if obj.license_expiration_date else None,
            'type': obj.get_license_type_display() if obj.license_type else None
        }



class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for user lists"""
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'role_name',
            'employee_status', 'is_active', 'created_at'
        ]


class UserManagementSerializer(serializers.ModelSerializer):
    """Serializer for user management by ADMIN"""
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    license_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'rut', 'phone', 'role', 'role_name', 'employee_status',
            'license_type', 'license_expiration_date', 'license_photo_url',
            'license_status', 'telegram_id', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_license_status(self, obj):
        """Get license status"""
        if obj.role.name != Role.OPERADOR:
            return 'N/A'
        
        if not obj.has_valid_license():
            return 'expired'
        
        if obj.license_expires_soon():
            return 'expiring_soon'
        
        return 'valid'
    
    def validate_email(self, value):
        """Validate that email is unique"""
        instance = self.instance
        if User.objects.filter(email=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value
    
    def validate_rut(self, value):
        """Validate that RUT is unique"""
        instance = self.instance
        if User.objects.filter(rut=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe un usuario con este RUT.")
        return value
    
    def validate(self, attrs):
        """Validate user data"""
        # Check if OPERADOR has license info
        role = attrs.get('role', self.instance.role if self.instance else None)
        if role and role.name == Role.OPERADOR:
            if not attrs.get('license_type') and (not self.instance or not self.instance.license_type):
                raise serializers.ValidationError({
                    'license_type': 'Los operadores deben tener un tipo de licencia'
                })
            if not attrs.get('license_expiration_date') and (not self.instance or not self.instance.license_expiration_date):
                raise serializers.ValidationError({
                    'license_expiration_date': 'Los operadores deben tener fecha de vencimiento'
                })
        
        return attrs


class UserPasswordResetSerializer(serializers.Serializer):
    """Serializer for admin to reset user password"""
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    send_email = serializers.BooleanField(default=True)
    
    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden'
            })
        return attrs
