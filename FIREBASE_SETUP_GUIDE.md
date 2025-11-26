# Firebase Setup Guide - CMMS Image Processing & Real-Time Chat

Esta guía te ayudará a configurar Firebase para el sistema de procesamiento de imágenes y chat en tiempo real.

## Requisitos Previos

- Cuenta de Google/Gmail
- Acceso a Google Cloud Console
- Permisos para crear proyectos en Firebase

## Paso 1: Crear Proyecto Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com)
2. Haz clic en "Agregar proyecto" o "Add project"
3. Ingresa el nombre del proyecto: `cmms-somacor` (o el nombre que prefieras)
4. Acepta los términos y condiciones
5. Habilita Google Analytics (opcional pero recomendado)
6. Haz clic en "Crear proyecto"

## Paso 2: Habilitar Firestore Database

1. En el menú lateral, ve a **Build > Firestore Database**
2. Haz clic en "Crear base de datos" o "Create database"
3. Selecciona el modo:
   - **Modo de producción**: Requiere reglas de seguridad (recomendado)
   - **Modo de prueba**: Acceso abierto por 30 días (solo para desarrollo)
4. Selecciona la ubicación del servidor:
   - Para Chile: `southamerica-east1` (São Paulo, Brasil)
   - Alternativa: `us-central1` (Iowa, USA)
5. Haz clic en "Habilitar"

### Configurar Reglas de Seguridad de Firestore

Una vez creada la base de datos, configura las reglas de seguridad:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper function to check if user is authenticated
    function isAuthenticated() {
      return request.auth != null;
    }
    
    // Helper function to check if user is admin or supervisor
    function isAdminOrSupervisor() {
      return isAuthenticated() && 
             (request.auth.token.role == 'ADMIN' || 
              request.auth.token.role == 'SUPERVISOR');
    }
    
    // Helper function to check if user is participant in room
    function isParticipant(roomId) {
      return isAuthenticated() && 
             request.auth.uid in get(/databases/$(database)/documents/chat_rooms/$(roomId)).data.participants;
    }
    
    // Chat rooms - only participants can read, admins can write
    match /chat_rooms/{roomId} {
      allow read: if isParticipant(roomId) || isAdminOrSupervisor();
      allow create: if isAuthenticated();
      allow update: if isParticipant(roomId) || isAdminOrSupervisor();
      allow delete: if isAdminOrSupervisor();
      
      // Messages subcollection
      match /messages/{messageId} {
        allow read: if isParticipant(roomId) || isAdminOrSupervisor();
        allow create: if isParticipant(roomId);
        allow update: if isParticipant(roomId) && 
                        request.auth.uid == resource.data.senderId;
        allow delete: if isAdminOrSupervisor();
      }
    }
    
    // User presence - users can only update their own presence
    match /user_presence/{userId} {
      allow read: if isAuthenticated();
      allow write: if isAuthenticated() && request.auth.uid == userId;
    }
    
    // Notifications - users can only read their own notifications
    match /notifications/{userId}/{document=**} {
      allow read: if isAuthenticated() && request.auth.uid == userId;
      allow write: if isAdminOrSupervisor();
    }
  }
}
```

## Paso 3: Habilitar Cloud Messaging (FCM)

1. En el menú lateral, ve a **Build > Cloud Messaging**
2. Si es la primera vez, haz clic en "Comenzar" o "Get started"
3. FCM se habilitará automáticamente
4. Anota el **Server Key** (lo necesitarás más adelante)

### Configurar Cloud Messaging para Web

1. Ve a **Project Settings** (ícono de engranaje)
2. Selecciona la pestaña **Cloud Messaging**
3. En "Web configuration", genera un nuevo par de claves:
   - Haz clic en "Generate key pair"
   - Copia el **Web Push certificate** (VAPID key)

## Paso 4: Descargar Credenciales de Service Account

1. Ve a **Project Settings** (ícono de engranaje)
2. Selecciona la pestaña **Service accounts**
3. Haz clic en "Generate new private key"
4. Confirma haciendo clic en "Generate key"
5. Se descargará un archivo JSON con las credenciales
6. **IMPORTANTE**: Guarda este archivo de forma segura, contiene credenciales sensibles
7. Renombra el archivo a algo descriptivo, por ejemplo: `firebase-cmms-credentials.json`
8. Mueve el archivo a una ubicación segura en tu proyecto (NO lo subas a Git)

## Paso 5: Configurar Variables de Entorno

Edita el archivo `backend/.env` y configura las siguientes variables:

```env
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=/ruta/completa/a/firebase-cmms-credentials.json
FIREBASE_DATABASE_URL=https://cmms-somacor.firebaseio.com
FIREBASE_STORAGE_BUCKET=cmms-somacor.appspot.com
```

**Nota**: Reemplaza `cmms-somacor` con el ID real de tu proyecto Firebase.

### Encontrar los valores correctos:

- **FIREBASE_DATABASE_URL**: 
  - Ve a Project Settings > General
  - Busca "Realtime Database URL" (aunque uses Firestore, este valor es necesario)
  - Formato: `https://[PROJECT_ID].firebaseio.com`

