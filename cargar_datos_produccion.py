"""
Script para cargar datos de demostración en producción usando la API
"""
import requests
import json

# Backend URL
BACKEND_URL = "https://cmms-backend-888881509782.us-central1.run.app"

def create_admin_user():
    """Crear usuario administrador"""
    print("\n1. Creando usuario administrador...")
    
    # Intentar crear usuario admin usando el endpoint de setup con la clave secreta
    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/setup/create-admin/",
        json={
            "secret_key": "CMMS2025Setup"
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        print("✓ Usuario admin creado exitosamente")
        print(f"  Email: {data.get('email', 'admin@cmms.com')}")
        print(f"  Password: admin123")
        return True, "admin@cmms.com", "admin123"
    elif response.status_code == 400:
        # Ya existe un admin
        print("- Usuario admin ya existe")
        return True, "admin@cmms.com", "admin123"
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
        return False, None, None

def login_admin(email, password):
    """Login como admin"""
    print("\n2. Iniciando sesión...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login/",
        json={
            "email": email,
            "password": password
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access"]
        print("✓ Sesión iniciada correctamente")
        return token
    else:
        print(f"✗ Error en login: {response.status_code} - {response.text}")
        return None

def create_checklist_templates(token):
    """Crear plantillas de checklist"""
    print("\n3. Creando plantillas de checklist...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    templates = [
        {
            "code": "F-PR-020-CH01",
            "name": "Check List Camionetas MDO",
            "vehicle_type": "CAMIONETA",
            "description": "Checklist diario para camionetas de mantenimiento",
            "items": [
                {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Motor", "order": 2, "question": "Nivel de refrigerante", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Frenos", "order": 3, "question": "Nivel de líquido de frenos", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Neumáticos", "order": 4, "question": "Presión de neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Seguridad", "order": 5, "question": "Luces funcionando", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Seguridad", "order": 6, "question": "Cinturones de seguridad", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
            ],
            "is_system_template": True,
            "passing_score": 80
        },
        {
            "code": "CH-SUPERSUCKER-01",
            "name": "Check List Camión Supersucker",
            "vehicle_type": "CAMION",
            "description": "Checklist para camión supersucker",
            "items": [
                {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Motor", "order": 2, "question": "Nivel de refrigerante", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Sistema Hidráulico", "order": 3, "question": "Nivel de aceite hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Sistema Hidráulico", "order": 4, "question": "Fugas en mangueras", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Sistema de Vacío", "order": 5, "question": "Presión del sistema", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Neumáticos", "order": 6, "question": "Presión de neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
            ],
            "is_system_template": True,
            "passing_score": 80
        },
        {
            "code": "F-PR-034-CH01",
            "name": "Check Retroexcavadora MDO",
            "vehicle_type": "RETROEXCAVADORA",
            "description": "Checklist para retroexcavadora",
            "items": [
                {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Hidráulico", "order": 2, "question": "Nivel de aceite hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Hidráulico", "order": 3, "question": "Estado de cilindros", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Estructura", "order": 4, "question": "Estado de brazos y cucharón", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Neumáticos", "order": 5, "question": "Estado de neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
            ],
            "is_system_template": True,
            "passing_score": 80
        },
        {
            "code": "F-PR-037-CH01",
            "name": "Check List Cargador Frontal MDO",
            "vehicle_type": "CARGADOR_FRONTAL",
            "description": "Checklist para cargador frontal",
            "items": [
                {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Transmisión", "order": 2, "question": "Nivel de aceite transmisión", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Hidráulico", "order": 3, "question": "Sistema hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Neumáticos", "order": 4, "question": "Estado de neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
            ],
            "is_system_template": True,
            "passing_score": 80
        },
        {
            "code": "F-PR-040-CH01",
            "name": "Check List Minicargador MDO",
            "vehicle_type": "MINICARGADOR",
            "description": "Checklist para minicargador",
            "items": [
                {"section": "Motor", "order": 1, "question": "Nivel de aceite", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Hidráulico", "order": 2, "question": "Sistema hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
                {"section": "Orugas/Neumáticos", "order": 3, "question": "Estado de orugas/neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
            ],
            "is_system_template": True,
            "passing_score": 80
        }
    ]
    
    created_count = 0
    existing_count = 0
    error_count = 0
    
    for template in templates:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/checklists/templates/",
            headers=headers,
            json=template
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✓ {template['name']}")
            created_count += 1
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print(f"  - {template['name']} (ya existe)")
            existing_count += 1
        else:
            print(f"  ✗ Error en {template['name']}: {response.status_code}")
            error_count += 1
    
    print(f"\nResumen: {created_count} creadas, {existing_count} existentes, {error_count} errores")
    return created_count > 0 or existing_count > 0

def main():
    print("=" * 60)
    print("CARGA DE DATOS DE DEMOSTRACIÓN - CMMS SOMACOR")
    print("=" * 60)
    
    # Usar credenciales existentes
    email = "admin@cmms.com"
    password = "admin123"
    
    print("\n1. Usando usuario admin existente...")
    print(f"  Email: {email}")
    
    # Paso 2: Login
    token = login_admin(email, password)
    if not token:
        print("\n✗ No se pudo iniciar sesión")
        return
    
    # Paso 3: Crear plantillas
    if not create_checklist_templates(token):
        print("\n✗ No se pudieron crear las plantillas")
        return
    
    print("\n" + "=" * 60)
    print("✓ DATOS CARGADOS EXITOSAMENTE")
    print("=" * 60)
    print("\nCredenciales de acceso:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print("\nAccede al sistema en:")
    print("  https://cmms-somacor-prod.web.app")
    print("=" * 60)

if __name__ == "__main__":
    main()
