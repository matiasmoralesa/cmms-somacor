"""
Authentication views and endpoints
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import User, Role, Permission
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    RoleSerializer,
    PermissionSerializer
)
from .schema_examples import (
    LOGIN_REQUEST_EXAMPLE,
    LOGIN_RESPONSE_EXAMPLE,
    USER_PROFILE_EXAMPLE,
    PASSWORD_CHANGE_REQUEST_EXAMPLE,
    PASSWORD_CHANGE_RESPONSE_EXAMPLE,
    VALIDATION_ERROR_EXAMPLE,
    AUTHENTICATION_ERROR_EXAMPLE,
)


@extend_schema(
    tags=['Autenticación'],
    summary='Iniciar sesión',
    description='Autentica un usuario y devuelve tokens JWT (access y refresh) junto con información del usuario',
    examples=[LOGIN_REQUEST_EXAMPLE, LOGIN_RESPONSE_EXAMPLE, AUTHENTICATION_ERROR_EXAMPLE],
    responses={
        200: CustomTokenObtainPairSerializer,
        400: OpenApiResponse(description='Credenciales inválidas'),
        401: OpenApiResponse(description='No autorizado'),
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login endpoint that returns JWT tokens with user info
    POST /api/v1/auth/login
    """
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['Autenticación'],
    summary='Cerrar sesión',
    description='Invalida el refresh token del usuario para cerrar la sesión',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh_token': {'type': 'string', 'description': 'Token de refresco a invalidar'}
            },
            'required': ['refresh_token']
        }
    },
    responses={
        200: OpenApiResponse(description='Sesión cerrada exitosamente'),
        400: OpenApiResponse(description='Token inválido o faltante'),
    }
)
class LogoutView(APIView):
    """
    Logout endpoint - blacklists the refresh token
    POST /api/v1/auth/logout
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Sesión cerrada exitosamente'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Token inválido o ya expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        tags=['Autenticación'],
        summary='Obtener perfil del usuario',
        description='Obtiene la información del perfil del usuario autenticado',
        examples=[USER_PROFILE_EXAMPLE],
        responses={200: UserProfileSerializer}
    ),
    put=extend_schema(
        tags=['Autenticación'],
        summary='Actualizar perfil del usuario',
        description='Actualiza la información del perfil del usuario autenticado',
        responses={200: UserProfileSerializer, 400: OpenApiResponse(description='Datos inválidos')}
    ),
    patch=extend_schema(
        tags=['Autenticación'],
        summary='Actualizar parcialmente perfil del usuario',
        description='Actualiza parcialmente la información del perfil del usuario autenticado',
        responses={200: UserProfileSerializer, 400: OpenApiResponse(description='Datos inválidos')}
    )
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile
    GET/PUT /api/v1/auth/profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@extend_schema(
    tags=['Autenticación'],
    summary='Cambiar contraseña',
    description='Permite al usuario autenticado cambiar su contraseña',
    request=PasswordChangeSerializer,
    examples=[PASSWORD_CHANGE_REQUEST_EXAMPLE, PASSWORD_CHANGE_RESPONSE_EXAMPLE, VALIDATION_ERROR_EXAMPLE],
    responses={
        200: OpenApiResponse(description='Contraseña cambiada exitosamente'),
        400: OpenApiResponse(description='Datos inválidos o contraseña actual incorrecta'),
    }
)
class PasswordChangeView(APIView):
    """
    Change password for authenticated user
    POST /api/v1/auth/password-change
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Contraseña cambiada exitosamente'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Request password reset - sends email with reset link
    POST /api/v1/auth/password-reset
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email, is_active=True)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link (you'll need to configure your frontend URL)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
            
            # Send email (configure email backend in settings)
            try:
                send_mail(
                    subject='Restablecer Contraseña - CMMS',
                    message=f'Hola {user.get_full_name()},\n\n'
                            f'Has solicitado restablecer tu contraseña.\n'
                            f'Haz clic en el siguiente enlace:\n\n'
                            f'{reset_link}\n\n'
                            f'Este enlace expira en 24 horas.\n\n'
                            f'Si no solicitaste este cambio, ignora este mensaje.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return Response(
                    {'message': 'Se ha enviado un email con instrucciones para restablecer tu contraseña'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': 'Error al enviar el email. Intenta nuevamente.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token
    POST /api/v1/auth/password-reset-confirm
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                uid = request.data.get('uid')
                token = serializer.validated_data['token']
                new_password = serializer.validated_data['new_password']
                
                # Decode user ID
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
                
                # Verify token
                if not default_token_generator.check_token(user, token):
                    return Response(
                        {'error': 'Token inválido o expirado'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Set new password
                user.set_password(new_password)
                user.save()
                
                return Response(
                    {'message': 'Contraseña restablecida exitosamente'},
                    status=status.HTTP_200_OK
                )
                
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {'error': 'Token inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create new user (ADMIN only)
    GET/POST /api/v1/auth/users
    """
    queryset = User.objects.all().select_related('role')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter users based on role"""
        user = self.request.user
        
        # Only ADMIN can see all users
        if not user.can_manage_users():
            return User.objects.filter(id=user.id)
        
        return User.objects.all().select_related('role')
    
    def perform_create(self, serializer):
        """Only ADMIN can create users"""
        if not self.request.user.can_manage_users():
            raise permissions.PermissionDenied('No tienes permisos para crear usuarios')
        serializer.save()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete user (ADMIN only)
    GET/PUT/DELETE /api/v1/auth/users/{id}
    """
    queryset = User.objects.all().select_related('role')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on role"""
        user = self.request.user
        
        # Only ADMIN can manage other users
        if not user.can_manage_users():
            return User.objects.filter(id=user.id)
        
        return User.objects.all().select_related('role')
    
    def perform_update(self, serializer):
        """Only ADMIN can update other users"""
        if not self.request.user.can_manage_users():
            if self.get_object().id != self.request.user.id:
                raise permissions.PermissionDenied('No tienes permisos para editar este usuario')
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete - set is_active to False"""
        if not self.request.user.can_manage_users():
            raise permissions.PermissionDenied('No tienes permisos para eliminar usuarios')
        
        instance.is_active = False
        instance.save()


class RoleListView(generics.ListAPIView):
    """
    List all roles
    GET /api/v1/auth/roles
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class PermissionListView(generics.ListAPIView):
    """
    List all permissions
    GET /api/v1/auth/permissions
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by module if provided"""
        queryset = Permission.objects.all()
        module = self.request.query_params.get('module', None)
        
        if module:
            queryset = queryset.filter(module=module)
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_license_status(request):
    """
    Check license status for current user
    GET /api/v1/auth/check-license
    """
    user = request.user
    
    if user.role.name != Role.OPERADOR:
        return Response({
            'applicable': False,
            'message': 'La validación de licencia solo aplica para operadores'
        })
    
    return Response({
        'applicable': True,
        'valid': user.has_valid_license(),
        'expires_soon': user.license_expires_soon(),
        'days_until_expiration': user.days_until_license_expiration(),
        'expiration_date': user.license_expiration_date.isoformat() if user.license_expiration_date else None,
        'license_type': user.get_license_type_display() if user.license_type else None,
        'can_operate': user.has_valid_license()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def users_with_expiring_licenses(request):
    """
    Get list of users with licenses expiring soon (ADMIN/SUPERVISOR only)
    GET /api/v1/auth/expiring-licenses
    """
    user = request.user
    
    if not user.can_view_all_resources():
        return Response(
            {'error': 'No tienes permisos para ver esta información'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get OPERADOR users with expiring licenses
    from datetime import date, timedelta
    
    thirty_days_from_now = date.today() + timedelta(days=30)
    
    expiring_users = User.objects.filter(
        role__name=Role.OPERADOR,
        is_active=True,
        license_expiration_date__lte=thirty_days_from_now,
        license_expiration_date__gte=date.today()
    ).select_related('role')
    
    expired_users = User.objects.filter(
        role__name=Role.OPERADOR,
        is_active=True,
        license_expiration_date__lt=date.today()
    ).select_related('role')
    
    return Response({
        'expiring_soon': UserSerializer(expiring_users, many=True).data,
        'expired': UserSerializer(expired_users, many=True).data,
        'total_expiring': expiring_users.count(),
        'total_expired': expired_users.count()
    })



# Setup endpoint - Solo para inicialización
@extend_schema(
    tags=['Setup'],
    summary='Crear usuario admin inicial',
    description='Crea el primer usuario administrador. Solo funciona si no existe ningún admin.',
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_initial_admin(request):
    """
    Crea el usuario admin inicial
    NOTA: Este endpoint debe ser deshabilitado en producción después del primer uso
    """
    # Solo permitir en DEBUG o con una clave secreta
    secret_key = request.data.get('secret_key')
    
    if not settings.DEBUG and secret_key != 'CMMS2025Setup':
        return Response(
            {'error': 'No autorizado'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verificar si ya existe un admin
    if User.objects.filter(role=Role.ADMIN).exists():
        return Response(
            {'message': 'Ya existe un usuario administrador'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Crear admin
    try:
        admin = User.objects.create_superuser(
            email='admin@cmms.com',
            password='admin123',
            first_name='Admin',
            last_name='Sistema',
            role=Role.ADMIN
        )
        
        return Response({
            'message': 'Usuario administrador creado exitosamente',
            'email': admin.email,
            'credentials': {
                'email': 'admin@cmms.com',
                'password': 'admin123'
            },
            'warning': 'Por favor, cambia la contraseña inmediatamente'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



# User Management Views (ADMIN only)
from rest_framework import viewsets, filters
from rest_framework.decorators import action as viewset_action
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsAdmin
from .serializers import UserListSerializer, UserManagementSerializer, UserPasswordResetSerializer


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management by ADMIN.
    Provides CRUD operations and additional actions for user management.
    """
    queryset = User.objects.all().select_related('role')
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'employee_status', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'rut']
    ordering_fields = ['email', 'created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'reset_password':
            return UserPasswordResetSerializer
        return UserManagementSerializer
    
    def perform_destroy(self, instance):
        """Soft delete - set is_active to False instead of deleting"""
        instance.is_active = False
        instance.save()
    
    @extend_schema(
        tags=['Gestión de Usuarios'],
        summary='Activar usuario',
        description='Activa un usuario desactivado',
        responses={200: OpenApiResponse(description='Usuario activado exitosamente')}
    )
    @viewset_action(detail=True, methods=['patch'])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'message': f'Usuario {user.get_full_name()} activado exitosamente',
            'user': UserManagementSerializer(user).data
        })
    
    @extend_schema(
        tags=['Gestión de Usuarios'],
        summary='Desactivar usuario',
        description='Desactiva un usuario activo',
        responses={200: OpenApiResponse(description='Usuario desactivado exitosamente')}
    )
    @viewset_action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        user = self.get_object()
        
        # Prevent deactivating yourself
        if user.id == request.user.id:
            return Response(
                {'error': 'No puedes desactivar tu propia cuenta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        
        return Response({
            'message': f'Usuario {user.get_full_name()} desactivado exitosamente',
            'user': UserManagementSerializer(user).data
        })
    
    @extend_schema(
        tags=['Gestión de Usuarios'],
        summary='Restablecer contraseña de usuario',
        description='Permite al ADMIN restablecer la contraseña de cualquier usuario',
        request=UserPasswordResetSerializer,
        responses={
            200: OpenApiResponse(description='Contraseña restablecida exitosamente'),
            400: OpenApiResponse(description='Datos inválidos')
        }
    )
    @viewset_action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset user password (ADMIN only)"""
        user = self.get_object()
        serializer = UserPasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            send_email = serializer.validated_data.get('send_email', True)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Send email notification if requested
            if send_email:
                try:
                    send_mail(
                        subject='Contraseña Restablecida - CMMS',
                        message=f'Hola {user.get_full_name()},\n\n'
                                f'Tu contraseña ha sido restablecida por un administrador.\n'
                                f'Tu nueva contraseña temporal es: {new_password}\n\n'
                                f'Por favor, cambia tu contraseña al iniciar sesión.\n\n'
                                f'Saludos,\nEquipo CMMS',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Error sending email: {e}")
            
            return Response({
                'message': f'Contraseña restablecida exitosamente para {user.get_full_name()}',
                'email_sent': send_email
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=['Gestión de Usuarios'],
        summary='Crear nuevo usuario',
        description='Crea un nuevo usuario y envía email con credenciales',
        request=UserManagementSerializer,
        responses={
            201: UserManagementSerializer,
            400: OpenApiResponse(description='Datos inválidos')
        }
    )
    def create(self, request, *args, **kwargs):
        """Create new user with temporary password"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate temporary password
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Create user
        user = User.objects.create_user(
            password=temp_password,
            **serializer.validated_data
        )
        
        # Send welcome email with credentials
        try:
            send_mail(
                subject='Bienvenido a CMMS',
                message=f'Hola {user.get_full_name()},\n\n'
                        f'Se ha creado una cuenta para ti en el sistema CMMS.\n\n'
                        f'Tus credenciales de acceso son:\n'
                        f'Email: {user.email}\n'
                        f'Contraseña temporal: {temp_password}\n\n'
                        f'Por favor, cambia tu contraseña al iniciar sesión por primera vez.\n\n'
                        f'Puedes acceder al sistema en: {settings.FRONTEND_URL}\n\n'
                        f'Saludos,\nEquipo CMMS',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            email_sent = True
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            email_sent = False
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'user': UserManagementSerializer(user).data,
            'temporary_password': temp_password,
            'email_sent': email_sent,
            'message': 'Usuario creado exitosamente'
        }, status=status.HTTP_201_CREATED, headers=headers)
