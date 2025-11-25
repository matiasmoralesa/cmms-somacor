# Guía Completa de Configuración - Somacorbot

## 📋 Información del Bot

**Nombre:** Somacorbot
**Token:** `8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38`
**Username:** @Somacorbot (verificar en BotFather)

## 🎯 Paso 1: Configurar Información Básica en BotFather

### 1.1 Descripción Corta (About)

Abrir @BotFather y ejecutar:
```
/setabouttext
```
Seleccionar Somacorbot y pegar:

```
Bot oficial de Somacor CMMS para notificaciones de mantenimiento, órdenes de trabajo y alertas del sistema en tiempo real.
```

### 1.2 Descripción Larga (Description)

Ejecutar en @BotFather:
```
/setdescription
```
Seleccionar Somacorbot y pegar:

```
🔧 Somacorbot - Sistema CMMS Somacor

Bot oficial para recibir notificaciones instantáneas del sistema de gestión de mantenimiento.

📬 Notificaciones que recibirás:
• 📋 Órdenes de trabajo asignadas
• ⚙️ Mantenimiento preventivo programado
• 📦 Alertas de stock bajo en inventario
• 🔮 Predicciones de fallas de activos
• 🚨 Alertas críticas del sistema

🔗 Cómo vincular tu cuenta:
1. Envía /start para obtener tu Chat ID
2. Ingresa a la aplicación web CMMS
3. Ve a tu perfil > Notificaciones
4. Ingresa tu Chat ID y vincula tu cuenta
5. ¡Listo! Empezarás a recibir notificaciones

📱 Comandos disponibles:
/start - Obtener tu Chat ID
/help - Ver ayuda completa
/link - Instrucciones de vinculación
/status - Ver estado de tu cuenta
/test - Probar notificaciones

💡 Desarrollado por Somacor
```

### 1.3 Configurar Comandos

Ejecutar en @BotFather:
```
/setcommands
```
Seleccionar Somacorbot y pegar:

```
start - Iniciar bot y obtener Chat ID
help - Mostrar ayuda completa
link - Instrucciones para vincular cuenta
status - Ver estado de vinculación
test - Enviar notificación de prueba
equipos - Ver lista de equipos activos
ordenes - Ver tus órdenes de trabajo
pendientes - Ver órdenes pendientes
alertas - Ver alertas recientes
kpis - Ver métricas del sistema (Admin)
unlink - Desvincular cuenta
```

### 1.4 Configurar Foto de Perfil (Opcional)

Ejecutar en @BotFather:
```
/setuserpic
```
Seleccionar Somacorbot y enviar una imagen de 512x512 px con el logo de Somacor.

## 🔧 Paso 2: Crear Webhook Handler en Django



Creado en: `backend/apps/notifications/telegram_webhook.py`

Este archivo maneja todos los comandos del bot:
- `/start` - Muestra Chat ID y bienvenida
- `/help` - Ayuda completa
- `/link` - Instrucciones de vinculación
- `/status` - Estado de vinculación
- `/test` - Notificación de prueba
- `/unlink` - Desvincular cuenta

## 🌐 Paso 3: Configurar Webhook

### 3.1 Obtener URL del Webhook

Tu webhook estará en:
```
https://tu-dominio.com/api/v1/notifications/telegram/webhook/
```

O si usas Cloud Run:
```
https://tu-servicio.run.app/api/v1/notifications/telegram/webhook/
```

### 3.2 Configurar Webhook con Telegram

**Opción A: Usar el endpoint de Django**

```bash
curl -X POST https://tu-backend.com/api/v1/notifications/telegram/set_webhook/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://tu-dominio.com/api/v1/notifications/telegram/webhook/"}'
```

**Opción B: Usar API de Telegram directamente**

```bash
curl -X POST "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://tu-dominio.com/api/v1/notifications/telegram/webhook/"}'
```

**Opción C: Usar Python**

```python
import requests

BOT_TOKEN = "8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38"
WEBHOOK_URL = "https://tu-dominio.com/api/v1/notifications/telegram/webhook/"

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)

print(response.json())
```

### 3.3 Verificar Webhook

```bash
curl "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getWebhookInfo"
```

Deberías ver:
```json
{
  "ok": true,
  "result": {
    "url": "https://tu-dominio.com/api/v1/notifications/telegram/webhook/",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

## 🧪 Paso 4: Probar el Bot

### 4.1 Probar Comandos

1. Buscar @Somacorbot en Telegram
2. Enviar `/start`
3. Deberías recibir un mensaje con tu Chat ID
4. Probar otros comandos: `/help`, `/link`, `/status`

### 4.2 Probar Vinculación

1. Copiar tu Chat ID del mensaje de `/start`
2. Ir a la aplicación web CMMS
3. Perfil → Notificaciones → Telegram
4. Pegar Chat ID y hacer clic en "Vincular"
5. Deberías recibir un mensaje de confirmación en Telegram

### 4.3 Probar Notificación

1. En Telegram, enviar `/test`
2. Deberías recibir una notificación de prueba

## 📝 Paso 5: Configurar Variables de Entorno

Agregar al `.env` del backend:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38
TELEGRAM_WEBHOOK_URL=https://tu-dominio.com/api/v1/notifications/telegram/webhook/
```

