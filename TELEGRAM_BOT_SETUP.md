# Telegram Bot Integration - Guía de Configuración

## 📋 Información del Bot

**Bot Token:** `8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38`

**Bot Username:** (Obtener con `/getMe`)

## 🚀 Configuración

### 1. Variables de Entorno

Agregar al archivo `.env` del backend:

```bash
TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38
```

### 2. Migración de Base de Datos

Ejecutar la migración para agregar `telegram_chat_id` al modelo User:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 3. Obtener Chat ID

Para vincular un usuario con Telegram, necesitas su Chat ID. Hay varias formas:

#### Opción A: Usar el Bot @userinfobot

1. Buscar `@userinfobot` en Telegram
2. Iniciar conversación
3. El bot te enviará tu Chat ID

#### Opción B: Usar el Bot @getidsbot

1. Buscar `@getidsbot` en Telegram
2. Iniciar conversación
3. El bot te enviará tu Chat ID

#### Opción C: Crear un comando /start en tu bot

Agregar un webhook para recibir mensajes y extraer el chat_id.

## 🔌 API Endpoints

### Obtener Información del Bot

```bash
GET /api/v1/notifications/telegram/bot_info/
```

**Response:**
```json
{
  "id": 8206203157,
  "is_bot": true,
  "first_name": "CMMS Bot",
  "username": "cmms_notifications_bot",
  "can_join_groups": true,
  "can_read_all_group_messages": false,
  "supports_inline_queries": false
}
```

### Vincular Chat de Telegram

```bash
POST /api/v1/notifications/telegram/link_chat/
Content-Type: application/json
Authorization: Bearer <token>

{
  "chat_id": "123456789"
}
```

**Response:**
```json
{
  "message": "Telegram chat linked successfully",
  "chat_id": "123456789"
}
```

### Desvincular Chat

```bash
POST /api/v1/notifications/telegram/unlink_chat/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Telegram chat unlinked successfully"
}
```

### Enviar Notificación de Prueba

```bash
POST /api/v1/notifications/telegram/test_notification/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Test notification sent successfully"
}
```

## 📱 Flujo de Vinculación

### 1. Usuario obtiene su Chat ID

El usuario debe:
1. Buscar el bot en Telegram usando el username
2. Iniciar conversación con `/start`
3. Obtener su Chat ID (usando @userinfobot o similar)

### 2. Vincular en la aplicación

```typescript
// Frontend
const linkTelegramChat = async (chatId: string) => {
  const response = await api.post('/notifications/telegram/link_chat/', {
    chat_id: chatId
  });
  
  if (response.data.message) {
    // Vinculación exitosa
    // El usuario recibirá un mensaje de confirmación en Telegram
  }
};
```

### 3. Configurar Preferencias

```typescript
// Habilitar notificaciones de Telegram para un tipo específico
const updatePreferences = async () => {
  await api.post('/notifications/preferences/update_bulk/', {
    preferences: [
      {
        notification_type: 'WORK_ORDER_ASSIGNED',
        in_app_enabled: true,
        email_enabled: true,
        telegram_enabled: true  // ✅ Habilitar Telegram
      }
    ]
  });
};
```

## 📨 Formato de Notificaciones

Las notificaciones en Telegram se envían con el siguiente formato:

```
🟠 Nueva Orden de Trabajo Asignada

Se te ha asignado la orden OT-2024-001 para mantenimiento preventivo del Camión Supersucker 001.

Prioridad: HIGH
Tipo: WORK_ORDER_ASSIGNED

📋 Orden: OT-2024-001
📦 Activo: Camión Supersucker 001
```

### Emojis por Prioridad

- 🔴 **CRITICAL** - Notificación con sonido
- 🟠 **HIGH** - Notificación con sonido
- 🟡 **MEDIUM** - Notificación con sonido
- 🔵 **LOW** - Notificación silenciosa

## 🔧 Uso Programático

### Enviar Notificación Individual

```python
from apps.notifications.telegram_service import get_telegram_service

telegram_service = get_telegram_service()

# Enviar notificación
telegram_service.send_notification(
    chat_id='123456789',
    notification_type='WORK_ORDER_ASSIGNED',
    title='Nueva Orden Asignada',
    message='Se te ha asignado OT-2024-001',
    priority='HIGH',
    data={
        'work_order_number': 'OT-2024-001',
        'asset_name': 'Camión Supersucker 001'
    }
)
```

### Enviar Mensaje Simple

```python
telegram_service.send_message(
    chat_id='123456789',
    text='<b>Hola!</b> Este es un mensaje de prueba.',
    parse_mode='HTML'
)
```

### Crear Notificación con Telegram Automático

```python
from apps.notifications.models import Notification

# Crear notificación (se enviará automáticamente por Telegram si está habilitado)
notification = Notification.objects.create(
    user=user,
    notification_type='MAINTENANCE_DUE',
    priority='HIGH',
    title='Mantenimiento Vencido',
    message='El mantenimiento del activo está vencido',
    asset=asset
)

# El sistema verificará automáticamente:
# 1. Si el usuario tiene telegram_chat_id
# 2. Si tiene habilitadas las notificaciones de Telegram para este tipo
# 3. Si está en horario de silencio
```

