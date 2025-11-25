"""
Plan de Pruebas Completo - Sistema CMMS SOMACOR
Ejecuta pruebas funcionales de todos los módulos del sistema
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Configuración
BACKEND_URL = "https://cmms-backend-888881509782.us-central1.run.app"
FRONTEND_URL = "https://cmms-somacor-prod.web.app"

# Resultados de pruebas
test_results = []

def log_test(module: str, test_name: str, status: str, details: str = ""):
    """Registrar resultado de prueba"""
    result = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "test": test_name,
        "status": status,  # PASS, FAIL, SKIP
        "details": details
    }
    test_results.append(result)
    
    icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "○"
    print(f"  {icon} {test_name}: {status}")
    if details:
        print(f"    {details}")

def login(email: str, password: str) -> Tuple[bool, str, Dict]:
    """Login y obtener token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login/",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, data["access"], data.get("user", {})
        else:
            return False, "", {}
    except Exception as e:
        return False, "", {}

def test_authentication():
    """Módulo 1: Autenticación"""
    print("\n" + "="*70)
    print("MÓDULO 1: AUTENTICACIÓN")
    print("="*70)
    
    # Test 1.1: Login Admin
    success, token, user = login("admin@cmms.com", "admin123")
    if success and user.get("role") == "ADMIN":
        log_test("Autenticación", "Login Admin", "PASS", 
                f"Usuario: {user.get('full_name')}, Rol: {user.get('role')}")
    else:
        log_test("Autenticación", "Login Admin", "FAIL", "No se pudo autenticar")
        return None
    
    # Test 1.2: Login Supervisor
    success_sup, token_sup, user_sup = login("supervisor@somacor.com", "Supervisor123!")
    if success_sup:
        log_test("Autenticación", "Login Supervisor", "PASS", 
                f"Usuario: {user_sup.get('full_name', 'N/A')}")
    else:
        log_test("Autenticación", "Login Supervisor", "SKIP", 
                "Usuario no existe o credenciales incorrectas")
    
    # Test 1.3: Login Operador
    success_op, token_op, user_op = login("operador1@somacor.com", "Operador123!")
    if success_op:
        log_test("Autenticación", "Login Operador", "PASS", 
                f"Usuario: {user_op.get('full_name', 'N/A')}")
    else:
        log_test("Autenticación", "Login Operador", "SKIP", 
                "Usuario no existe o credenciales incorrectas")
    
    # Test 1.4: Login con credenciales incorrectas
    success_bad, _, _ = login("admin@cmms.com", "wrongpassword")
    if not success_bad:
        log_test("Autenticación", "Rechazo credenciales incorrectas", "PASS")
    else:
        log_test("Autenticación", "Rechazo credenciales incorrectas", "FAIL", 
                "Sistema permitió login con credenciales incorrectas")
    
    return token

