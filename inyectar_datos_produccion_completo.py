#!/usr/bin/env python3
"""
Script para inyectar datos completos en producción
Incluye: Usuarios, Activos, Órdenes de Trabajo, Checklists, Inventario, Predicciones
"""

import requests
import json
from datetime import datetime, timedelta
import random

# Configuración
BASE_URL = "https://cmms-backend-888881509782.us-central1.run.app"
API_URL = f"{BASE_URL}/api/v1"

# Credenciales de admin
ADMIN_EMAIL = "admin@cmms.com"
ADMIN_PASSWORD = "admin123"

def get_auth_token():
    """Obtener token de autenticación"""
    print("🔐 Obteniendo token de autenticación...")
    response = requests.post(
        f"{API_URL}/auth/login/",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()['access']
        print("✅ Token obtenido exitosamente")
        return token
    else:
        print(f"❌ Error al obtener token: {response.status_code}")
        print(response.text)
        return None

def create_headers(token):
    """Crear headers con autenticación"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def create_assets(token):
    """Crear activos de prueba"""
    print("\n🚛 Creando activos...")
    headers = create_headers(token)
    
    assets = [
        {
            "name": "Camión Supersucker SS-001",
            "asset_code": "SS-001",
            "vehicle_type": "CAMION_SUPERSUCKER",
            "manufacturer": "Volvo",
            "model": "FMX 500",
            "serial_number": "VLV2023SS001",
            "license_plate": "HJKL-12",
            "status": "OPERATIONAL",
            "criticality": "CRITICAL",
            "specifications": {
                "year": 2023,
                "engine": "D13K500",
                "capacity": "15000L"
            }
        },
        {
            "name": "Camioneta MDO CM-001",
            "asset_code": "CM-001",
            "vehicle_type": "CAMIONETA_MDO",
            "manufacturer": "Toyota",
            "model": "Hilux 4x4",
            "serial_number": "TOY2023CM001",
            "license_plate": "ABCD-34",
            "status": "OPERATIONAL",
            "criticality": "HIGH",
            "specifications": {
                "year": 2023,
                "engine": "2.8L Diesel",
                "transmission": "Automatic"
            }
        },
        {
            "name": "Retroexcavadora RE-001",
            "asset_code": "RE-001",
            "vehicle_type": "RETROEXCAVADORA_MDO",
            "manufacturer": "Caterpillar",
            "model": "420F2",
            "serial_number": "CAT2022RE001",
            "license_plate": "WXYZ-56",
            "status": "OPERATIONAL",
            "criticality": "HIGH",
            "specifications": {
                "year": 2022,
                "bucket_capacity": "1.0m3",
                "operating_weight": "8500kg"
            }
        },
        {
            "name": "Cargador Frontal CF-001",
            "asset_code": "CF-001",
            "vehicle_type": "CARGADOR_FRONTAL_MDO",
            "manufacturer": "Komatsu",
            "model": "WA320-8",
            "serial_number": "KOM2023CF001",
            "license_plate": "PQRS-78",
            "status": "OPERATIONAL",
            "criticality": "CRITICAL",
            "specifications": {
                "year": 2023,
                "bucket_capacity": "2.3m3",
                "operating_weight": "12000kg"
            }
        },
        {
            "name": "Minicargador MC-001",
            "asset_code": "MC-001",
            "vehicle_type": "MINICARGADOR_MDO",
            "manufacturer": "Bobcat",
            "model": "S650",
            "serial_number": "BOB2023MC001",
            "license_plate": "MNOP-90",
            "status": "OPERATIONAL",
            "criticality": "MEDIUM",
            "specifications": {
                "year": 2023,
                "operating_capacity": "1134kg",
                "engine": "Kubota V2607"
            }
        },
        {
            "name": "Camioneta MDO CM-002",
            "asset_code": "CM-002",
            "vehicle_type": "CAMIONETA_MDO",
            "manufacturer": "Ford",
            "model": "Ranger XLT",
            "serial_number": "FOR2022CM002",
            "license_plate": "EFGH-23",
            "status": "MAINTENANCE",
            "criticality": "MEDIUM",
            "specifications": {
                "year": 2022,
                "engine": "2.0L Bi-Turbo",
                "transmission": "Automatic"
            }
        }
    ]
    
    created_assets = []
    for asset_data in assets:
        try:
            response = requests.post(
                f"{API_URL}/assets/",
                headers=headers,
                json=asset_data
            )
            if response.status_code in [200, 201]:
                asset = response.json()
                created_assets.append(asset)
                print(f"  ✅ Activo creado: {asset_data['name']}")
            else:
                print(f"  ⚠️  Error creando {asset_data['name']}: {response.status_code}")
                print(f"     {response.text}")
        except Exception as e:
            print(f"  ❌ Error creando activo {asset_data['name']}: {e}")
    
    return created_assets

def create_work_orders(token, assets):
    """Crear órdenes de trabajo"""
    print("\n📋 Creando órdenes de trabajo...")
    headers = create_headers(token)
    
    if not assets:
        print("  ⚠️  No hay activos disponibles")
        return []
    
    work_orders = []
    statuses = ["PENDING", "IN_PROGRESS", "COMPLETED"]
    priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"]
    types = ["CORRECTIVE", "PREVENTIVE", "PREDICTIVE"]
    
    for i, asset in enumerate(assets[:5]):  # Crear 5 órdenes
        wo_data = {
            "title": f"Mantenimiento {types[i % 3]} - {asset['name']}",
            "description": f"Orden de trabajo para {asset['name']}. Revisión programada según plan de mantenimiento.",
            "asset": asset['id'],
            "work_order_type": types[i % 3],
            "priority": priorities[i % 4],
            "status": statuses[i % 3],
            "scheduled_date": (datetime.now() + timedelta(days=i)).isoformat(),
            "estimated_hours": random.randint(2, 8)
        }
        
        try:
            response = requests.post(
                f"{API_URL}/work-orders/",
                headers=headers,
                json=wo_data
            )
            if response.status_code in [200, 201]:
                wo = response.json()
                work_orders.append(wo)
                print(f"  ✅ Orden creada: {wo_data['title']}")
            else:
                print(f"  ⚠️  Error creando orden: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return work_orders

def create_spare_parts(token):
    """Crear repuestos"""
    print("\n🔧 Creando repuestos...")
    headers = create_headers(token)
    
    spare_parts = [
        {
            "part_number": "FLT-001",
            "name": "Filtro de Aceite",
            "description": "Filtro de aceite para motor diesel",
            "category": "FILTROS",
            "quantity": 25,
            "minimum_stock": 10,
            "unit_cost": 15000,
            "location": "Bodega A - Estante 1",
            "supplier": "Repuestos Industriales S.A."
        },
        {
            "part_number": "FLT-002",
            "name": "Filtro de Aire",
            "description": "Filtro de aire para motor diesel",
            "category": "FILTROS",
            "quantity": 30,
            "minimum_stock": 15,
            "unit_cost": 12000,
            "location": "Bodega A - Estante 1",
            "supplier": "Repuestos Industriales S.A."
        },
        {
            "part_number": "ACE-001",
            "name": "Aceite Motor 15W-40",
            "description": "Aceite mineral para motor diesel",
            "category": "LUBRICANTES",
            "quantity": 50,
            "minimum_stock": 20,
            "unit_cost": 8500,
            "location": "Bodega B - Zona Líquidos",
            "supplier": "Lubricantes del Norte"
        },
        {
            "part_number": "NEU-001",
            "name": "Neumático 295/80R22.5",
            "description": "Neumático para camión pesado",
            "category": "NEUMATICOS",
            "quantity": 8,
            "minimum_stock": 4,
            "unit_cost": 250000,
            "location": "Bodega C - Neumáticos",
            "supplier": "Neumáticos Mineros Ltda."
        },
        {
            "part_number": "BAT-001",
            "name": "Batería 12V 180Ah",
            "description": "Batería para arranque de motor diesel",
            "category": "ELECTRICOS",
            "quantity": 6,
            "minimum_stock": 3,
            "unit_cost": 180000,
            "location": "Bodega A - Estante 5",
            "supplier": "Baterías Industriales"
        }
    ]
    
    created_parts = []
    for part_data in spare_parts:
        try:
            response = requests.post(
                f"{API_URL}/spare-parts/",
                headers=headers,
                json=part_data
            )
            if response.status_code in [200, 201]:
                part = response.json()
                created_parts.append(part)
                print(f"  ✅ Repuesto creado: {part_data['name']}")
            else:
                print(f"  ⚠️  Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return created_parts

def create_predictions(token, assets):
    """Crear predicciones de fallas"""
    print("\n🤖 Creando predicciones...")
    headers = create_headers(token)
    
    if not assets:
        print("  ⚠️  No hay activos disponibles")
        return []
    
    predictions = []
    risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    for i, asset in enumerate(assets):
        pred_data = {
            "asset": asset['id'],
            "failure_probability": random.uniform(10, 85),
            "predicted_failure_date": (datetime.now() + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
            "confidence_score": random.uniform(70, 95),
            "model_version": "v1.0.0",
            "risk_level": risk_levels[i % 4],
            "recommendations": f"Revisar sistema hidráulico y realizar mantenimiento preventivo en {asset['name']}"
        }
        
        try:
            response = requests.post(
                f"{API_URL}/predictions/",
                headers=headers,
                json=pred_data
            )
            if response.status_code in [200, 201]:
                pred = response.json()
                predictions.append(pred)
                print(f"  ✅ Predicción creada para: {asset['name']}")
            else:
                print(f"  ⚠️  Error: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return predictions

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 INYECCIÓN DE DATOS EN PRODUCCIÓN")
    print("=" * 60)
    
    # Obtener token
    token = get_auth_token()
    if not token:
        print("\n❌ No se pudo obtener el token. Abortando.")
        return
    
    # Crear datos
    assets = create_assets(token)
    work_orders = create_work_orders(token, assets)
    spare_parts = create_spare_parts(token)
    predictions = create_predictions(token, assets)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("=" * 60)
    print(f"  🚛 Activos: {len(assets)}")
    print(f"  📋 Órdenes de Trabajo: {len(work_orders)}")
    print(f"  🔧 Repuestos: {len(spare_parts)}")
    print(f"  🤖 Predicciones: {len(predictions)}")
    print("=" * 60)
    print("\n✅ Proceso completado!")
    print(f"\n🌐 Accede al sistema en: {BASE_URL}")
    print(f"   Email: {ADMIN_EMAIL}")
    print(f"   Password: {ADMIN_PASSWORD}")

if __name__ == "__main__":
    main()
