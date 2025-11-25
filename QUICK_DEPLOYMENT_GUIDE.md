# 🚀 Guía Rápida de Despliegue en GCP

## ⚡ Despliegue en 5 Pasos (30 minutos)

### Paso 1: Preparación (5 min)

```bash
# Navegar a la carpeta de despliegue
cd deployment/gcp

# Dar permisos de ejecución
chmod +x *.sh

# Ejecutar script de preparación
./00-prepare-deployment.sh
```

**Qué hace este script:**
- ✅ Verifica herramientas instaladas (gcloud, firebase, docker, etc.)
- ✅ Solicita información del proyecto
- ✅ Genera secretos seguros automáticamente
- ✅ Crea archivos de configuración
- ✅ Habilita APIs necesarias en GCP
- ✅ Verifica facturación

### Paso 2: Despliegue Automático (20 min)

```bash
# Ejecutar despliegue completo
./deploy-all.sh
```

**Qué hace este script:**
1. Crea Cloud SQL (PostgreSQL)
2. Crea 4 buckets de Storage
3. Configura Pub/Sub (topics y subscriptions)
4. Despliega Backend a Cloud Run
5. Despliega Frontend a Firebase Hosting
6. Configura CORS y variables de entorno

### Paso 3: Crear Superusuario (2 min)

```bash
# Opción A: Usando Cloud Run (Recomendado)
gcloud run services update cmms-backend \
  --set-env-vars="CREATE_SUPERUSER=true,DJANGO_SUPERUSER_EMAIL=admin@cmms.com,DJANGO_SUPERUSER_PASSWORD=Admin123!" \
  --region us-central1

# Esperar 30 segundos
sleep 30

# Remover variables (seguridad)
gcloud run services update cmms-backend \
  --remove-env-vars="CREATE_SUPERUSER,DJANGO_SUPERUSER_EMAIL,DJANGO_SUPERUSER_PASSWORD" \
  --region us-central1
```

### Paso 4: Verificar Despliegue (2 min)

```bash
# Obtener URLs
source .env.gcp
echo "Backend: $SERVICE_URL"
echo "Frontend: $FRONTEND_URL"

# Probar backend
curl $SERVICE_URL/api/v1/core/health/live/

# Abrir frontend en navegador
# Windows: start $FRONTEND_URL
# Mac: open $FRONTEND_URL
# Linux: xdg-open $FRONTEND_URL
```

### Paso 5: Acceder al Sistema (1 min)

1. Abre el frontend en tu navegador
2. Inicia sesión con:
   - Email: `admin@cmms.com`
   - Password: `Admin123!`
3. ¡Listo! 🎉

---

## 📋 Checklist Pre-Despliegue

Antes de empezar, asegúrate de tener:

- [ ] Cuenta de Google Cloud Platform
- [ ] Tarjeta de crédito/débito para facturación
- [ ] Google Cloud SDK instalado (`gcloud`)
- [ ] Firebase CLI instalado (`firebase-tools`)
- [ ] Docker instalado (opcional, para builds locales)
- [ ] 30 minutos de tiempo disponible

---

## 💰 Costos Esperados

### Primera Vez (Gratis)
- Google Cloud ofrece $300 en créditos gratuitos
- Suficiente para 6-12 meses de uso en desarrollo

### Después de Créditos
- **Desarrollo**: ~$13/mes
- **Producción Pequeña**: ~$50-100/mes
- **Producción Mediana**: ~$200-400/mes

---

## 🔧 Configuraciones Recomendadas

### Para Desarrollo/Testing

```bash
# Antes de ejecutar deploy-all.sh, edita .env.gcp:
export DB_TIER="db-f1-micro"
export CLOUD_RUN_MIN_INSTANCES="0"
export CLOUD_RUN_MAX_INSTANCES="2"
export CLOUD_RUN_MEMORY="512Mi"
```

**Costo**: ~$7-10/mes

### Para Producción (Recomendado)

```bash
# Antes de ejecutar deploy-all.sh, edita .env.gcp:
export DB_TIER="db-g1-small"
export CLOUD_RUN_MIN_INSTANCES="1"
export CLOUD_RUN_MAX_INSTANCES="10"
export CLOUD_RUN_MEMORY="1Gi"
```

**Costo**: ~$50-70/mes

---

## 🆘 Solución de Problemas

### Error: "Permission denied"

```bash
# Verificar autenticación
gcloud auth list

# Re-autenticar si es necesario
gcloud auth login

# Verificar proyecto
gcloud config get-value project
```

### Error: "Billing not enabled"

1. Ve a: https://console.cloud.google.com/billing
2. Vincula una cuenta de facturación
3. Vuelve a ejecutar el script

### Error: "API not enabled"

```bash
# Habilitar todas las APIs necesarias
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  pubsub.googleapis.com \
  cloudbuild.googleapis.com
```

### Backend no responde

```bash
# Ver logs
gcloud run services logs read cmms-backend --region us-central1 --limit 50

# Verificar estado
gcloud run services describe cmms-backend --region us-central1
```

### Frontend muestra error de conexión

```bash
# Verificar URL del backend en frontend
cat ../../frontend/.env.production

# Debe coincidir con:
gcloud run services describe cmms-backend --region us-central1 --format="value(status.url)"
```

---