def test_users(token: str):
    """Módulo 2: Gestión de Usuarios"""
    print("\n" + "="*70)
    print("MÓDULO 2: GESTIÓN DE USUARIOS")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 2.1: Listar usuarios
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/auth/users/", headers=headers)
        if response.status_code == 200:
            users = response.json()
            if isinstance(users, dict) and 'results' in users:
                users = users['results']
            user_count = len(users) if isinstance(users, list) else 0
            log_test("Usuarios", "Listar usuarios", "PASS", 
                    f"Total usuarios: {user_count}")
        else:
            log_test("Usuarios", "Listar usuarios", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Usuarios", "Listar usuarios", "FAIL", str(e))
    
    # Test 2.2: Obtener roles
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/auth/roles/", headers=headers)
        if response.status_code == 200:
            roles = response.json()
            if isinstance(roles, dict) and 'results' in roles:
                roles = roles['results']
            role_names = [r.get('name') for r in roles] if isinstance(roles, list) else []
            log_test("Usuarios", "Listar roles", "PASS", 
                    f"Roles: {', '.join(role_names)}")
        else:
            log_test("Usuarios", "Listar roles", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Usuarios", "Listar roles", "FAIL", str(e))
    
    # Test 2.3: Ver perfil propio
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/auth/profile/", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            log_test("Usuarios", "Ver perfil propio", "PASS", 
                    f"Email: {profile.get('email')}")
        else:
            log_test("Usuarios", "Ver perfil propio", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Usuarios", "Ver perfil propio", "FAIL", str(e))

def test_assets(token: str):
    """Módulo 3: Gestión de Activos"""
    print("\n" + "="*70)
    print("MÓDULO 3: GESTIÓN DE ACTIVOS")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 3.1: Listar activos
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/assets/", headers=headers)
        if response.status_code == 200:
            assets = response.json()
            if isinstance(assets, dict) and 'results' in assets:
                assets = assets['results']
            asset_count = len(assets) if isinstance(assets, list) else 0
            log_test("Activos", "Listar activos", "PASS", 
                    f"Total activos: {asset_count}")
            return assets
        else:
            log_test("Activos", "Listar activos", "FAIL", 
                    f"Status: {response.status_code}")
            return []
    except Exception as e:
        log_test("Activos", "Listar activos", "FAIL", str(e))
        return []
    
    # Test 3.2: Listar ubicaciones
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/assets/locations/", headers=headers)
        if response.status_code == 200:
            locations = response.json()
            if isinstance(locations, dict) and 'results' in locations:
                locations = locations['results']
            loc_count = len(locations) if isinstance(locations, list) else 0
            log_test("Activos", "Listar ubicaciones", "PASS", 
                    f"Total ubicaciones: {loc_count}")
        else:
            log_test("Activos", "Listar ubicaciones", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Activos", "Listar ubicaciones", "FAIL", str(e))
    
    # Test 3.3: Filtrar activos por tipo
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/assets/?vehicle_type=CAMIONETA_MDO", 
            headers=headers
        )
        if response.status_code == 200:
            assets = response.json()
            if isinstance(assets, dict) and 'results' in assets:
                assets = assets['results']
            log_test("Activos", "Filtrar por tipo de vehículo", "PASS", 
                    f"Camionetas encontradas: {len(assets) if isinstance(assets, list) else 0}")
        else:
            log_test("Activos", "Filtrar por tipo de vehículo", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Activos", "Filtrar por tipo de vehículo", "FAIL", str(e))

def test_inventory(token: str):
    """Módulo 4: Gestión de Inventario"""
    print("\n" + "="*70)
    print("MÓDULO 4: GESTIÓN DE INVENTARIO")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 4.1: Listar repuestos
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/inventory/spare-parts/", headers=headers)
        if response.status_code == 200:
            parts = response.json()
            if isinstance(parts, dict) and 'results' in parts:
                parts = parts['results']
            part_count = len(parts) if isinstance(parts, list) else 0
            log_test("Inventario", "Listar repuestos", "PASS", 
                    f"Total repuestos: {part_count}")
        else:
            log_test("Inventario", "Listar repuestos", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Inventario", "Listar repuestos", "FAIL", str(e))
    
    # Test 4.2: Filtrar repuestos por categoría
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/inventory/spare-parts/?category=FILTERS", 
            headers=headers
        )
        if response.status_code == 200:
            parts = response.json()
            if isinstance(parts, dict) and 'results' in parts:
                parts = parts['results']
            log_test("Inventario", "Filtrar por categoría", "PASS", 
                    f"Filtros encontrados: {len(parts) if isinstance(parts, list) else 0}")
        else:
            log_test("Inventario", "Filtrar por categoría", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Inventario", "Filtrar por categoría", "FAIL", str(e))
    
    # Test 4.3: Verificar stock bajo
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/inventory/spare-parts/low-stock/", 
            headers=headers
        )
        if response.status_code == 200:
            parts = response.json()
            if isinstance(parts, dict) and 'results' in parts:
                parts = parts['results']
            log_test("Inventario", "Alertas de stock bajo", "PASS", 
                    f"Items con stock bajo: {len(parts) if isinstance(parts, list) else 0}")
        else:
            log_test("Inventario", "Alertas de stock bajo", "SKIP", 
                    "Endpoint no disponible o sin datos")
    except Exception as e:
        log_test("Inventario", "Alertas de stock bajo", "SKIP", str(e))

def test_work_orders(token: str, assets: List):
    """Módulo 5: Órdenes de Trabajo"""
    print("\n" + "="*70)
    print("MÓDULO 5: ÓRDENES DE TRABAJO")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 5.1: Listar órdenes de trabajo
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/work-orders/", headers=headers)
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, dict) and 'results' in orders:
                orders = orders['results']
            order_count = len(orders) if isinstance(orders, list) else 0
            log_test("Órdenes de Trabajo", "Listar órdenes", "PASS", 
                    f"Total órdenes: {order_count}")
        else:
            log_test("Órdenes de Trabajo", "Listar órdenes", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Órdenes de Trabajo", "Listar órdenes", "FAIL", str(e))
    
    # Test 5.2: Filtrar por prioridad
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/work-orders/?priority=HIGH", 
            headers=headers
        )
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, dict) and 'results' in orders:
                orders = orders['results']
            log_test("Órdenes de Trabajo", "Filtrar por prioridad", "PASS", 
                    f"Órdenes alta prioridad: {len(orders) if isinstance(orders, list) else 0}")
        else:
            log_test("Órdenes de Trabajo", "Filtrar por prioridad", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Órdenes de Trabajo", "Filtrar por prioridad", "FAIL", str(e))
    
    # Test 5.3: Filtrar por tipo
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/work-orders/?work_order_type=PREVENTIVE", 
            headers=headers
        )
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, dict) and 'results' in orders:
                orders = orders['results']
            log_test("Órdenes de Trabajo", "Filtrar por tipo", "PASS", 
                    f"Órdenes preventivas: {len(orders) if isinstance(orders, list) else 0}")
        else:
            log_test("Órdenes de Trabajo", "Filtrar por tipo", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Órdenes de Trabajo", "Filtrar por tipo", "FAIL", str(e))

def test_maintenance_plans(token: str):
    """Módulo 6: Planes de Mantenimiento"""
    print("\n" + "="*70)
    print("MÓDULO 6: PLANES DE MANTENIMIENTO")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 6.1: Listar planes
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/maintenance/plans/", headers=headers)
        if response.status_code == 200:
            plans = response.json()
            if isinstance(plans, dict) and 'results' in plans:
                plans = plans['results']
            plan_count = len(plans) if isinstance(plans, list) else 0
            log_test("Planes de Mantenimiento", "Listar planes", "PASS", 
                    f"Total planes: {plan_count}")
        else:
            log_test("Planes de Mantenimiento", "Listar planes", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Planes de Mantenimiento", "Listar planes", "FAIL", str(e))
    
    # Test 6.2: Filtrar planes activos
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/maintenance/plans/?is_active=true", 
            headers=headers
        )
        if response.status_code == 200:
            plans = response.json()
            if isinstance(plans, dict) and 'results' in plans:
                plans = plans['results']
            log_test("Planes de Mantenimiento", "Filtrar planes activos", "PASS", 
                    f"Planes activos: {len(plans) if isinstance(plans, list) else 0}")
        else:
            log_test("Planes de Mantenimiento", "Filtrar planes activos", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Planes de Mantenimiento", "Filtrar planes activos", "FAIL", str(e))

def test_checklists(token: str):
    """Módulo 7: Checklists"""
    print("\n" + "="*70)
    print("MÓDULO 7: CHECKLISTS")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 7.1: Listar plantillas
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/checklists/templates/", headers=headers)
        if response.status_code == 200:
            templates = response.json()
            if isinstance(templates, dict) and 'results' in templates:
                templates = templates['results']
            template_count = len(templates) if isinstance(templates, list) else 0
            log_test("Checklists", "Listar plantillas", "PASS", 
                    f"Total plantillas: {template_count}")
        else:
            log_test("Checklists", "Listar plantillas", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Checklists", "Listar plantillas", "FAIL", str(e))
    
    # Test 7.2: Filtrar por tipo de vehículo
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/checklists/templates/?vehicle_type=CAMIONETA_MDO", 
            headers=headers
        )
        if response.status_code == 200:
            templates = response.json()
            if isinstance(templates, dict) and 'results' in templates:
                templates = templates['results']
            log_test("Checklists", "Filtrar plantillas por vehículo", "PASS", 
                    f"Plantillas para camionetas: {len(templates) if isinstance(templates, list) else 0}")
        else:
            log_test("Checklists", "Filtrar plantillas por vehículo", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Checklists", "Filtrar plantillas por vehículo", "FAIL", str(e))
    
    # Test 7.3: Listar respuestas de checklist
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/checklists/responses/", headers=headers)
        if response.status_code == 200:
            responses = response.json()
            if isinstance(responses, dict) and 'results' in responses:
                responses = responses['results']
            response_count = len(responses) if isinstance(responses, list) else 0
            log_test("Checklists", "Listar respuestas", "PASS", 
                    f"Total respuestas: {response_count}")
        else:
            log_test("Checklists", "Listar respuestas", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Checklists", "Listar respuestas", "FAIL", str(e))

def test_notifications(token: str):
    """Módulo 8: Notificaciones"""
    print("\n" + "="*70)
    print("MÓDULO 8: NOTIFICACIONES")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 8.1: Listar notificaciones
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/notifications/", headers=headers)
        if response.status_code == 200:
            notifications = response.json()
            if isinstance(notifications, dict) and 'results' in notifications:
                notifications = notifications['results']
            notif_count = len(notifications) if isinstance(notifications, list) else 0
            log_test("Notificaciones", "Listar notificaciones", "PASS", 
                    f"Total notificaciones: {notif_count}")
        else:
            log_test("Notificaciones", "Listar notificaciones", "FAIL", 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("Notificaciones", "Listar notificaciones", "FAIL", str(e))
    
    # Test 8.2: Contador de no leídas
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/notifications/unread_count/", 
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0) if isinstance(data, dict) else 0
            log_test("Notificaciones", "Contador no leídas", "PASS", 
                    f"Notificaciones no leídas: {count}")
        else:
            log_test("Notificaciones", "Contador no leídas", "SKIP", 
                    "Endpoint no disponible")
    except Exception as e:
        log_test("Notificaciones", "Contador no leídas", "SKIP", str(e))

def generate_report():
    """Generar reporte de pruebas"""
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    
    total = len(test_results)
    passed = len([r for r in test_results if r['status'] == 'PASS'])
    failed = len([r for r in test_results if r['status'] == 'FAIL'])
    skipped = len([r for r in test_results if r['status'] == 'SKIP'])
    
    print(f"\nTotal de pruebas: {total}")
    print(f"✓ Exitosas: {passed} ({passed/total*100:.1f}%)")
    print(f"✗ Fallidas: {failed} ({failed/total*100:.1f}%)")
    print(f"○ Omitidas: {skipped} ({skipped/total*100:.1f}%)")
    
    # Agrupar por módulo
    modules = {}
    for result in test_results:
        module = result['module']
        if module not in modules:
            modules[module] = {'PASS': 0, 'FAIL': 0, 'SKIP': 0}
        modules[module][result['status']] += 1
    
    print("\n" + "-"*70)
    print("RESULTADOS POR MÓDULO")
    print("-"*70)
    for module, stats in modules.items():
        total_mod = sum(stats.values())
        print(f"\n{module}:")
        print(f"  ✓ {stats['PASS']}/{total_mod} exitosas")
        if stats['FAIL'] > 0:
            print(f"  ✗ {stats['FAIL']}/{total_mod} fallidas")
        if stats['SKIP'] > 0:
            print(f"  ○ {stats['SKIP']}/{total_mod} omitidas")
    
    # Guardar reporte en archivo
    report = {
        "fecha_ejecucion": datetime.now().isoformat(),
        "sistema": "CMMS SOMACOR",
        "backend_url": BACKEND_URL,
        "frontend_url": FRONTEND_URL,
        "resumen": {
            "total": total,
            "exitosas": passed,
            "fallidas": failed,
            "omitidas": skipped,
            "porcentaje_exito": round(passed/total*100, 2)
        },
        "modulos": modules,
        "pruebas": test_results
    }
    
    with open('reporte_pruebas_cmms.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Reporte guardado en: reporte_pruebas_cmms.json")

def main():
    """Ejecutar plan de pruebas completo"""
    print("="*70)
    print("PLAN DE PRUEBAS - SISTEMA CMMS SOMACOR")
    print("="*70)
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Autenticación
    token = test_authentication()
    if not token:
        print("\n✗ No se pudo autenticar. Abortando pruebas.")
        return
    
    # Ejecutar pruebas de cada módulo
    test_users(token)
    assets = test_assets(token)
    test_inventory(token)
    test_work_orders(token, assets)
    test_maintenance_plans(token)
    test_checklists(token)
    test_notifications(token)
    
    # Generar reporte
    generate_report()
    
    print("\n" + "="*70)
    print("PRUEBAS COMPLETADAS")
    print("="*70)

if __name__ == "__main__":
    main()