## 🔒 Paso 6: Seguridad (Opcional pero Recomendado)

### 6.1 Validar Requests de Telegram

Agregar validación de IP en el webhook:

```python
TELEGRAM_IPS = [
    '149.154.160.0/20',
    '91.108.4.0/22'
]
```

### 6.2 Usar Secret Token

Al configurar el webhook, agregar un secret token:

```bash
curl -X POST "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://tu-dominio.com/api/v1/notifications/telegram/webhook/",
    "secret_token": "tu-secret-token-aqui"
  }'
```

## 📱 Paso 7: Uso del Bot

### Para Usuarios

1. **Obtener Chat ID:**
   - Buscar @Somacorbot
   - Enviar `/start`
   - Copiar el Chat ID

2. **Vincular Cuenta:**
   - Ir a CMMS Web → Perfil → Notificaciones
   - Pegar Chat ID
   - Clic en "Vincular Telegram"
   - Confirmar en Telegram

3. **Configurar Preferencias:**
   - En CMMS Web, seleccionar qué notificaciones recibir por Telegram
   - Guardar cambios

4. **Recibir Notificaciones:**
   - Las notificaciones llegarán automáticamente
   - Formato con emojis según prioridad
   - Enlaces a la aplicación web

### Comandos Disponibles

```
/start   - Obtener Chat ID
/help    - Ver ayuda
/link    - Instrucciones de vinculación
/status  - Ver estado de cuenta
/test    - Notificación de prueba
/unlink  - Desvincular cuenta
```

## 🎨 Paso 8: Personalización (Opcional)

### 8.1 Cambiar Mensajes

Editar `telegram_webhook.py` para personalizar los mensajes de cada comando.

### 8.2 Agregar Comandos

Agregar nuevos comandos en la función `handle_command()`.

### 8.3 Botones Inline (Avanzado)

Agregar botones interactivos a los mensajes:

```python
keyboard = {
    'inline_keyboard': [[
        {'text': '🔗 Vincular Cuenta', 'url': 'https://cmms.somacor.com/profile'},
        {'text': '📱 Ver App', 'url': 'https://cmms.somacor.com'}
    ]]
}

telegram_service.send_message(
    chat_id=chat_id,
    text=message,
    reply_markup=json.dumps(keyboard)
)
```

## 🐛 Troubleshooting

### Bot no responde

1. Verificar que el webhook esté configurado:
   ```bash
   curl "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getWebhookInfo"
   ```

2. Verificar logs del servidor:
   ```bash
   tail -f logs/django.log | grep telegram
   ```

3. Verificar que la URL del webhook sea accesible públicamente

### Notificaciones no llegan

1. Verificar que el usuario tenga `telegram_chat_id` configurado
2. Verificar preferencias de notificación
3. Verificar que `telegram_enabled` esté en `true`
4. Revisar logs de errores

### Error "Chat not found"

1. Usuario debe iniciar conversación con el bot primero
2. Verificar que el Chat ID sea correcto
3. Usuario no debe haber bloqueado el bot

## 📊 Monitoreo

### Ver Estadísticas del Bot

```bash
curl "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getMe"
```

### Ver Updates Pendientes

```bash
curl "https://api.telegram.org/bot8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38/getUpdates"
```

### Logs de Django

```python
# Ver logs de Telegram
import logging
logger = logging.getLogger('apps.notifications.telegram_webhook')
```

## ✅ Checklist de Configuración

- [ ] Configurar comandos en BotFather
- [ ] Configurar descripción del bot
- [ ] Configurar foto de perfil (opcional)
- [ ] Crear webhook handler en Django
- [ ] Configurar webhook URL
- [ ] Verificar webhook con getWebhookInfo
- [ ] Probar comando /start
- [ ] Probar vinculación de cuenta
- [ ] Probar notificación de prueba
- [ ] Configurar variables de entorno
- [ ] Documentar para usuarios finales

## 🎉 ¡Listo!

Tu bot Somacorbot está completamente configurado y listo para enviar notificaciones del sistema CMMS.

Los usuarios pueden:
1. ✅ Obtener su Chat ID con `/start`
2. ✅ Vincular su cuenta desde la web
3. ✅ Configurar preferencias de notificación
4. ✅ Recibir notificaciones en tiempo real
5. ✅ Probar con `/test`
6. ✅ Ver estado con `/status`
7. ✅ Desvincular con `/unlink`

## 📞 Soporte

Para problemas o preguntas:
- Revisar logs del servidor
- Verificar configuración del webhook
- Contactar al administrador del sistema
