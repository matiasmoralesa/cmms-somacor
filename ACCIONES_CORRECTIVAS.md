# Acciones Correctivas - Sistema CMMS SOMACOR

**Fecha**: 18 de Noviembre de 2025  
**Basado en**: Reporte de Pruebas v1.0

---

## 🚨 Acciones Críticas (Ejecutar Hoy)

### 1. Corregir Error en Módulo de Notificaciones

**Problema**: Error 500 al intentar acceder a `/api/v1/notifications/`

**Causa Raíz**: Tabla `notifications_notification` no existe en la base de datos

**Solución**:

```bash
# Paso 1: Conectar al Cloud SQL Proxy
./cloud_sql_proxy.exe cmms-somacorv2:us-central1:cmms-db

# Paso 2: En otra terminal, ejecutar migraciones
cd backend
export DATABASE_URL="postgresql://cmms_user:CmmsSecure2024!@127.0.0.1:5432/cmms_prod"
python manage.py migrate

# Paso 3: Verificar que las tablas se crearon
python manage.py showmigrations
```

**Verificación**:
```bash
# Probar endpoint de notificaciones
curl -H "Authorization: Bearer <token>" \
  https://cmms-backend-888881509782.us-central1.run.app/api/v1/notifications/
```

**Tiempo Estimado**: 15 minutos  
**Prioridad**: 🔴 CRÍTICA  
**Responsable**: DevOps / Backend Developer

---

### 2. Verificar y Recrear Datos de Inventario

**Problema**: API de inventario funciona pero no hay repuestos registrados

**Causa Raíz**: Datos no se persistieron correctamente o fueron eliminados

**Solución**:

```bash
# Paso 1: Verificar datos actuales
python -c "
import requests
token = '<admin_token>'
headers = {'Authorization': f'Bearer {token}'}
r = requests.get('https://cmms-backend-888881509782.us-central1.run.app/api/v1/inventory/spare-parts/', headers=headers)
print(f'Repuestos actuales: {len(r.json().get(\"results\", []))}')
"

# Paso 2: Recrear datos si es necesario
python cargar_datos_completos.py

# Paso 3: Verificar nuevamente
# Repetir paso 1
```

**Verificación**:
- Debe haber al menos 5 repuestos registrados
- Categorías: FILTERS, LUBRICANTS, TIRES, ELECTRICAL

**Tiempo Estimado**: 10 minutos  
**Prioridad**: 🟡 ALTA  
**Responsable**: Backend Developer

---

### 3. Recrear Planes de Mantenimiento

**Problema**: No hay planes de mantenimiento registrados

**Causa Raíz**: Datos no se persistieron correctamente

**Solución**:

```bash
# Opción 1: Usar script de carga completa
python cargar_datos_completos.py

# Opción 2: Crear manualmente vía API
python -c "
import requests
from datetime import datetime, timedelta

token = '<admin_token>'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Obtener primer activo
assets = requests.get('https://cmms-backend-888881509782.us-central1.run.app/api/v1/assets/', headers=headers).json()
asset_id = assets['results'][0]['id']

# Crear plan
plan = {
    'name': 'Mantenimiento Preventivo Mensual',
    'description': 'Plan de mantenimiento preventivo cada 250 horas',
    'plan_type': 'PREVENTIVE',
    'asset': asset_id,
    'frequency_type': 'HOURS',
    'frequency_value': 250,
    'estimated_duration_hours': 4,
    'is_active': True
}

r = requests.post('https://cmms-backend-888881509782.us-central1.run.app/api/v1/maintenance/plans/', 
                  headers=headers, json=plan)
print(f'Plan creado: {r.status_code}')
"
```

**Verificación**:
- Debe haber al menos 3 planes de mantenimiento
- Al menos 1 plan activo por cada tipo de vehículo principal

**Tiempo Estimado**: 20 minutos  
**Prioridad**: 🟡 ALTA  
**Responsable**: Backend Developer

---

