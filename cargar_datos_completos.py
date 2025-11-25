"""
Script completo para cargar datos de demostración en el sistema CMMS
Incluye: usuarios, activos, órdenes de trabajo, inventario, planes de mantenimiento, etc.
"""
import requests
import json
from datetime import datetime, timedelta

# Backend URL
BACKEND_URL = "https://cmms-backend-888881509782.us-central1.run.app"

def login_admin():
    """Login como admin"""
    print("\n1. Iniciando sesión como administrador...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login/",
        json={
            "email": "admin@cmms.com",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access"]
        print("✓ Sesión iniciada correctamente")
        return token
    else:
        print(f"✗ Error en login: {response.status_code} - {response.text}")
        return None

def create_users(token):
    """Crear usuarios de prueba"""
    print("\n2. Creando usuarios...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Primero obtener roles disponibles
    roles_response = requests.get(
        f"{BACKEND_URL}/api/v1/auth/roles/",
        headers=headers
    )
    
    if roles_response.status_code != 200:
        print("  ✗ No se pudieron obtener los roles")
        return False
    
    roles_data = roles_response.json()
    if isinstance(roles_data, dict) and 'results' in roles_data:
        roles_data = roles_data['results']
    
    roles = {r['name']: r['id'] for r in roles_data}
    
    users = [
        {
            "email": "supervisor@somacor.com",
            "password": "Supervisor123!",
            "first_name": "Juan",
            "last_name": "Pérez",
            "rut": "12345678-9",
            "role": roles.get("SUPERVISOR"),
            "phone": "+56912345678",
            "employee_status": "ACTIVE"
        },
        {
            "email": "operador1@somacor.com",
            "password": "Operador123!",
            "first_name": "Pedro",
            "last_name": "González",
            "rut": "23456789-0",
            "role": roles.get("OPERADOR"),
            "phone": "+56923456789",
            "employee_status": "ACTIVE",
            "license_type": "MUNICIPAL",
            "license_expiration_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        },
        {
            "email": "operador2@somacor.com",
            "password": "Operador123!",
            "first_name": "María",
            "last_name": "Silva",
            "rut": "34567890-1",
            "role": roles.get("OPERADOR"),
            "phone": "+56934567890",
            "employee_status": "ACTIVE",
            "license_type": "PROFESIONAL",
            "license_expiration_date": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
        }
    ]
    
    created_count = 0
    existing_count = 0
    
    for user in users:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/users/",
            headers=headers,
            json=user
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✓ {user['first_name']} {user['last_name']}")
            created_count += 1
        elif response.status_code == 400:
            print(f"  - {user['first_name']} {user['last_name']} (ya existe o error)")
            existing_count += 1
        else:
            print(f"  ✗ Error en {user['email']}: {response.status_code} - {response.text[:100]}")
    
    print(f"Resumen: {created_count} creados, {existing_count} existentes")
    return created_count > 0 or existing_count > 0

def create_locations(token):
    """Crear ubicaciones"""
    print("\n3. Creando ubicaciones...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Primero obtener ubicaciones existentes
    response = requests.get(
        f"{BACKEND_URL}/api/v1/assets/locations/",
        headers=headers
    )
    
    existing_locations = []
    if response.status_code == 200:
        locs_data = response.json()
        if isinstance(locs_data, dict) and 'results' in locs_data:
            existing_locations = locs_data['results']
        elif isinstance(locs_data, list):
            existing_locations = locs_data
    
    existing_codes = {loc.get('code'): loc for loc in existing_locations if loc.get('code')}
    
    locations = [
        {
            "name": "Planta Principal",
            "code": "PP-01",
            "address": "Av. Industrial 1234, Santiago",
            "description": "Planta principal de operaciones"
        },
        {
            "name": "Bodega Central",
            "code": "BC-01",
            "address": "Calle Bodega 567, Santiago",
            "description": "Bodega central de repuestos"
        },
        {
            "name": "Taller Mecánico",
            "code": "TM-01",
            "address": "Av. Taller 890, Santiago",
            "description": "Taller de mantenimiento mecánico"
        }
    ]
    
    created_locations = []
    
    for location in locations:
        if location['code'] in existing_codes:
            print(f"  - {location['name']} (ya existe)")
            created_locations.append(existing_codes[location['code']])
            continue
            
        response = requests.post(
            f"{BACKEND_URL}/api/v1/assets/locations/",
            headers=headers,
            json=location
        )
        
        if response.status_code in [200, 201]:
            loc_data = response.json()
            created_locations.append(loc_data)
            print(f"  ✓ {location['name']}")
        else:
            print(f"  ✗ Error: {response.status_code}")
    
    return created_locations

def create_assets(token, locations):
    """Crear activos/vehículos"""
    print("\n4. Creando activos...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if not locations:
        print("  ✗ No hay ubicaciones disponibles")
        # Intentar obtener ubicaciones existentes
        response = requests.get(
            f"{BACKEND_URL}/api/v1/assets/locations/",
            headers=headers
        )
        if response.status_code == 200:
            locations = response.json()
            if isinstance(locations, dict) and 'results' in locations:
                locations = locations['results']
            if not locations:
                return []
        else:
            return []
    
    location_id = locations[0]['id']
    
    assets = [
        {
            "asset_code": "CAM-001",
            "name": "Camioneta Toyota Hilux",
            "vehicle_type": "CAMIONETA_MDO",
            "manufacturer": "Toyota",
            "model": "Hilux 4x4",
            "serial_number": "TOY2022001",
            "license_plate": "ABCD-12",
            "status": "OPERATIONAL",
            "location": location_id,
            "installation_date": "2022-01-15"
        },
        {
            "asset_code": "CSS-001",
            "name": "Camión Supersucker",
            "vehicle_type": "CAMION_SUPERSUCKER",
            "manufacturer": "Freightliner",
            "model": "M2 Supersucker",
            "serial_number": "FRE2021001",
            "license_plate": "EFGH-34",
            "status": "OPERATIONAL",
            "location": location_id,
            "installation_date": "2021-06-20"
        },
        {
            "asset_code": "RET-001",
            "name": "Retroexcavadora CAT 420F",
            "vehicle_type": "RETROEXCAVADORA_MDO",
            "manufacturer": "Caterpillar",
            "model": "420F",
            "serial_number": "CAT2020001",
            "license_plate": "IJKL-56",
            "status": "OPERATIONAL",
            "location": location_id,
            "installation_date": "2020-03-10"
        },
        {
            "asset_code": "CAR-001",
            "name": "Cargador Frontal CAT 950",
            "vehicle_type": "CARGADOR_FRONTAL_MDO",
            "manufacturer": "Caterpillar",
            "model": "950 GC",
            "serial_number": "CAT2021002",
            "license_plate": "MNOP-78",
            "status": "OPERATIONAL",
            "location": location_id,
            "installation_date": "2021-08-15"
        },
        {
            "asset_code": "MIN-001",
            "name": "Minicargador Bobcat S570",
            "vehicle_type": "MINICARGADOR_MDO",
            "manufacturer": "Bobcat",
            "model": "S570",
            "serial_number": "BOB2022001",
            "license_plate": "QRST-90",
            "status": "OPERATIONAL",
            "location": location_id,
            "installation_date": "2022-02-20"
        }
    ]
    
    # Primero obtener activos existentes
    response = requests.get(
        f"{BACKEND_URL}/api/v1/assets/",
        headers=headers
    )
    
    existing_assets = []
    if response.status_code == 200:
        assets_data = response.json()
        if isinstance(assets_data, dict) and 'results' in assets_data:
            existing_assets = assets_data['results']
        elif isinstance(assets_data, list):
            existing_assets = assets_data
    
    existing_codes = {a.get('asset_code'): a for a in existing_assets if a.get('asset_code')}
    created_assets = []
    
    for asset in assets:
        if asset['asset_code'] in existing_codes:
            print(f"  - {asset['name']} (ya existe)")
            created_assets.append(existing_codes[asset['asset_code']])
            continue
            
        response = requests.post(
            f"{BACKEND_URL}/api/v1/assets/",
            headers=headers,
            json=asset
        )
        
        if response.status_code in [200, 201]:
            asset_data = response.json()
            created_assets.append(asset_data)
            print(f"  ✓ {asset['name']}")
        else:
            print(f"  ✗ Error: {response.status_code} - {response.text[:100]}")
    
    return created_assets

def create_spare_parts(token):
    """Crear repuestos"""
    print("\n5. Creando repuestos...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    spare_parts = [
        {
            "code": "FIL-001",
            "name": "Filtro de Aceite",
            "description": "Filtro de aceite para motores diesel",
            "category": "FILTERS",
            "unit_of_measure": "UNIT",
            "minimum_stock": 10,
            "current_stock": 25,
            "unit_cost": 15000,
            "supplier": "Repuestos Chile S.A."
        },
        {
            "code": "FIL-002",
            "name": "Filtro de Aire",
            "description": "Filtro de aire para motores diesel",
            "category": "FILTERS",
            "unit_of_measure": "UNIT",
            "minimum_stock": 8,
            "current_stock": 20,
            "unit_cost": 25000,
            "supplier": "Repuestos Chile S.A."
        },
        {
            "code": "ACE-001",
            "name": "Aceite Motor 15W40",
            "description": "Aceite para motor diesel 15W40",
            "category": "LUBRICANTS",
            "unit_of_measure": "LITER",
            "minimum_stock": 50,
            "current_stock": 120,
            "unit_cost": 8000,
            "supplier": "Lubricantes del Sur"
        },
        {
            "code": "NEU-001",
            "name": "Neumático 275/70R18",
            "description": "Neumático para camioneta",
            "category": "TIRES",
            "unit_of_measure": "UNIT",
            "minimum_stock": 4,
            "current_stock": 12,
            "unit_cost": 180000,
            "supplier": "Neumáticos Express"
        },
        {
            "code": "BAT-001",
            "name": "Batería 12V 100Ah",
            "description": "Batería para vehículos pesados",
            "category": "ELECTRICAL",
            "unit_of_measure": "UNIT",
            "minimum_stock": 2,
            "current_stock": 6,
            "unit_cost": 120000,
            "supplier": "Baterías Power"
        }
    ]
    
    created_count = 0
    
    for part in spare_parts:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/inventory/spare-parts/",
            headers=headers,
            json=part
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✓ {part['name']}")
            created_count += 1
        elif response.status_code == 400:
            print(f"  - {part['name']} (ya existe)")
        else:
            print(f"  ✗ Error: {response.status_code}")
    
    return created_count > 0

def create_maintenance_plans(token, assets):
    """Crear planes de mantenimiento"""
    print("\n6. Creando planes de mantenimiento...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if not assets:
        print("  ✗ No hay activos disponibles")
        return False
    
    plans = []
    
    # Plan para cada activo
    for asset in assets[:3]:  # Solo los primeros 3 para no saturar
        if not asset.get('id'):
            continue
        plan = {
            "name": f"Mantenimiento Preventivo {asset['name']}",
            "description": f"Plan de mantenimiento preventivo para {asset['name']}",
            "plan_type": "PREVENTIVE",
            "asset": asset['id'],
            "frequency_type": "HOURS",
            "frequency_value": 250,
            "estimated_duration_hours": 4,
            "is_active": True
        }
        plans.append(plan)
    
    created_count = 0
    
    for plan in plans:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/maintenance/plans/",
            headers=headers,
            json=plan
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✓ {plan['name']}")
            created_count += 1
        elif response.status_code == 400:
            print(f"  - {plan['name']} (ya existe)")
        else:
            print(f"  ✗ Error: {response.status_code} - {response.text[:100]}")
    
    return created_count > 0

def create_work_orders(token, assets):
    """Crear órdenes de trabajo"""
    print("\n7. Creando órdenes de trabajo...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if not assets:
        print("  ✗ No hay activos disponibles")
        return False
    
    work_orders = []
    
    if assets and assets[0].get('id'):
        work_orders.append({
            "title": "Cambio de aceite y filtros",
            "description": "Mantenimiento preventivo: cambio de aceite motor y filtros",
            "work_order_type": "PREVENTIVE",
            "priority": "MEDIUM",
            "asset": assets[0]['id'],
            "scheduled_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "estimated_hours": 2
        })
    
    if len(assets) > 1 and assets[1].get('id'):
        work_orders.append({
            "title": "Revisión sistema hidráulico",
            "description": "Inspección y mantenimiento del sistema hidráulico",
            "work_order_type": "PREVENTIVE",
            "priority": "MEDIUM",
            "asset": assets[1]['id'],
            "scheduled_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "estimated_hours": 4
        })
    
    if len(assets) > 2 and assets[2].get('id'):
        work_orders.append({
            "title": "Reparación fuga de aceite",
            "description": "Reparación urgente de fuga en motor",
            "work_order_type": "CORRECTIVE",
            "priority": "HIGH",
            "asset": assets[2]['id'],
            "scheduled_date": datetime.now().strftime("%Y-%m-%d"),
            "estimated_hours": 6
        })
    
    created_count = 0
    
    for wo in work_orders:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/work-orders/",
            headers=headers,
            json=wo
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✓ {wo['title']}")
            created_count += 1
        elif response.status_code == 400:
            print(f"  - {wo['title']} (error)")
        else:
            print(f"  ✗ Error: {response.status_code} - {response.text[:100]}")
    
    return created_count > 0

def main():
    print("=" * 70)
    print("CARGA COMPLETA DE DATOS DE DEMOSTRACIÓN - CMMS SOMACOR")
    print("=" * 70)
    
    # Login
    token = login_admin()
    if not token:
        print("\n✗ No se pudo iniciar sesión")
        return
    
    # Crear datos
    create_users(token)
    locations = create_locations(token)
    assets = create_assets(token, locations)
    create_spare_parts(token)
    create_maintenance_plans(token, assets)
    create_work_orders(token, assets)
    
    print("\n" + "=" * 70)
    print("✓ CARGA DE DATOS COMPLETADA")
    print("=" * 70)
    print("\nDatos creados:")
    print("  • Usuarios: Admin, Supervisor, 2 Operadores")
    print("  • Ubicaciones: 3 ubicaciones")
    print("  • Activos: 5 vehículos/equipos")
    print("  • Repuestos: 5 items de inventario")
    print("  • Planes de mantenimiento: 3 planes")
    print("  • Órdenes de trabajo: 3 órdenes")
    print("  • Plantillas de checklist: 5 plantillas (ya creadas)")
    print("\nCredenciales de acceso:")
    print("  Admin: admin@cmms.com / admin123")
    print("  Supervisor: supervisor@somacor.com / Supervisor123!")
    print("  Operador 1: operador1@somacor.com / Operador123!")
    print("  Operador 2: operador2@somacor.com / Operador123!")
    print("\nAccede al sistema en:")
    print("  https://cmms-somacor-prod.web.app")
    print("=" * 70)

if __name__ == "__main__":
    main()
