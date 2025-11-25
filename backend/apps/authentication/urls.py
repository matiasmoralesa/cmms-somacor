"""Authentication URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

# Router for user management
router = DefaultRouter()
router.register(r'users-management', views.UserManagementViewSet, basename='user_management')

urlpatterns = [
    # Setup (temporal - solo para inicialización)
    path('setup/create-admin/', views.create_initial_admin, name='create_admin'),
    
    # Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    
    # Users management (admin only)
    path('users/', views.UserListCreateView.as_view(), name='user_list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Roles and permissions
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('permissions/', views.PermissionListView.as_view(), name='permission_list'),
    
    # License checks
    path('check-license/', views.check_license_status, name='check_license'),
    path('expiring-licenses/', views.users_with_expiring_licenses, name='expiring_licenses'),
    
    # User management router
    path('', include(router.urls)),
]
