"""
Script para crear usuario administrador en producción
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Configurar variables de entorno para producción
os.environ['DB_NAME'] = 'cmms_prod'
os.environ['DB_USER'] = 'cmms_user'
os.environ['DB_PASSWORD'] = 'CmmsSecure2024!'
os.environ['DB_HOST'] = '/cloudsql/argon-edge-478500-i8:us-central1:cmms-db'

django.setup()

from apps.authentication.models import User, Role

def create_admin_user():
    """Crear usuario administrador"""
    
    # Crear o obtener rol ADMIN
    admin_role, created = Role.objects.get_or_create(
        name=Role.ADMIN,
        defaults={
            'description': 'Administrador del sistema con acceso completo'
        }
    )
    
    if created:
        print(f"✓ Rol ADMIN creado")
    else:
        print(f"- Rol ADMIN ya existe")
    
    # Verificar si ya existe el usuario admin
    if User.objects.filter(email='admin@cmms.com').exists():
        print("- Usuario admin@cmms.com ya existe")
        user = User.objects.get(email='admin@cmms.com')
        print(f"  Email: {user.email}")
        print(f"  Nombre: {user.get_full_name()}")
        print(f"  Rol: {user.role.name}")
        return user
    
    # Crear usuario administrador
    try:
        admin_user = User.objects.create_user(
            email='admin@cmms.com',
            password='admin123',
            first_name='Admin',
            last_name='Sistema',
            rut='11111111-1',
            role=admin_role,
            is_staff=True,
            is_superuser=True
        )
        
        print(f"✓ Usuario administrador creado exitosamente")
        print(f"  Email: admin@cmms.com")
        print(f"  Password: admin123")
        print(f"  Rol: ADMIN")
        
        return admin_user
        
    except Exception as e:
        print(f"✗ Error creando usuario: {e}")
        return None

def create_test_users():
    """Crear usuarios de prueba"""
    
    # Crear roles
    supervisor_role, _ = Role.objects.get_or_create(
        name=Role.SUPERVISOR,
        defaults={'description': 'Supervisor de mantenimiento'}
    )
    
    operador_role, _ = Role.objects.get_or_create(
        name=Role.OPERADOR,
        defaults={'description': 'Operador de equipos'}
    )
    
    # Crear supervisor
    if not User.objects.filter(email='supervisor@cmms.com').exists():
        User.objects.create_user(
            email='supervisor@cmms.com',
            password='supervisor123',
            first_name='Juan',
            last_name='Supervisor',
            rut='22222222-2',
            role=supervisor_role
        )
        print("✓ Usuario supervisor@cmms.com creado")
    
    # Crear operador
    if not User.objects.filter(email='operador@cmms.com').exists():
        from datetime import date, timedelta
        User.objects.create_user(
            email='operador@cmms.com',
            password='operador123',
            first_name='Pedro',
            last_name='Operador',
            rut='33333333-3',
            role=operador_role,
            license_type='MUNICIPAL',
            license_expiration_date=date.today() + timedelta(days=365),
            license_photo_url='https://example.com/license.jpg'
        )
        print("✓ Usuario operador@cmms.com creado")

if __name__ == '__main__':
    print("Creando usuarios en base de datos de producción...\n")
    
    try:
        create_admin_user()
        create_test_users()
        
        print("\n✓ Proceso completado")
        print("\nUsuarios disponibles:")
        print("  - admin@cmms.com / admin123 (ADMIN)")
        print("  - supervisor@cmms.com / supervisor123 (SUPERVISOR)")
        print("  - operador@cmms.com / operador123 (OPERADOR)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
