# Deployment de Somacorbot a Cloud Run

## 📋 Resumen

El bot de Telegram está integrado en el backend de Django, por lo que se despliega junto con la aplicación principal.

## 🚀 Deployment

### Opción 1: Desplegar con el Backend (Recomendado)

El bot ya está integrado en el backend de Django, así que se despliega automáticamente cuando despliegas el backend.

```bash
# Desde el directorio backend/
gcloud run deploy cmms-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38"
```

### Opción 2: Usar Docker

```bash
# Build
docker build -t gcr.io/PROJECT_ID/cmms-backend:latest -f backend/Dockerfile backend/

# Push
docker push gcr.io/PROJECT_ID/cmms-backend:latest

# Deploy
gcloud run deploy cmms-backend \
  --image gcr.io/PROJECT_ID/cmms-backend:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38"
```

## 🔧 Configurar Webhook

Una vez desplegado, configurar el webhook de Telegram:

```bash
# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe cmms-backend --region us-central1 --format='value(status.url)')

# Configurar webhook
curl -X POST "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${SERVICE_URL}/api/v1/notifications/telegram/webhook/\"}"
```

## ✅ Verificar Deployment

```bash
# Verificar webhook
curl "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getWebhookInfo"

# Probar bot
# Enviar /start en Telegram a @Somacorbot
```

## 📝 Variables de Entorno Requeridas

```bash
TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38
DATABASE_URL=postgresql://...
GCP_PROJECT_ID=your-project-id
PUBSUB_NOTIFICATIONS_TOPIC=cmms-notifications
```

## 🔒 Seguridad

### Configurar Secret en Secret Manager

```bash
# Crear secret
echo -n "8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38" | \
  gcloud secrets create telegram-bot-token --data-file=-

# Dar acceso al service account
gcloud secrets add-iam-policy-binding telegram-bot-token \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Usar en Cloud Run
gcloud run services update cmms-backend \
  --update-secrets=TELEGRAM_BOT_TOKEN=telegram-bot-token:latest \
  --region us-central1
```

## 📊 Monitoreo

### Ver Logs

```bash
# Logs del servicio
gcloud run services logs read cmms-backend --region us-central1

# Filtrar logs de Telegram
gcloud run services logs read cmms-backend --region us-central1 | grep telegram
```

### Métricas

```bash
# Ver métricas del servicio
gcloud run services describe cmms-backend --region us-central1
```

## 🧪 Testing

### Test Local

```bash
# Ejecutar servidor local
cd backend
python manage.py runserver

# En otra terminal, configurar webhook local (usando ngrok)
ngrok http 8000

# Configurar webhook con URL de ngrok
curl -X POST "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-ngrok-url.ngrok.io/api/v1/notifications/telegram/webhook/"}'
```

### Test en Producción

```bash
# Probar comandos
/start
/help
/status
/equipos
/ordenes
/pendientes
/alertas
/kpis
```

## 🔄 Actualizar Bot

```bash
# 1. Hacer cambios en telegram_webhook.py
# 2. Commit y push
git add backend/apps/notifications/telegram_webhook.py
git commit -m "Update bot commands"
git push

# 3. Redesplegar
gcloud run deploy cmms-backend \
  --source backend/ \
  --region us-central1
```

## 🐛 Troubleshooting

### Bot no responde

1. Verificar webhook:
```bash
curl "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getWebhookInfo"
```

2. Verificar logs:
```bash
gcloud run services logs read cmms-backend --region us-central1 --limit 50
```

3. Verificar que el servicio esté corriendo:
```bash
gcloud run services describe cmms-backend --region us-central1
```

### Comandos no funcionan

1. Verificar que el usuario esté vinculado
2. Verificar permisos de rol
3. Revisar logs de errores

### Webhook no recibe mensajes

1. Verificar que la URL sea accesible públicamente
2. Verificar que el endpoint esté configurado correctamente
3. Verificar que no haya errores en el webhook handler

## ✅ Checklist de Deployment

- [ ] Backend desplegado en Cloud Run
- [ ] Variables de entorno configuradas
- [ ] Webhook configurado
- [ ] Webhook verificado con getWebhookInfo
- [ ] Bot probado con /start
- [ ] Comandos probados
- [ ] Logs monitoreados
- [ ] Documentación actualizada

## 🎉 ¡Listo!

El bot Somacorbot está desplegado y funcionando en Cloud Run.