## ⚠️ Acciones Importantes (Esta Semana)

### 4. Crear Usuarios de Prueba

**Problema**: Solo existe usuario admin, no se pueden probar otros roles

**Solución**:

```python
# Script: crear_usuarios_prueba.py
import requests

BACKEND_URL = "https://cmms-backend-888881509782.us-central1.run.app"

# Login como admin
response = requests.post(f"{BACKEND_URL}/api/v1/auth/login/",
                        json={"email": "admin@cmms.com", "password": "admin123"})
token = response.json()["access"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Obtener roles
roles_response = requests.get(f"{BACKEND_URL}/api/v1/auth/roles/", headers=headers)
roles_data = roles_response.json()
if isinstance(roles_data, dict) and 'results' in roles_data:
    roles_data = roles_data['results']
roles = {r['name']: r['id'] for r in roles_data}

# Crear usuarios
usuarios = [
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
        "employee_status": "ACTIVE"
    },
    {
        "email": "operador2@somacor.com",
        "password": "Operador123!",
        "first_name": "María",
        "last_name": "Silva",
        "rut": "34567890-1",
        "role": roles.get("OPERADOR"),
        "phone": "+56934567890",
        "employee_status": "ACTIVE"
    }
]

for usuario in usuarios:
    r = requests.post(f"{BACKEND_URL}/api/v1/auth/users/", headers=headers, json=usuario)
    print(f"{usuario['email']}: {r.status_code}")
```

**Verificación**:
```bash
# Probar login con cada usuario
python plan_pruebas_cmms.py
```

**Tiempo Estimado**: 15 minutos  
**Prioridad**: 🟡 ALTA  
**Responsable**: Backend Developer

---

### 5. Implementar Monitoreo de Errores

**Problema**: No hay visibilidad de errores en producción

**Solución**:

```bash
# Opción 1: Google Cloud Monitoring (ya disponible)
# Configurar alertas en GCP Console

# Opción 2: Sentry (recomendado)
# 1. Crear cuenta en sentry.io
# 2. Agregar a requirements.txt:
echo "sentry-sdk[django]==1.40.0" >> backend/requirements.txt

# 3. Configurar en settings.py:
cat >> backend/config/settings/production.py << 'EOF'

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment='production'
)
EOF

# 4. Agregar variable de entorno en Cloud Run
gcloud run services update cmms-backend \
  --region=us-central1 \
  --set-env-vars="SENTRY_DSN=<your-sentry-dsn>"
```

**Verificación**:
- Errores aparecen en Sentry dashboard
- Alertas configuradas para errores críticos

**Tiempo Estimado**: 30 minutos  
**Prioridad**: 🟡 ALTA  
**Responsable**: DevOps

---

### 6. Documentar APIs

**Problema**: Falta documentación de ejemplos de uso

**Solución**:

```bash
# La documentación Swagger ya está disponible en:
# https://cmms-backend-888881509782.us-central1.run.app/api/docs/

# Agregar ejemplos adicionales:
# 1. Revisar cada endpoint en views.py
# 2. Agregar decoradores @extend_schema con ejemplos
# 3. Actualizar schema_examples.py con más casos

# Ejemplo:
@extend_schema(
    tags=['Activos'],
    summary='Listar activos',
    description='Obtiene lista de todos los activos con filtros opcionales',
    parameters=[
        OpenApiParameter(
            name='vehicle_type',
            type=str,
            description='Filtrar por tipo de vehículo',
            examples=[
                OpenApiExample('Camionetas', value='CAMIONETA_MDO'),
                OpenApiExample('Camiones', value='CAMION_SUPERSUCKER'),
            ]
        )
    ],
    responses={
        200: AssetSerializer(many=True),
        401: OpenApiResponse(description='No autenticado'),
    }
)
```

**Verificación**:
- Documentación Swagger actualizada
- Ejemplos de request/response para cada endpoint

**Tiempo Estimado**: 2 horas  
**Prioridad**: 🟢 MEDIA  
**Responsable**: Backend Developer

