#!/usr/bin/env python
"""
Script para agregar estados de máquinas (Machine Status) a la base de datos
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.assets.models import Asset, Location
from apps.machine_status.models import AssetStatus, AssetStatusHistory

User = get_user_model()

def create_machine_statuses():
    """Crear estados de máquinas para todos los activos"""
    print("Creando estados de máquinas...")
    
    assets = Asset.objects.all()
    users = User.objects.filter(role__name__in=['OPERADOR', 'SUPERVISOR'])
    
    if not assets.exists():
        print("  ⚠️  No hay activos en la base de datos. Ejecuta populate_data.py primero.")
        return []
    
    if not users.exists():
        print("  ⚠️  No hay usuarios operadores/supervisores. Ejecuta populate_data.py primero.")
        return []
    
    statuses = []
    status_types = ['OPERANDO', 'DETENIDA', 'EN_MANTENIMIENTO', 'FUERA_DE_SERVICIO']
    
    for asset in assets:
        # Crear 3-8 registros de estado por activo (historial)
        num_statuses = random.randint(3, 8)
        
        for i in range(num_statuses):
            days_ago = random.randint(1, 90)
            reported_at = timezone.now() - timedelta(days=days_ago)
            
            # Determinar estado (mayoría operando)
            if i == 0:  # Estado más reciente
                status_type = random.choices(
                    status_types,
                    weights=[70, 15, 10, 5]
                )[0]
            else:
                status_type = random.choices(
                    status_types,
                    weights=[60, 20, 15, 5]
                )[0]
            
            # Generar datos realistas (max 10 digitos totales, 2 decimales)
            odometer_reading = Decimal(str(round(random.uniform(1000, 99999), 2)))
            fuel_level = random.randint(10, 100)
            
            condition_notes = [
                "Equipo en condiciones normales de operación",
                "Requiere revisión menor en próximo mantenimiento",
                "Operando sin novedades",
                "Pequeña fuga de aceite detectada, programar revisión",
                "Ruido anormal en motor, requiere inspección",
                "Equipo operando correctamente",
                "Nivel de aceite bajo, completado",
                "Neumáticos en buen estado",
            ]
            
            status = AssetStatus.objects.create(
                asset=asset,
                status_type=status_type,
                odometer_reading=odometer_reading,
                fuel_level=fuel_level,
                condition_notes=random.choice(condition_notes),
                reported_by=random.choice(users),
                location=asset.location,
                reported_at=reported_at
            )
            
            statuses.append(status)
    
    print(f"  ✓ Creados {len(statuses)} registros de estado")
    return statuses

def main():
    print("=" * 60)
    print("AGREGANDO ESTADOS DE MÁQUINAS")
    print("=" * 60)
    print("")
    
    try:
        statuses = create_machine_statuses()
        
        print("")
        print("=" * 60)
        print("RESUMEN")
        print("=" * 60)
        print(f"Estados de máquinas creados: {len(statuses)}")
        print("=" * 60)
        print("✓ Estados agregados exitosamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
