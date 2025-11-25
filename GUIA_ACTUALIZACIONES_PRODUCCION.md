# Guía de Actualizaciones en Producción

## 📋 Índice
1. [Tipos de Cambios](#tipos-de-cambios)
2. [Proceso de Actualización](#proceso-de-actualización)
3. [Actualización sin Downtime](#actualización-sin-downtime)
4. [Rollback (Revertir Cambios)](#rollback-revertir-cambios)
5. [Casos de Uso Comunes](#casos-de-uso-comunes)
6. [Mejores Prácticas](#mejores-prácticas)

---

## Tipos de Cambios

### 🟢 Cambios Menores (Sin Downtime)
- Corrección de bugs
- Cambios en la UI
- Nuevas funcionalidades que no afectan la BD
- Actualizaciones de texto/traducciones
- Mejoras de rendimiento

**Tiempo estimado:** 10-30 minutos

### 🟡 Cambios Medianos (Downtime Mínimo)
- Cambios en modelos de BD (agregar campos)
- Nuevos endpoints API
- Cambios en lógica de negocio
- Actualizaciones de dependencias

**Tiempo estimado:** 30-60 minutos

### 🔴 Cambios Mayores (Requieren Planificación)
- Cambios estructurales en BD
- Migraciones de datos complejas
- Cambios en arquitectura
- Actualizaciones de versión mayor

**Tiempo estimado:** 1-3 horas

---

## Proceso de Actualización

### Paso 1: Preparación

#### 1.1 Crear Rama de Desarrollo
```bash
# Crear rama para tu cambio
git checkout -b feature/nueva-funcionalidad

# Hacer tus cambios
# ... editar archivos ...

# Commit
git add .
git commit -m "feat: agregar nueva funcionalidad X"

# Push
git push origin feature/nueva-funcionalidad
```

#### 1.2 Probar Localmente
```bash
# Backend
cd backend
python manage.py test
python manage.py runserver

# Frontend
cd frontend
npm run test
npm run dev

# Verificar que todo funciona
```

#### 1.3 Crear Backup
```bash
# Backup de base de datos
gcloud sql backups create --instance=cmms-db

# Verificar backup
gcloud sql backups list --instance=cmms-db

# Guardar ID del backup por si necesitas revertir
BACKUP_ID=$(gcloud sql backups list --instance=cmms-db --limit=1 --format="value(id)")
echo "Backup ID: $BACKUP_ID"
```

### Paso 2: Actualización del Backend

#### 2.1 Build Nueva Versión
```bash
cd backend

# Build con tag de versión
VERSION="v1.1.0"
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/cmms-backend:${VERSION}

# También tagear como latest
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/cmms-backend:latest
```

#### 2.2 Desplegar sin Tráfico (Blue-Green Deployment)
```bash
# Desplegar nueva versión sin enviarle tráfico
gcloud run deploy cmms-backend \
  --image gcr.io/TU_PROJECT_ID/cmms-backend:${VERSION} \
  --region us-central1 \
  --no-traffic \
  --tag ${VERSION}

# Esto crea una URL temporal para probar
# https://v1-1-0---cmms-backend-xxx-uc.a.run.app
```

#### 2.3 Probar Nueva Versión
```bash
# Obtener URL de la nueva versión
NEW_URL=$(gcloud run services describe cmms-backend \
  --region us-central1 \
  --format="value(status.traffic[0].url)")

# Probar health check
curl ${NEW_URL}/api/v1/core/health/

# Probar login
curl -X POST ${NEW_URL}/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@somacor.com","password":"Demo2024!"}'

# Si todo está OK, continuar
```

#### 2.4 Ejecutar Migraciones (si hay)
```bash
# Solo si hay cambios en la base de datos
gcloud run jobs create cmms-migrate-${VERSION} \
  --image gcr.io/TU_PROJECT_ID/cmms-backend:${VERSION} \
  --region us-central1 \
  --set-cloudsql-instances TU_PROJECT_ID:us-central1:cmms-db \
  --set-secrets="SECRET_KEY=django-secret-key:latest,DB_PASSWORD=db-password:latest" \
  --command python \
  --args manage.py,migrate

gcloud run jobs execute cmms-migrate-${VERSION} --region us-central1 --wait
```

#### 2.5 Migrar Tráfico Gradualmente
```bash
# Enviar 10% del tráfico a la nueva versión
gcloud run services update-traffic cmms-backend \
  --region us-central1 \
  --to-revisions=${VERSION}=10

# Esperar 5-10 minutos y monitorear errores
# Ver logs en tiempo real
gcloud logging tail "resource.type=cloud_run_revision" --limit=50

# Si todo está bien, aumentar a 50%
gcloud run services update-traffic cmms-backend \
  --region us-central1 \
  --to-revisions=${VERSION}=50

# Esperar otros 5-10 minutos

# Si todo sigue bien, migrar 100%
gcloud run services update-traffic cmms-backend \
  --region us-central1 \
  --to-revisions=${VERSION}=100
```

### Paso 3: Actualización del Frontend

#### 3.1 Build Nueva Versión
```bash
cd frontend

# Actualizar variable de entorno si cambió la URL del backend
# (normalmente no cambia)

# Build
npm run build

# Verificar build
ls -la dist/
```

#### 3.2 Preview Antes de Desplegar
```bash
# Crear canal de preview
firebase hosting:channel:deploy preview-${VERSION}

# Esto te da una URL temporal para probar
# https://tu-proyecto--preview-v1-1-0-xxx.web.app

# Probar en el navegador
# Verificar que todo funciona
```

#### 3.3 Desplegar a Producción
```bash
# Si el preview está OK, desplegar
firebase deploy --only hosting

# Firebase mantiene versiones anteriores automáticamente
# Puedes revertir desde la consola si es necesario
```

### Paso 4: Actualización de Otros Servicios

#### 4.1 Bot de Telegram
```bash
cd telegram-bot

# Build nueva versión
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/cmms-telegram-bot:${VERSION}

# Desplegar
gcloud run deploy cmms-telegram-bot \
  --image gcr.io/TU_PROJECT_ID/cmms-telegram-bot:${VERSION} \
  --region us-central1

# El bot se actualiza automáticamente sin downtime
```

#### 4.2 DAGs de Airflow
```bash
cd airflow/dags

# Obtener bucket de DAGs
DAGS_BUCKET=$(gcloud composer environments describe cmms-composer \
  --location us-central1 \
  --format="value(config.dagGcsPrefix)")

# Subir DAGs actualizados
gsutil -m cp *.py ${DAGS_BUCKET}/

# Los DAGs se actualizan automáticamente en 1-2 minutos
```

### Paso 5: Verificación Post-Actualización

```bash
# 1. Health checks
curl https://TU_BACKEND_URL/api/v1/core/health/

# 2. Verificar logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50 \
  --format=json

# 3. Verificar métricas en Cloud Console
# https://console.cloud.google.com/monitoring

# 4. Probar funcionalidad crítica
# - Login
# - Crear orden de trabajo
# - Ver activos
# - Ejecutar checklist

# 5. Verificar bot de Telegram
# Enviar /status y verificar respuesta
```

---

## Actualización sin Downtime

### Estrategia: Blue-Green Deployment

Cloud Run hace esto automáticamente cuando usas `--no-traffic`:

```bash
# 1. Desplegar nueva versión (Green) sin tráfico
gcloud run deploy cmms-backend \
  --image gcr.io/TU_PROJECT_ID/cmms-backend:new \
  --no-traffic \
  --tag new

# 2. Probar versión nueva
curl https://new---cmms-backend-xxx.run.app/api/v1/core/health/

# 3. Cambiar tráfico gradualmente
gcloud run services update-traffic cmms-backend \
  --to-revisions=new=10  # 10%

# 4. Monitorear

# 5. Aumentar gradualmente
gcloud run services update-traffic cmms-backend \
  --to-revisions=new=50  # 50%

# 6. Completar migración
gcloud run services update-traffic cmms-backend \
  --to-revisions=new=100  # 100%

# La versión anterior (Blue) sigue disponible para rollback
```

### Ventajas:
- ✅ Cero downtime
- ✅ Rollback instantáneo
- ✅ Pruebas en producción con tráfico real
- ✅ Migración gradual y segura

---

## Rollback (Revertir Cambios)

### Escenario 1: Problema Detectado Inmediatamente

#### Opción A: Cambiar Tráfico a Versión Anterior
```bash
# Listar revisiones disponibles
gcloud run revisions list \
  --service=cmms-backend \
  --region=us-central1

# Cambiar todo el tráfico a la versión anterior
gcloud run services update-traffic cmms-backend \
  --region us-central1 \
  --to-revisions=REVISION_ANTERIOR=100

# Esto toma efecto en segundos
```

#### Opción B: Redesplegar Versión Anterior
```bash
# Redesplegar imagen anterior
gcloud run deploy cmms-backend \
  --image gcr.io/TU_PROJECT_ID/cmms-backend:v1.0.0 \
  --region us-central1
```

### Escenario 2: Problema en Base de Datos

```bash
# 1. Detener aplicación (opcional, para evitar más cambios)
gcloud run services update cmms-backend \
  --region us-central1 \
  --min-instances=0 \
  --max-instances=0

# 2. Restaurar backup de base de datos
gcloud sql backups restore BACKUP_ID \
  --backup-instance=cmms-db

# 3. Reactivar aplicación con versión anterior
gcloud run services update cmms-backend \
  --region us-central1 \
  --min-instances=1 \
  --max-instances=10

gcloud run services update-traffic cmms-backend \
  --to-revisions=VERSION_ANTERIOR=100
```

### Escenario 3: Rollback de Frontend

```bash
# Firebase mantiene historial de deploys
firebase hosting:rollback

# O desde la consola web:
# https://console.firebase.google.com
# Hosting > Ver historial > Rollback
```

---

## Casos de Uso Comunes

### Caso 1: Agregar un Nuevo Campo a un Modelo

```python
# backend/apps/assets/models.py
class Asset(models.Model):
    # ... campos existentes ...
    nuevo_campo = models.CharField(max_length=100, null=True, blank=True)
```

**Proceso:**
```bash
# 1. Crear migración
python manage.py makemigrations

# 2. Probar localmente
python manage.py migrate
python manage.py test

# 3. Commit y push
git add .
git commit -m "feat: agregar campo nuevo_campo a Asset"
git push

# 4. Build y deploy
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/cmms-backend:v1.1.0

# 5. Deploy sin tráfico
gcloud run deploy cmms-backend \
  --image gcr.io/TU_PROJECT_ID/cmms-backend:v1.1.0 \
  --no-traffic \
  --tag v1-1-0

# 6. Ejecutar migración
gcloud run jobs execute cmms-migrate-v1-1-0 --wait

# 7. Migrar tráfico
gcloud run services update-traffic cmms-backend \
  --to-revisions=v1-1-0=100
```

### Caso 2: Corregir un Bug en el Frontend

```bash
# 1. Hacer el cambio
cd frontend/src/components
# ... editar archivo ...

# 2. Probar localmente
npm run dev

# 3. Build y deploy
npm run build
firebase deploy --only hosting

# Listo! Se actualiza en 1-2 minutos
```

### Caso 3: Actualizar Texto/Traducciones

```bash
# 1. Editar archivos de traducción
cd frontend/src/locales
# ... editar es.json ...

# 2. Build y deploy
npm run build
firebase deploy --only hosting

# No requiere cambios en backend
# No requiere migraciones
# Actualización instantánea
```

### Caso 4: Agregar Nuevo Endpoint API

```python
# backend/apps/work_orders/views.py
@api_view(['GET'])
def get_statistics(request):
    # ... nueva funcionalidad ...
    return Response(data)
```

**Proceso:**
```bash
# 1. Agregar endpoint
# 2. Agregar tests
# 3. Probar localmente
# 4. Deploy backend (proceso normal)
# 5. Actualizar frontend para usar nuevo endpoint
# 6. Deploy frontend
```

### Caso 5: Actualizar Dependencias

```bash
# Backend
cd backend
pip install --upgrade django
pip freeze > requirements.txt

# Probar
python manage.py test

# Deploy
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/cmms-backend:v1.1.1

# Frontend
cd frontend
npm update
npm audit fix

# Probar
npm run test
npm run build

# Deploy
firebase deploy --only hosting
```

---

## Mejores Prácticas

### ✅ Antes de Actualizar

1. **Crear backup de base de datos**
   ```bash
   gcloud sql backups create --instance=cmms-db
   ```

2. **Probar en ambiente local**
   ```bash
   docker-compose up
   # Probar todos los cambios
   ```

3. **Ejecutar suite de pruebas**
   ```bash
   cd backend
   ./run_integration_tests.sh
   ./run_security_tests.sh
   ```

4. **Revisar changelog**
   - Documentar qué cambió
   - Identificar breaking changes
   - Planificar comunicación a usuarios

5. **Programar ventana de mantenimiento** (para cambios mayores)
   - Notificar a usuarios con 24-48 horas de anticipación
   - Elegir horario de bajo tráfico (ej: 2-4 AM)

### ✅ Durante la Actualización

1. **Monitorear logs en tiempo real**
   ```bash
   gcloud logging tail "resource.type=cloud_run_revision" --limit=100
   ```

2. **Verificar métricas**
   - Tasa de errores
   - Tiempo de respuesta
   - Uso de recursos

3. **Migración gradual de tráfico**
   - 10% → esperar 5 min → verificar
   - 50% → esperar 10 min → verificar
   - 100% → monitorear por 30 min

4. **Tener plan de rollback listo**
   - Comandos preparados
   - Backup ID anotado
   - Persona responsable identificada

### ✅ Después de Actualizar

1. **Verificación funcional**
   - Probar flujos críticos
   - Verificar integraciones
   - Revisar reportes

2. **Monitoreo extendido**
   - Primeras 2 horas: monitoreo activo
   - Primeras 24 horas: revisión periódica
   - Primera semana: atención a reportes de usuarios

3. **Documentar**
   - Actualizar changelog
   - Documentar problemas encontrados
   - Actualizar guías si es necesario

4. **Comunicar**
   - Notificar a usuarios de nuevas funcionalidades
   - Enviar release notes
   - Actualizar documentación de usuario

### ✅ Versionado Semántico

Usar formato: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0 → 2.0.0): Cambios incompatibles
- **MINOR** (1.0.0 → 1.1.0): Nueva funcionalidad compatible
- **PATCH** (1.0.0 → 1.0.1): Corrección de bugs

Ejemplos:
```bash
v1.0.0  # Lanzamiento inicial
v1.0.1  # Corrección de bug
v1.1.0  # Nueva funcionalidad: reportes avanzados
v1.1.1  # Corrección de bug en reportes
v2.0.0  # Cambio mayor: nueva arquitectura
```

---

## 🚨 Qué Hacer si Algo Sale Mal

### Problema: Alta Tasa de Errores

```bash
# 1. Rollback inmediato
gcloud run services update-traffic cmms-backend \
  --to-revisions=VERSION_ANTERIOR=100

# 2. Revisar logs
gcloud logging read "severity>=ERROR" --limit=100

# 3. Identificar causa
# 4. Corregir en desarrollo
# 5. Volver a intentar
```

### Problema: Base de Datos Corrupta

```bash
# 1. Detener aplicación
gcloud run services update cmms-backend --max-instances=0

# 2. Restaurar backup
gcloud sql backups restore BACKUP_ID --backup-instance=cmms-db

# 3. Verificar integridad
# 4. Reactivar aplicación
gcloud run services update cmms-backend --max-instances=10
```

### Problema: Frontend No Carga

```bash
# 1. Rollback en Firebase
firebase hosting:rollback

# 2. Verificar
curl https://tu-proyecto.web.app

# 3. Revisar logs de Firebase
firebase hosting:channel:list
```

---

## 📊 Checklist de Actualización

### Pre-Actualización
- [ ] Backup de base de datos creado
- [ ] Cambios probados localmente
- [ ] Tests pasando
- [ ] Changelog actualizado
- [ ] Usuarios notificados (si aplica)
- [ ] Plan de rollback preparado

### Durante Actualización
- [ ] Nueva versión desplegada sin tráfico
- [ ] Pruebas en versión nueva exitosas
- [ ] Migraciones ejecutadas (si aplica)
- [ ] Tráfico migrado gradualmente
- [ ] Logs monitoreados
- [ ] Métricas normales

### Post-Actualización
- [ ] Verificación funcional completa
- [ ] Monitoreo por 24 horas
- [ ] Sin errores críticos
- [ ] Usuarios notificados de cambios
- [ ] Documentación actualizada
- [ ] Retrospectiva realizada (si hubo problemas)

---

## 💡 Tips Adicionales

### Automatización con CI/CD

Puedes automatizar el proceso con GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and Deploy Backend
        run: |
          gcloud builds submit --tag gcr.io/$PROJECT_ID/cmms-backend
          gcloud run deploy cmms-backend --image gcr.io/$PROJECT_ID/cmms-backend
      
      - name: Deploy Frontend
        run: |
          cd frontend
          npm install
          npm run build
          firebase deploy --only hosting
```

### Ambiente de Staging

Considera tener un ambiente de staging:

```bash
# Crear servicios de staging
gcloud run deploy cmms-backend-staging \
  --image gcr.io/TU_PROJECT_ID/cmms-backend:staging

firebase hosting:channel:deploy staging
```

### Monitoreo de Cambios

```bash
# Ver historial de revisiones
gcloud run revisions list --service=cmms-backend

# Ver tráfico actual
gcloud run services describe cmms-backend \
  --format="value(status.traffic)"
```

---

## 📞 Contacto

Si tienes dudas sobre actualizaciones:
- Email: devops@tu-empresa.com
- Documentación: Ver DEPLOYMENT_PROCEDURES.md
- Soporte GCP: console.cloud.google.com/support

---

**Versión:** 1.0  
**Fecha:** 2024-11-13  
**Próxima Revisión:** Después de cada actualización mayor
