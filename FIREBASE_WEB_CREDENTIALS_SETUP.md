# Firebase Web Credentials Setup

## Obtener Credenciales de Firebase para el Frontend

Para completar la configuración de Firebase Authentication en el frontend, necesitas obtener las credenciales web de tu proyecto Firebase.

### Pasos para Obtener las Credenciales:

1. **Ir a la Consola de Firebase**
   - Visita: https://console.firebase.google.com/
   - Selecciona tu proyecto: `cmms-somacor-prod`

2. **Navegar a Configuración del Proyecto**
   - Haz clic en el ícono de engranaje ⚙️ junto a "Project Overview"
   - Selecciona "Project settings" (Configuración del proyecto)

3. **Ir a la Sección de Apps**
   - Desplázate hacia abajo hasta la sección "Your apps" (Tus aplicaciones)
   - Si no tienes una app web registrada, haz clic en el ícono `</>` para agregar una

4. **Registrar una App Web (si es necesario)**
   - Nombre de la app: `CMMS Frontend`
   - Marca la casilla "Also set up Firebase Hosting" si planeas usar Firebase Hosting
   - Haz clic en "Register app"

5. **Copiar las Credenciales**
   - Verás un objeto de configuración similar a este:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIza...",
     authDomain: "cmms-somacor-prod.firebaseapp.com",
     projectId: "cmms-somacor-prod",
     storageBucket: "cmms-somacor-prod.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123"
   };
   ```

6. **Actualizar el Archivo .env del Frontend**
   - Abre el archivo `frontend/.env`
   - Reemplaza los valores placeholder con tus credenciales reales:
   ```env
   VITE_API_URL=https://cmms-backend-888881509782.us-central1.run.app/api/v1

   # Firebase Configuration
   VITE_FIREBASE_API_KEY=AIza...
   VITE_FIREBASE_AUTH_DOMAIN=cmms-somacor-prod.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=cmms-somacor-prod
   VITE_FIREBASE_STORAGE_BUCKET=cmms-somacor-prod.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
   VITE_FIREBASE_APP_ID=1:123456789:web:abc123
   ```

7. **Actualizar el Archivo .env.production (si existe)**
   - Repite el mismo proceso para `frontend/.env.production`

### Verificar la Configuración

Después de actualizar las credenciales:

1. **Reiniciar el servidor de desarrollo**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Verificar en la consola del navegador**
   - Abre las herramientas de desarrollador (F12)
   - No deberías ver errores relacionados con Firebase
   - Firebase debería inicializarse correctamente

3. **Probar el login**
   - Intenta iniciar sesión con un usuario existente
   - El token de Firebase debería aparecer en las peticiones HTTP

### Configuración Adicional en Firebase Console

#### Habilitar Email/Password Authentication:

1. En la consola de Firebase, ve a "Authentication" en el menú lateral
2. Haz clic en la pestaña "Sign-in method"
3. Habilita "Email/Password"
4. Guarda los cambios

#### Configurar Dominios Autorizados:

1. En "Authentication" > "Settings" > "Authorized domains"
2. Agrega tus dominios:
   - `localhost` (para desarrollo)
   - Tu dominio de producción (ej: `cmms.somacor.com`)
   - Tu dominio de Firebase Hosting (si aplica)

#### Configurar Email Templates (Opcional):

1. En "Authentication" > "Templates"
2. Personaliza las plantillas de email para:
   - Verificación de email
   - Recuperación de contraseña
   - Cambio de email

### Solución de Problemas

#### Error: "Firebase: Error (auth/invalid-api-key)"
- Verifica que el API Key sea correcto
- Asegúrate de que no haya espacios extra en el .env

#### Error: "Firebase: Error (auth/unauthorized-domain)"
- Agrega tu dominio a la lista de dominios autorizados en Firebase Console

#### Error: "Firebase: Error (auth/network-request-failed)"
- Verifica tu conexión a internet
- Verifica que el proyecto Firebase esté activo

### Recursos Adicionales

- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [Firebase Web Setup Guide](https://firebase.google.com/docs/web/setup)
- [Firebase Console](https://console.firebase.google.com/)

## Estado Actual

✅ Backend configurado con Firebase Admin SDK
✅ Frontend configurado con Firebase Authentication
✅ Interceptores de API actualizados para usar tokens de Firebase
⏳ Pendiente: Actualizar credenciales web en .env

Una vez que actualices las credenciales, el sistema estará completamente funcional con Firebase Authentication.
