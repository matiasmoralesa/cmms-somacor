# Guía para Poblar la Base de Datos con Datos de Ejemplo

Este script crea datos de ejemplo realistas para el sistema CMMS que pueden ser utilizados para entrenar modelos de Machine Learning.

## Datos que se Crean

El script `populate_data.py` crea los siguientes datos:

### 1. Usuarios (8 usuarios)
- Técnicos, supervisores y gerentes
- Emails con dominio @somacor.com
- Contraseña por defecto: `password123`

### 2. Repuestos (27 items)
- Filtros (aceite, aire, hidráulico, combustible)
- Aceites y lubricantes
- Componentes mecánicos (rodamientos, sellos, correas)
- Componentes eléctricos (alternadores, baterías, sensores)
- Componentes hidráulicos (bombas, cilindros, válvulas)
- Componentes de motor (pistones, culatas, turbocompresores)
- Herramientas y consumibles

### 3. Activos (19 equipos)
- 4 Excavadoras (CAT, Komatsu, Volvo)
- 3 Cargadoras (CAT, Komatsu)
- 3 Camiones (Volvo, Mercedes, Scania)
- 2 Grúas (Liebherr, Tadano)
- 3 Generadores (CAT, Cummins, Perkins)
- 2 Compresores (Atlas Copco, Ingersoll Rand)
- 2 Bombas (Grundfos, KSB)

### 4. Historial de Mantenimiento
- Entre 3 y múltiples registros por activo (basado en horas de operación)
- Tipos: Preventivo (60%), Correctivo (25%), Predictivo (10%), Emergencia (5%)
- Incluye duración, costos y descripciones realistas

### 5. Órdenes de Trabajo
- Entre 5 y 15 órdenes por activo
- Estados: Abierta, En Progreso, Completada, Cancelada
- Prioridades: Baja, Media, Alta, Urgente
- Incluye tareas asociadas

### 6. Movimientos de Inventario
- Entradas (compras)
- Salidas (uso en órdenes de trabajo)
- Ajustes de inventario

### 7. Órdenes de Compra
- Entre 20 y 40 órdenes
- Estados: Borrador, Pendiente, Aprobada, Ordenada, Recibida, Cancelada
- Incluye items con cantidades y precios

## Requisitos Previos

1. Base de datos PostgreSQL configurada y migraciones aplicadas
2. Entorno virtual activado
3. Dependencias instaladas (incluyendo `faker`)

```bash
pip install faker
```

## Cómo Ejecutar el Script

### Opción 1: Desde el directorio backend

```bash
cd backend
python populate_data.py
```

### Opción 2: Como módulo de Django

```bash
cd backend
python manage.py shell < populate_data.py
```

### Opción 3: Usando el manage.py directamente

```bash
cd backend
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production'); import django; django.setup(); exec(open('populate_data.py').read())"
```

## Notas Importantes

1. **El script es idempotente**: Usa `get_or_create` para usuarios, repuestos y activos, por lo que puede ejecutarse múltiples veces sin duplicar estos datos.

2. **Datos realistas**: Los datos generados incluyen:
   - Fechas coherentes (compras, instalaciones, mantenimientos)
   - Horas de operación basadas en antigüedad del equipo
   - Costos y duraciones realistas según tipo de mantenimiento
   - Estados de equipos basados en uso

3. **Para ML**: Los datos incluyen suficiente historial para entrenar modelos de:
   - Predicción de fallas
   - Optimización de mantenimiento preventivo
   - Estimación de costos
   - Análisis de patrones de uso

4. **Limpieza de datos**: Si necesitas empezar de cero:

```bash
cd backend
python manage.py flush --no-input
python manage.py migrate
python populate_data.py
```

## Verificación

Después de ejecutar el script, deberías ver un resumen como este:

```
============================================================
RESUMEN DE DATOS CREADOS
============================================================
Usuarios: 8
Repuestos: 27
Activos: 19
Registros de Mantenimiento: XXX
Órdenes de Trabajo: XXX
Movimientos de Inventario: XXX
Órdenes de Compra: XX
============================================================
✓ Base de datos poblada exitosamente
============================================================
```

## Acceso a los Datos

Puedes acceder a los datos creados mediante:

1. **Django Admin**: http://localhost:8000/admin
   - Usuario: cualquiera de los creados
   - Contraseña: `password123`

2. **API REST**: http://localhost:8000/api/v1/
   - `/assets/` - Lista de activos
   - `/work-orders/` - Órdenes de trabajo
   - `/inventory/spare-parts/` - Repuestos
   - etc.

3. **Django Shell**:
```bash
python manage.py shell
>>> from apps.assets.models import Asset
>>> Asset.objects.count()
>>> Asset.objects.filter(status='OPERATIONAL').count()
```

## Personalización

Puedes modificar el script para:
- Cambiar la cantidad de datos generados
- Ajustar las probabilidades de estados
- Agregar más tipos de equipos
- Modificar rangos de costos y duraciones
- Agregar más descripciones de mantenimiento

## Solución de Problemas

### Error: "No module named 'faker'"
```bash
pip install faker
```

### Error: "DJANGO_SETTINGS_MODULE is not set"
El script ya configura esto automáticamente, pero si tienes problemas:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
```

### Error de base de datos
Verifica que PostgreSQL esté corriendo y las migraciones aplicadas:
```bash
python manage.py migrate
```
