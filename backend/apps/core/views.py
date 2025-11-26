"""
Core views
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.db import transaction
from io import StringIO
import sys


@csrf_exempt
@require_http_methods(["POST", "GET"])
def run_migrations(request):
    """
    Endpoint to run database migrations
    Only accessible in production for initial setup
    """
    try:
        # Capture output
        out = StringIO()
        
        # Run migrations
        call_command('migrate', '--noinput', stdout=out, stderr=out)
        
        output = out.getvalue()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Migrations completed successfully',
            'output': output
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'error': str(sys.exc_info())
        }, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'cmms-backend'
    })


@require_http_methods(["GET"])
def check_user(request):
    """
    Check if a user exists and is active
    """
    try:
        from apps.authentication.models import User
        email = request.GET.get('email', 'admin@somacor.cl')
        
        try:
            user = User.objects.get(email=email)
            return JsonResponse({
                'exists': True,
                'email': user.email,
                'is_active': user.is_active,
                'has_password': user.password != '',
                'role': user.role.name if user.role else None,
                'firebase_uid': user.firebase_uid
            })
        except User.DoesNotExist:
            return JsonResponse({
                'exists': False,
                'email': email
            })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def sync_firebase_users(request):
    """
    Endpoint to sync Firebase users with Django database
    Creates users in Django that exist in Firebase
    """
    try:
        from apps.authentication.models import User, Role
        from datetime import datetime
        
        # Usuarios a sincronizar
        users_to_sync = [
            {
                'email': 'admin@somacor.cl',
                'password': 'Admin123!',
                'role': 'ADMIN',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'rut': '11111111-1',
                'firebase_uid': 'yD9roANaOITWAysyczjmBgMls5f1',
                'employee_status': 'ACTIVE'
            },
            {
                'email': 'supervisor@somacor.cl',
                'password': 'Super123!',
                'role': 'SUPERVISOR',
                'first_name': 'Supervisor',
                'last_name': 'Sistema',
                'rut': '22222222-2',
                'firebase_uid': 'WQisFpxLYGhpYzZS70H4qvDBUq32',
                'employee_status': 'ACTIVE'
            },
            {
                'email': 'operador@somacor.cl',
                'password': 'Opera123!',
                'role': 'OPERADOR',
                'first_name': 'Operador',
                'last_name': 'Sistema',
                'rut': '33333333-3',
                'firebase_uid': 'a0EA2lWbEwXEnItTOFDUvYwX9Tm2',
                'employee_status': 'ACTIVE',
                'license_type': 'MUNICIPAL',
                'license_expiration_date': '2026-12-31'
            }
        ]
        
        results = []
        
        with transaction.atomic():
            for user_data in users_to_sync:
                email = user_data['email']
                
                try:
                    # Obtener o crear rol
                    role, _ = Role.objects.get_or_create(
                        name=user_data['role'],
                        defaults={'description': f'Rol {user_data["role"]}'}
                    )
                    
                    # Preparar defaults
                    defaults = {
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'role': role,
                        'rut': user_data['rut'],
                        'firebase_uid': user_data['firebase_uid'],
                        'is_active': True,
                        'employee_status': user_data['employee_status']
                    }
                    
                    # Agregar campos de licencia si existen
                    if 'license_type' in user_data:
                        defaults['license_type'] = user_data['license_type']
                    if 'license_expiration_date' in user_data:
                        defaults['license_expiration_date'] = datetime.strptime(
                            user_data['license_expiration_date'], '%Y-%m-%d'
                        ).date()
                    
                    # Verificar si el usuario existe en Django (por email o RUT)
                    try:
                        django_user = User.objects.get(email=email)
                        created = False
                    except User.DoesNotExist:
                        try:
                            django_user = User.objects.get(rut=user_data['rut'])
                            created = False
                        except User.DoesNotExist:
                            # Crear nuevo usuario con contraseña
                            django_user = User.objects.create_user(
                                email=email,
                                password=user_data['password'],
                                **defaults
                            )
                            created = True
                    
                    if created:
                        results.append({
                            'email': email,
                            'status': 'created',
                            'id': str(django_user.id),
                            'role': django_user.role.name
                        })
                    else:
                        # Actualizar usuario existente
                        django_user.first_name = user_data['first_name']
                        django_user.last_name = user_data['last_name']
                        django_user.role = role
                        django_user.rut = user_data['rut']
                        django_user.firebase_uid = user_data['firebase_uid']
                        django_user.is_active = True
                        django_user.employee_status = user_data['employee_status']
                        
                        # Actualizar campos de licencia si existen
                        if 'license_type' in user_data:
                            django_user.license_type = user_data['license_type']
                        if 'license_expiration_date' in user_data:
                            django_user.license_expiration_date = datetime.strptime(
                                user_data['license_expiration_date'], '%Y-%m-%d'
                            ).date()
                        
                        django_user.set_password(user_data['password'])
                        django_user.save()
                        results.append({
                            'email': email,
                            'status': 'updated',
                            'id': str(django_user.id),
                            'role': django_user.role.name
                        })
                    
                except Exception as e:
                    results.append({
                        'email': email,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return JsonResponse({
            'status': 'success',
            'message': 'Users synced successfully',
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'error': str(sys.exc_info())
        }, status=500)
