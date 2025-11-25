# Real-time Notification System - Implementación Completa

## 📋 Resumen

Se ha implementado un sistema completo de notificaciones en tiempo real con integración de Google Cloud Pub/Sub, gestión de preferencias, UI moderna y soporte offline.

## 🎯 Componentes Implementados

### Backend

#### 1. Models (`backend/apps/notifications/models.py`)

**Notification Model:**
- Tipos: Work Order, Maintenance, Low Stock, Predictions, System
- Prioridades: LOW, MEDIUM, HIGH, CRITICAL
- Relaciones: WorkOrder, Asset, Prediction
- Estados: is_read, read_at
- Integración Pub/Sub: pubsub_message_id

**NotificationPreference Model:**
- Canales: In-App, Email, Push
- Quiet Hours: Horarios de silencio configurables
- Preferencias por tipo de notificación

#### 2. Pub/Sub Service (`backend/apps/notifications/pubsub_service.py`)

**Características:**
- Cliente de Google Cloud Pub/Sub
- Publicación de notificaciones individuales
- Publicación en lote
- Creación automática de topics
- Manejo de errores robusto

**Métodos:**
```python
publish_notification(user_id, notification_type, title, message, priority, data)
publish_bulk_notifications(notifications)
create_topic_if_not_exists()
```

#### 3. API Endpoints (`backend/apps/notifications/views.py`)

**NotificationViewSet:**
- `GET /notifications/` - Lista de notificaciones
- `GET /notifications/unread/` - No leídas
- `GET /notifications/unread_count/` - Contador
- `POST /notifications/{id}/mark_read/` - Marcar como leída
- `POST /notifications/mark_all_read/` - Marcar todas
- `DELETE /notifications/clear_read/` - Limpiar leídas
- `POST /notifications/bulk_create/` - Crear múltiples

**NotificationPreferenceViewSet:**
- `GET /preferences/` - Lista de preferencias
- `GET /preferences/defaults/` - Crear defaults
- `POST /preferences/update_bulk/` - Actualizar múltiples
- `PATCH /preferences/{id}/` - Actualizar una

### Frontend

#### 1. Types (`frontend/src/types/notification.types.ts`)

**Interfaces:**
- `Notification` - Notificación completa
- `NotificationPreference` - Preferencias de usuario
- `NotificationStats` - Estadísticas

#### 2. Service (`frontend/src/services/notificationService.ts`)

**Métodos:**
- `getNotifications()` - Obtener notificaciones
- `getUnreadNotifications()` - No leídas
- `getUnreadCount()` - Contador
- `markAsRead()` - Marcar como leída
- `markAllAsRead()` - Marcar todas
- `clearRead()` - Limpiar leídas
- `getPreferences()` - Obtener preferencias
- `updateBulkPreferences()` - Actualizar preferencias

#### 3. Store (`frontend/src/store/notificationStore.ts`)

**Estado:**
- `notifications` - Lista de notificaciones
- `unreadCount` - Contador de no leídas
- `isOnline` - Estado de conexión
- `queueSize` - Tamaño de cola offline

**Acciones:**
- `fetchNotifications()` - Cargar notificaciones
- `fetchUnreadCount()` - Actualizar contador
- `markAsRead()` - Marcar como leída
- `startPolling()` - Iniciar polling (30s)
- `syncOfflineQueue()` - Sincronizar cola offline

#### 4. Components

**NotificationBell:**
- Icono de campana con badge
- Dropdown con últimas 5 notificaciones
- Navegación a detalles
- Marcar como leída
- Polling automático cada 30s

**ToastNotification:**
- Notificaciones emergentes
- Colores por prioridad
- Auto-dismiss (5s)
- Botón de cerrar

**ToastContainer:**
- Contenedor de toasts
- Máximo 3 toasts simultáneos
- Posición: top-right

#### 5. Pages

**Notifications Page:**
- Lista completa de notificaciones
- Filtros: Todas / No leídas
- Marcar como leída
- Marcar todas como leídas
- Limpiar leídas
- Navegación a detalles

#### 6. Offline Queue (`frontend/src/services/offlineQueue.ts`)

**Características:**
- Cola en localStorage
- Máximo 100 notificaciones
- Sincronización automática al reconectar
- Event listeners para online/offline
- Callbacks de sincronización

## 📁 Estructura de Archivos

```
backend/apps/notifications/
├── models.py                    (Notification, NotificationPreference)
├── serializers.py               (Serializers)
├── views.py                     (ViewSets)
├── urls.py                      (URL configuration)
└── pubsub_service.py            (Pub/Sub integration)

frontend/src/
├── types/
│   └── notification.types.ts    (TypeScript types)
├── services/
│   ├── notificationService.ts   (API service)
│   └── offlineQueue.ts          (Offline queue)
├── store/
│   └── notificationStore.ts     (Zustand store)
├── components/
│   └── notifications/
│       ├── NotificationBell.tsx
│       ├── ToastNotification.tsx
│       └── ToastContainer.tsx
└── pages/
    └── Notifications.tsx        (Full page)
```

## 🔧 Configuración

### Backend Environment Variables

```bash
# Google Cloud Pub/Sub
GCP_PROJECT_ID=your-project-id
PUBSUB_NOTIFICATIONS_TOPIC=cmms-notifications

# Google Cloud credentials
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Frontend Integration

**App.tsx:**
```typescript
import ToastContainer from './components/notifications/ToastContainer';

function App() {
  return (
    <BrowserRouter>
      <ToastContainer />
      {/* ... routes ... */}
    </BrowserRouter>
  );
}
```

**Header.tsx:**
```typescript
import NotificationBell from '../notifications/NotificationBell';