## 🎯 Casos de Uso

### 1. Notificar Asignación de Orden de Trabajo

```python
# Cuando se asigna una orden de trabajo
work_order = WorkOrder.objects.create(...)

# Crear notificación
Notification.objects.create(
    user=assigned_user,
    notification_type='WORK_ORDER_ASSIGNED',
    priority='HIGH',
    title=f'Nueva orden asignada: {work_order.work_order_number}',
    message=f'Se te ha asignado la orden {work_order.work_order_number}',
    work_order=work_order
)

# Se enviará automáticamente por:
# - In-App (siempre)
# - Email (si está habilitado)
# - Telegram (si está habilitado y vinculado)
```

### 2. Alertas de Stock Bajo

```python
# Cuando el stock está bajo
spare_part = SparePart.objects.get(...)

if spare_part.current_stock <= spare_part.min_stock_level:
    # Notificar a administradores
    admins = User.objects.filter(role='ADMIN')
    
    for admin in admins:
        Notification.objects.create(
            user=admin,
            notification_type='LOW_STOCK',
            priority='MEDIUM',
            title=f'Stock bajo: {spare_part.name}',
            message=f'El stock de {spare_part.name} está bajo ({spare_part.current_stock} unidades)'
        )
```

### 3. Predicciones de Alto Riesgo

```python
# Cuando se detecta alto riesgo
prediction = FailurePrediction.objects.create(...)

if prediction.risk_level in ['HIGH', 'CRITICAL']:
    # Notificar a técnicos responsables
    Notification.objects.create(
        user=responsible_user,
        notification_type='PREDICTION_HIGH_RISK',
        priority='CRITICAL',
        title=f'Alerta: {prediction.asset.name}',
        message=f'Se ha detectado alto riesgo de falla ({prediction.failure_probability}%)',
        asset=prediction.asset,
        prediction=prediction
    )
```

## 🔒 Seguridad

### Validación de Chat ID

El sistema valida que el chat_id pertenezca al usuario que lo está vinculando enviando un mensaje de confirmación.

### Privacidad

- Los chat_id se almacenan encriptados en la base de datos
- Solo el usuario puede vincular/desvincular su chat
- Las notificaciones solo se envían si el usuario las ha habilitado

### Rate Limiting

Telegram tiene límites de tasa:
- 30 mensajes por segundo por bot
- 20 mensajes por minuto por chat

El sistema maneja estos límites automáticamente.

## 📊 Monitoreo

### Logs

```python
# Ver logs de Telegram
import logging
logger = logging.getLogger('apps.notifications.telegram_service')

# Los logs incluyen:
# - Mensajes enviados exitosamente
# - Errores de API
# - Chat IDs inválidos
```

### Métricas

Puedes monitorear:
- Número de usuarios con Telegram vinculado
- Notificaciones enviadas por Telegram
- Tasa de éxito/fallo

```python
# Obtener estadísticas
from django.contrib.auth import get_user_model
User = get_user_model()

# Usuarios con Telegram vinculado
users_with_telegram = User.objects.exclude(telegram_chat_id__isnull=True).count()

# Notificaciones enviadas por Telegram
from apps.notifications.models import Notification
telegram_notifications = Notification.objects.exclude(
    pubsub_message_id__isnull=True
).count()
```

## 🐛 Troubleshooting

### Error: "Chat not found"

**Causa:** El chat_id es inválido o el usuario bloqueó el bot.

**Solución:**
1. Verificar que el chat_id sea correcto
2. Pedir al usuario que inicie conversación con el bot
3. Verificar que el usuario no haya bloqueado el bot

### Error: "Bot was blocked by the user"

**Causa:** El usuario bloqueó el bot.

**Solución:**
1. Pedir al usuario que desbloquee el bot
2. Desvincular el chat automáticamente

### Notificaciones no llegan

**Verificar:**
1. ✅ Usuario tiene telegram_chat_id configurado
2. ✅ Preferencia telegram_enabled está en true
3. ✅ No está en horario de silencio
4. ✅ Bot token es válido
5. ✅ Usuario no bloqueó el bot

## 🎉 Conclusión

La integración de Telegram está completa y lista para usar. Los usuarios pueden:

1. ✅ Vincular su cuenta de Telegram
2. ✅ Configurar preferencias por tipo de notificación
3. ✅ Recibir notificaciones en tiempo real
4. ✅ Gestionar horarios de silencio
5. ✅ Desvincular su cuenta cuando quieran

El sistema envía notificaciones automáticamente por Telegram cuando:
- El usuario tiene telegram_chat_id configurado
- La preferencia telegram_enabled está habilitada
- No está en horario de silencio
- La prioridad lo permite