## 📊 Monitoreo Post-Despliegue

### Ver Logs en Tiempo Real

```bash
# Backend
gcloud run services logs tail cmms-backend --region us-central1

# Filtrar errores
gcloud run services logs tail cmms-backend --region us-central1 --log-filter="severity>=ERROR"
```

### Ver Métricas

```bash
# Abrir Cloud Console
echo "https://console.cloud.google.com/run/detail/us-central1/cmms-backend/metrics?project=$GCP_PROJECT_ID"
```

### Configurar Alertas Básicas

```bash
# Alerta de errores
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="CMMS Backend Errors" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=60s
```

---

## 🔄 Actualizar la Aplicación

### Actualizar Backend

```bash
cd deployment/gcp
./04-deploy-backend-cloud-run.sh
```

### Actualizar Frontend

```bash
cd deployment/gcp
./05-deploy-frontend-firebase.sh
```

### Rollback (Si algo sale mal)

```bash
# Backend
gcloud run services update-traffic cmms-backend \
  --to-revisions=PREVIOUS=100 \
  --region us-central1

# Frontend
firebase hosting:rollback
```

---

## 🔐 Seguridad Post-Despliegue

### 1. Cambiar Contraseña de Admin

```bash
# Conectar a Cloud SQL
./cloud-sql-proxy-setup.sh

# En otra terminal
cd ../../backend
python manage.py changepassword admin@cmms.com
```

### 2. Configurar Backups Automáticos

```bash
# Ya están configurados por defecto (diarios a las 3 AM)
# Verificar:
gcloud sql backups list --instance=cmms-db
```

### 3. Configurar Alertas de Seguridad

```bash
# Habilitar Cloud Audit Logs
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member=user:tu-email@gmail.com \
  --role=roles/logging.viewer
```

---

## 📱 Configurar Dominio Personalizado (Opcional)

### Backend

```bash
# Mapear dominio
gcloud run domain-mappings create \
  --service cmms-backend \
  --domain api.tudominio.com \
  --region us-central1

# Seguir instrucciones para configurar DNS
```

### Frontend

```bash
# En Firebase Console
firebase hosting:channel:deploy production --only hosting
```

O manualmente en: https://console.firebase.google.com/project/_/hosting

---

## 📈 Optimizaciones Recomendadas

### Después de 1 Semana

1. **Revisar Logs**: Identificar errores recurrentes
2. **Optimizar Queries**: Agregar índices si es necesario
3. **Ajustar Auto-scaling**: Según patrones de uso
4. **Configurar Caché**: Implementar Redis si hay carga alta

### Después de 1 Mes

1. **Análisis de Costos**: Optimizar recursos no utilizados
2. **Implementar CDN**: Para assets estáticos
3. **Configurar Cloud Armor**: Protección DDoS
4. **Implementar Monitoring Avanzado**: Dashboards personalizados

---

## 🎯 Próximos Pasos Opcionales

### 1. Telegram Bot (Notificaciones Móviles)

```bash
# Ver guía completa en:
cat ../../TELEGRAM_BOT_SETUP.md
```

### 2. Cloud Composer (Automatización)

```bash
cd deployment/gcp
./06-setup-cloud-composer.sh
```

### 3. ML Service (Predicciones)

```bash
# Entrenar modelo inicial
cd ../../backend
python manage.py train_ml_model

# Desplegar a Vertex AI
# Ver guía en: VERTEX_AI_SETUP.md
```

---

## 📞 Soporte

### Documentación Completa

- `DEPLOYMENT_READINESS_ANALYSIS.md` - Análisis completo del proyecto
- `deployment/gcp/README.md` - Guía detallada de despliegue
- `MONITORING_SETUP.md` - Configuración de monitoreo
- `USER_GUIDE.md` - Guía de usuario del sistema

### Comandos Útiles

```bash
# Ver todos los recursos creados
gcloud projects describe $GCP_PROJECT_ID

# Ver costos actuales
gcloud billing accounts list

# Ver servicios activos
gcloud services list --enabled

# Eliminar todo (CUIDADO!)
# ./cleanup-all.sh
```

---

## ✅ Checklist Post-Despliegue

- [ ] Sistema desplegado y accesible
- [ ] Superusuario creado
- [ ] Login funciona correctamente
- [ ] Todos los CRUDs funcionan
- [ ] Contraseña de admin cambiada
- [ ] Backups configurados
- [ ] Logs monitoreados
- [ ] Alertas configuradas
- [ ] Documentación revisada
- [ ] Equipo capacitado

---

## 🎉 ¡Felicidades!

Tu sistema CMMS está ahora desplegado en Google Cloud Platform y listo para usar.

**URLs de Acceso:**
- Frontend: Revisa `.env.gcp` para `FRONTEND_URL`
- Backend API: Revisa `.env.gcp` para `SERVICE_URL`
- API Docs: `{SERVICE_URL}/api/docs/`

**Credenciales Iniciales:**
- Email: `admin@cmms.com`
- Password: `Admin123!` (¡Cámbiala inmediatamente!)

---

**Tiempo Total**: ~30 minutos
**Costo Inicial**: Gratis (con créditos de GCP)
**Costo Mensual**: $13-100 (según configuración)

¿Preguntas? Revisa la documentación completa o contacta al equipo de soporte.