<NotificationBell />
```

## 🚀 Flujo de Uso

### 1. Crear Notificación (Backend)

```python
from apps.notifications.models import Notification
from apps.notifications.pubsub_service import get_pubsub_service

# Crear notificación
notification = Notification.objects.create(
    user=user,
    notification_type='WORK_ORDER_ASSIGNED',
    priority='HIGH',
    title='Nueva orden asignada',
    message='Se te ha asignado la orden OT-2024-001',
    work_order=work_order
)

# Publicar a Pub/Sub
pubsub_service = get_pubsub_service()
message_id = pubsub_service.publish_notification(
    user_id=user.id,
    notification_type='WORK_ORDER_ASSIGNED',
    title='Nueva orden asignada',
    message='Se te ha asignado la orden OT-2024-001',
    priority='HIGH'
)

notification.pubsub_message_id = message_id
notification.save()
```

### 2. Recibir Notificaciones (Frontend)

```typescript
// En componente
import useNotificationStore from '../store/notificationStore';

const { unreadCount, fetchUnreadCount, startPolling } = useNotificationStore();

useEffect(() => {
  startPolling(); // Inicia polling cada 30s
  return () => stopPolling();
}, []);
```

### 3. Mostrar Toast

```typescript
// El ToastContainer automáticamente muestra toasts
// para nuevas notificaciones no leídas
<ToastContainer />
```

### 4. Gestionar Preferencias

```typescript
// Obtener preferencias
const preferences = await notificationService.getDefaultPreferences();

// Actualizar preferencias
await notificationService.updateBulkPreferences([
  {
    notification_type: 'WORK_ORDER_ASSIGNED',
    in_app_enabled: true,
    email_enabled: true,
    push_enabled: false,
  }
]);
```

## 📊 Tipos de Notificaciones

| Tipo | Descripción | Prioridad Default |
|------|-------------|-------------------|
| `WORK_ORDER_CREATED` | Orden de trabajo creada | MEDIUM |
| `WORK_ORDER_ASSIGNED` | Orden asignada | HIGH |
| `WORK_ORDER_COMPLETED` | Orden completada | MEDIUM |
| `MAINTENANCE_DUE` | Mantenimiento vencido | HIGH |
| `LOW_STOCK` | Stock bajo | MEDIUM |
| `PREDICTION_HIGH_RISK` | Predicción de alto riesgo | CRITICAL |
| `SYSTEM` | Notificación del sistema | LOW |

## 🎨 Colores por Prioridad

- **CRITICAL:** Rojo (#EF4444) 🔴
- **HIGH:** Naranja (#F97316) 🟠
- **MEDIUM:** Ámbar (#F59E0B) 🟡
- **LOW:** Azul (#3B82F6) 🔵

## 🔄 Polling y Sincronización

### Polling Automático
- Intervalo: 30 segundos
- Solo contador de no leídas
- Inicia automáticamente al montar NotificationBell
- Se detiene al desmontar

### Sincronización Offline
- Cola en localStorage
- Máximo 100 notificaciones
- Sincronización automática al reconectar
- Event listeners para online/offline

## 📱 Responsive Design

- **Desktop:** Dropdown completo con 5 notificaciones
- **Mobile:** Dropdown adaptado al ancho de pantalla
- **Toast:** Posición fija top-right, adaptable

## ✅ Testing

### Backend

```bash
# Crear notificación de prueba
python manage.py shell
>>> from apps.notifications.models import Notification
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.first()
>>> Notification.objects.create(
...     user=user,
...     notification_type='SYSTEM',
...     priority='HIGH',
...     title='Test',
...     message='Test notification'
... )
```

### Frontend

```bash
# Verificar polling
# Abrir DevTools > Network
# Buscar requests a /notifications/unread_count/ cada 30s

# Probar offline
# DevTools > Network > Offline
# Intentar marcar notificación como leída
# Volver online y verificar sincronización
```

## 🔍 Troubleshooting

### Notificaciones no aparecen

1. Verificar que el usuario esté autenticado
2. Revisar que startPolling() se llame
3. Verificar permisos de API
4. Revisar logs del backend

### Pub/Sub no funciona

1. Verificar GCP_PROJECT_ID
2. Verificar credenciales de GCP
3. Verificar que el topic exista
4. Revisar permisos de la cuenta de servicio

### Offline queue no sincroniza

1. Verificar localStorage
2. Revisar event listeners
3. Verificar conexión de red
4. Revisar logs de consola

## 📈 Mejoras Futuras

1. **WebSocket:**
   - Notificaciones en tiempo real
   - Sin polling
   - Menor latencia

2. **Push Notifications:**
   - Service Worker
   - Web Push API
   - Notificaciones del navegador

3. **Filtros Avanzados:**
   - Por fecha
   - Por tipo
   - Por prioridad

4. **Búsqueda:**
   - Buscar en notificaciones
   - Filtros combinados

5. **Agrupación:**
   - Agrupar notificaciones similares
   - Resumen de múltiples notificaciones

## 🎉 Conclusión

El sistema de notificaciones en tiempo real está completo con:
- ✅ Modelos de notificaciones y preferencias
- ✅ Integración con Google Cloud Pub/Sub
- ✅ API completa con 10+ endpoints
- ✅ Store de Zustand con polling
- ✅ Componentes UI modernos
- ✅ Página de notificaciones completa
- ✅ Sistema de toasts
- ✅ Cola offline con sincronización
- ✅ Soporte responsive
- ✅ Documentación completa

El sistema está listo para producción y puede manejar notificaciones en tiempo real con soporte offline completo.