- **FIREBASE_STORAGE_BUCKET**:
  - Ve a Project Settings > General
  - Busca "Storage bucket"
  - Formato: `[PROJECT_ID].appspot.com`

## Paso 6: Configurar Firebase en el Frontend

1. Ve a **Project Settings** en Firebase Console
2. En la sección "Your apps", haz clic en el ícono web `</>`
3. Registra tu app web:
   - Nombre de la app: `CMMS Web App`
   - No es necesario configurar Firebase Hosting por ahora
4. Copia la configuración de Firebase que aparece

Crea el archivo `frontend/src/config/firebase.ts`:

```typescript
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getMessaging, getToken } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: "TU_API_KEY",
  authDomain: "cmms-somacor.firebaseapp.com",
  projectId: "cmms-somacor",
  storageBucket: "cmms-somacor.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456",
  measurementId: "G-XXXXXXXXXX"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
export const db = getFirestore(app);

// Initialize Cloud Messaging
export const messaging = getMessaging(app);

// Request notification permission and get FCM token
export const requestNotificationPermission = async () => {
  try {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      const token = await getToken(messaging, {
        vapidKey: 'TU_VAPID_KEY'
      });
      return token;
    }
    return null;
  } catch (error) {
    console.error('Error getting notification permission:', error);
    return null;
  }
};
```

## Paso 7: Configurar Índices de Firestore

Para optimizar las consultas, crea los siguientes índices:

1. Ve a **Firestore Database > Indexes**
2. Crea los siguientes índices compuestos:

### Índice para mensajes de chat:
- Collection: `chat_rooms/{roomId}/messages`
- Campos:
  - `timestamp` (Descending)
  - `senderId` (Ascending)

### Índice para notificaciones:
- Collection: `notifications/{userId}/sent`
- Campos:
  - `createdAt` (Descending)
  - `type` (Ascending)

## Paso 8: Habilitar Offline Persistence (Opcional)

Para habilitar la persistencia offline en el frontend, actualiza la configuración:

```typescript
import { enableIndexedDbPersistence } from 'firebase/firestore';

// Enable offline persistence
enableIndexedDbPersistence(db)
  .catch((err) => {
    if (err.code === 'failed-precondition') {
      console.warn('Multiple tabs open, persistence can only be enabled in one tab at a time.');
    } else if (err.code === 'unimplemented') {
      console.warn('The current browser does not support offline persistence');
    }
  });
```

## Paso 9: Verificar la Configuración

Ejecuta el siguiente script para verificar que Firebase está correctamente configurado:

```bash
cd backend
python manage.py shell
```

Luego ejecuta:

```python
from apps.images.services.firebase_service import firebase_service

# Verificar que Firebase está disponible
print(f"Firebase disponible: {firebase_service.is_available()}")

# Intentar crear una sala de chat de prueba
if firebase_service.is_available():
    room = firebase_service.create_chat_room(
        work_order_id='TEST-001',
        participants=['user1', 'user2']
    )
    print(f"Sala de chat creada: {room}")
```

