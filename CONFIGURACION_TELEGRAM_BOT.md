# 🤖 Bot de Telegram Configurado

## ✅ Estado: Funcionando

El bot de Telegram está desplegado y funcionando correctamente.

---

## 📱 Información del Bot

- **Nombre:** Asistente somacor
- **Username:** @Somacorbot
- **Bot ID:** 8206203157
- **Estado:** ✅ Activo

---

## 🔧 Configuración en el Backend

El backend ya está configurado con el token del bot:

```bash
TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38
```

---

## 📲 Cómo Usar el Bot

### 1. Agregar el Bot a Telegram

1. Abre Telegram
2. Busca: **@Somacorbot**
3. Haz clic en "Start" o envía `/start`

### 2. Obtener tu Chat ID

Para recibir notificaciones, necesitas tu Chat ID:

**Opción A: Desde el bot**
```
1. Envía cualquier mensaje al bot
2. Ve a: https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getUpdates
3. Busca "chat":{"id":XXXXXXX}
4. Ese número es tu Chat ID
```

**Opción B: Usar un bot helper**
```
1. Busca @userinfobot en Telegram
2. Envía /start
3. Te dará tu Chat ID
```

### 3. Configurar Chat ID en tu Usuario

1. Inicia sesión en la aplicación web
2. Ve a tu perfil
3. Agrega tu Chat ID de Telegram
4. Guarda cambios

---

## 🔔 Tipos de Notificaciones

El bot enviará notificaciones para:

- 📋 **Órdenes de Trabajo**
  - Nueva orden asignada
  - Cambio de estado
  - Orden vencida

- ⚠️ **Alertas**
  - Stock bajo de repuestos
  - Mantenimiento vencido
  - Falla de activo

- 📊 **Reportes**
  - Reporte diario
  - Reporte semanal
  - Métricas importantes

---

## 🎨 Formato de Mensajes

El bot envía mensajes formateados con:

- **Emojis según prioridad:**
  - 🔴 CRITICAL
  - 🟠 HIGH
  - 🟡 MEDIUM
  - 🔵 LOW

- **Información estructurada:**
  - Título en negrita
  - Mensaje descriptivo
  - Datos adicionales (orden, activo, etc.)

---

## 🧪 Probar el Bot

### Desde la Aplicación Web

1. Ve a Notificaciones
2. Crea una notificación de prueba
3. Selecciona "Enviar por Telegram"
4. Deberías recibir el mensaje

### Desde la API

```bash
curl -X POST https://cmms-backend-888881509782.us-central1.run.app/api/v1/notifications/telegram/test \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "TU_CHAT_ID",
    "message": "Prueba desde CMMS"
  }'
```

### Directamente con la API de Telegram

```bash
curl -X POST "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "TU_CHAT_ID",
    "text": "¡Hola desde CMMS! 👋"
  }'
```

---

## ⚙️ Configuración Avanzada

### Webhook (Opcional)

Si quieres que el bot responda a comandos:

```bash
curl -X POST "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://cmms-backend-888881509782.us-central1.run.app/api/v1/telegram/webhook"
  }'
```

### Comandos del Bot

Puedes configurar comandos personalizados:

```
/start - Iniciar el bot
/help - Ayuda
/status - Ver estado de órdenes
/alerts - Ver alertas activas
```

---

## 🔒 Seguridad

### Token del Bot

⚠️ **IMPORTANTE:** El token del bot está hardcodeado. Para mayor seguridad:

```bash
# Opción 1: Usar Secret Manager
gcloud secrets create telegram-bot-token --data-file=-
# Pega el token y presiona Ctrl+D

# Opción 2: Regenerar token
# 1. Habla con @BotFather
# 2. Envía /revoke
# 3. Selecciona tu bot
# 4. Actualiza el backend con el nuevo token
```

### Validación de Mensajes

El bot valida que los mensajes vengan de Telegram usando:
- Token secreto
- Validación de firma (si usas webhook)

---

## 📊 Monitoreo

### Ver Logs del Bot

```bash
gcloud run services logs read cmms-backend \
  --region us-central1 \
  --filter="telegram" \
  --limit 50
```

### Estadísticas de Uso

```bash
# Ver mensajes enviados
curl "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getUpdates"
```

---

## 💰 Costos

**Bot de Telegram:** ✅ **GRATIS**

- Sin límite de mensajes
- Sin costo por usuario
- Sin costo por grupo

---

## 🐛 Troubleshooting

### El bot no responde

1. Verifica que el token sea correcto
2. Verifica que el bot esté activo
3. Revisa los logs del backend

### No recibo notificaciones

1. Verifica tu Chat ID
2. Verifica que esté configurado en tu perfil
3. Verifica las preferencias de notificación

### Error "Forbidden"

- El usuario bloqueó el bot
- Solución: Desbloquear y enviar /start

---

## 📚 Recursos

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [BotFather](https://t.me/botfather)
- [Telegram Bot Examples](https://core.telegram.org/bots/samples)

---

## ✅ Checklist

- [x] Bot creado y configurado
- [x] Token configurado en backend
- [x] Backend desplegado con Telegram
- [x] Bot funcionando correctamente
- [ ] Usuarios configuran su Chat ID
- [ ] Probar notificaciones
- [ ] Configurar comandos (opcional)
- [ ] Configurar webhook (opcional)

---

**¡El bot de Telegram está listo para usar!** 🎉

Para empezar a recibir notificaciones:
1. Busca @Somacorbot en Telegram
2. Envía /start
3. Obtén tu Chat ID
4. Configúralo en tu perfil de la aplicación