---

## 📋 Acciones Deseables (Próximas 2 Semanas)

### 7. Implementar Pruebas Automatizadas en CI/CD

**Objetivo**: Ejecutar pruebas automáticamente en cada commit

**Solución**:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-django
    
    - name: Run tests
      run: |
        cd backend
        pytest
    
    - name: Run API tests
      run: |
        python plan_pruebas_cmms.py
```

**Tiempo Estimado**: 3 horas  
**Prioridad**: 🟢 MEDIA

---

### 8. Configurar Alertas de Disponibilidad

**Objetivo**: Recibir notificaciones si el sistema cae

**Solución**:

```bash
# Crear uptime check en GCP
gcloud monitoring uptime create cmms-backend-check \
  --resource-type=uptime-url \
  --host=cmms-backend-888881509782.us-central1.run.app \
  --path=/api/v1/auth/login/ \
  --check-interval=5m

# Crear política de alertas
gcloud alpha monitoring policies create \
  --notification-channels=<channel-id> \
  --display-name="CMMS Backend Down" \
  --condition-display-name="Backend Unavailable" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s
```

**Tiempo Estimado**: 1 hora  
**Prioridad**: 🟢 MEDIA

---

### 9. Realizar Pruebas de Usuario (UAT)

**Objetivo**: Validar que el sistema cumple expectativas de usuarios finales

**Pasos**:

1. **Preparación**:
   - Crear usuarios de prueba para cada rol
   - Preparar escenarios de prueba
   - Documentar flujos de trabajo

2. **Ejecución**:
   - Sesión con supervisores (2 horas)
   - Sesión con operadores (2 horas)
   - Sesión con mecánicos (2 horas)

3. **Documentación**:
   - Registrar feedback
   - Priorizar mejoras
   - Crear tickets de trabajo

**Tiempo Estimado**: 1 semana  
**Prioridad**: 🟢 MEDIA

---

## 📊 Checklist de Verificación

### Antes de Marcar como Completo

- [ ] Módulo de notificaciones funcionando (sin error 500)
- [ ] Al menos 5 repuestos en inventario
- [ ] Al menos 3 planes de mantenimiento activos
- [ ] 4 usuarios de prueba creados (1 admin, 1 supervisor, 2 operadores)
- [ ] Todas las pruebas automatizadas pasando (>80%)
- [ ] Monitoreo configurado y funcionando
- [ ] Alertas configuradas
- [ ] Documentación API actualizada
- [ ] Logs revisados sin errores críticos
- [ ] Backup de base de datos configurado

---

## 🎯 Métricas de Éxito

### Objetivos Cuantitativos

| Métrica | Actual | Objetivo | Estado |
|---------|--------|----------|--------|
| Pruebas Exitosas | 76.2% | >90% | 🟡 |
| Disponibilidad APIs | 87.5% | >95% | 🟡 |
| Tiempo Respuesta | <200ms | <300ms | ✅ |
| Errores Críticos | 1 | 0 | 🔴 |
| Cobertura Módulos | 87.5% | 100% | 🟡 |

### Objetivos Cualitativos

- ✅ Sistema desplegado en producción
- ✅ Autenticación segura funcionando
- ✅ Módulos core operativos
- 🟡 Todos los módulos sin errores
- 🟡 Datos de prueba completos
- ⏳ Monitoreo implementado
- ⏳ Documentación completa

---

## 📞 Escalamiento

### Si los problemas persisten:

1. **Nivel 1 - Developer**: Revisar logs y código
2. **Nivel 2 - Tech Lead**: Revisar arquitectura y diseño
3. **Nivel 3 - DevOps**: Revisar infraestructura y configuración
4. **Nivel 4 - Vendor Support**: Contactar soporte de GCP si es necesario

---

**Última actualización**: 18 de Noviembre de 2025  
**Próxima revisión**: 20 de Noviembre de 2025  
**Responsable**: Equipo de Desarrollo CMMS