## Paso 10: Configurar Límites y Cuotas

Para evitar costos inesperados, configura límites:

1. Ve a **Firestore Database > Usage**
2. Configura alertas de uso
3. Establece límites diarios:
   - Lecturas: 50,000/día (capa gratuita)
   - Escrituras: 20,000/día (capa gratuita)
   - Eliminaciones: 20,000/día (capa gratuita)

## Estructura de Datos en Firestore

### Colección: `chat_rooms`

```javascript
{
  "workOrderId": "WO-12345",
  "assetId": "ASSET-001",
  "participants": ["user1", "user2", "user3"],
  "createdAt": Timestamp,
  "lastMessageAt": Timestamp,
  "lastMessage": {
    "text": "Último mensaje",
    "senderId": "user1",
    "timestamp": Timestamp
  }
}
```

### Subcolección: `chat_rooms/{roomId}/messages`

```javascript
{
  "roomId": "WO-12345",
  "senderId": "user1",
  "senderName": "Juan Pérez",
  "senderRole": "OPERADOR",
  "text": "Mensaje de texto",
  "imageUrl": "https://storage.googleapis.com/...",
  "timestamp": Timestamp,
  "readBy": ["user1", "user2"],
  "edited": false
}
```

### Colección: `user_presence`

```javascript
{
  "userId": "user1",
  "online": true,
  "lastSeen": Timestamp,
  "typingIn": "WO-12345",
  "deviceTokens": ["fcm-token-1", "fcm-token-2"]
}
```

### Colección: `notifications/{userId}/sent`

```javascript
{
  "userId": "user1",
  "type": "chat",
  "title": "Nuevo mensaje",
  "body": "Tienes un nuevo mensaje en WO-12345",
  "data": {
    "workOrderId": "WO-12345",
    "chatRoomId": "WO-12345",
    "deepLink": "/work-orders/WO-12345/chat"
  },
  "createdAt": Timestamp,
  "sentAt": Timestamp,
  "deliveredAt": Timestamp,
  "readAt": Timestamp
}
```

## Solución de Problemas

### Error: "Firebase is not available"

- Verifica que el archivo de credenciales existe en la ruta especificada
- Verifica que las variables de entorno están correctamente configuradas
- Verifica que el archivo de credenciales tiene los permisos correctos

### Error: "Permission denied" en Firestore

- Revisa las reglas de seguridad de Firestore
- Verifica que el usuario está autenticado
- Verifica que el token JWT incluye el campo `role`

### Error: "Failed to get FCM token"

- Verifica que Cloud Messaging está habilitado
- Verifica que el VAPID key es correcto
- Verifica que el usuario ha dado permiso para notificaciones

## Recursos Adicionales

- [Documentación de Firebase](https://firebase.google.com/docs)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

## Costos Estimados

### Capa Gratuita (Spark Plan)

- **Firestore**:
  - 50,000 lecturas/día
  - 20,000 escrituras/día
  - 20,000 eliminaciones/día
  - 1 GB almacenamiento

- **Cloud Messaging**:
  - Ilimitado (gratis)

- **Storage**:
  - 5 GB almacenamiento
  - 1 GB descarga/día

### Capa de Pago (Blaze Plan)

Si superas los límites gratuitos:
- Lecturas: $0.06 por 100,000 documentos
- Escrituras: $0.18 por 100,000 documentos
- Eliminaciones: $0.02 por 100,000 documentos
- Almacenamiento: $0.18/GB/mes

**Estimación para 1000 usuarios activos**: $25-50/mes

## Próximos Pasos

Una vez completada la configuración de Firebase:

1. Ejecuta las migraciones de Django para crear los modelos de imágenes
2. Configura Google Cloud Vision AI
3. Inicia el worker de Celery
4. Prueba el envío de mensajes de chat
5. Prueba las notificaciones push

¡Firebase está listo para usar! 🚀
