# Firebase Authentication - Próximos Pasos

## 🚀 Guía Rápida de Configuración

Esta guía te llevará paso a paso para completar la configuración de Firebase Authentication y migrar tus usuarios existentes.

---

## Paso 1: Obtener Credenciales Web de Firebase

### 1.1 Acceder a Firebase Console

1. Ve a https://console.firebase.google.com/
2. Inicia sesión con tu cuenta de Google
3. Selecciona el proyecto **cmms-somacor-prod**

### 1.2 Obtener Credenciales

1. Haz clic en el ícono de engranaje ⚙️ (junto a "Project Overview")
2. Selecciona **"Project settings"**
3. Desplázate hasta **"Your apps"**
4. Si no hay una app web, haz clic en el ícono `</>` para agregar una:
   - Nombre: `CMMS Frontend`
   - Marca "Also set up Firebase Hosting" (opcional)
   - Haz clic en "Register app"

5. Copia las credenciales que aparecen:

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

### 1.3 Actualizar .env del Frontend

Abre `frontend/.env` y actualiza con tus credenciales:

```env
VITE_API_URL=https://cmms-backend-888881509782.us-central1.run.app/api/v1

# Firebase Configuration
VITE_FIREBASE_API_KEY=AIza...  # Tu API Key
VITE_FIREBASE_AUTH_DOMAIN=cmms-somacor-prod.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=cmms-somacor-prod
VITE_FIREBASE_STORAGE_BUCKET=cmms-somacor-prod.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789  # Tu Sender ID
VITE_FIREBASE_APP_ID=1:123456789:web:abc123  # Tu App ID
```

---

## Paso 2: Configurar Firebase Authentication

### 2.1 Habilitar Email/Password Authentication

1. En Firebase Console, ve a **"Authentication"** en el menú lateral
2. Haz clic en la pestaña **"Sign-in method"**
3. Busca **"Email/Password"** y haz clic en él
4. Habilita el toggle
5. Haz clic en **"Save"**

### 2.2 Configurar Dominios Autorizados

1. En "Authentication", ve a **"Settings"**
2. Desplázate hasta **"Authorized domains"**
3. Agrega los siguientes dominios:
   - `localhost` (para desarrollo)
   - Tu dominio de producción (ej: `cmms.somacor.com`)
   - Tu dominio de Firebase Hosting (si aplica)

### 2.3 Personalizar Email Templates (Opcional pero Recomendado)

1. En "Authentication", ve a **"Templates"**
2. Personaliza las plantillas para:
   - **Password reset** (Recuperación de contraseña)
   - **Email address verification** (Verificación de email)
   - **Email address change** (Cambio de email)

Ejemplo de personalización:
```
Asunto: Restablece tu contraseña de CMMS Somacor

Hola,

Recibimos una solicitud para restablecer tu contraseña en CMMS Somacor.

Haz clic en el siguiente enlace para crear una nueva contraseña:
%LINK%

Si no solicitaste este cambio, ignora este correo.

Saludos,
Equipo CMMS Somacor
```

---

## Paso 3: Probar la Configuración

### 3.1 Iniciar el Frontend

```bash
cd frontend
npm install  # Si es necesario
npm run dev
```

### 3.2 Verificar en el Navegador

1. Abre http://localhost:5173
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña "Console"
4. No deberías ver errores de Firebase
5. Deberías ver: "Firebase initialized successfully" (o similar)

### 3.3 Crear un Usuario de Prueba

Opción A - Desde Firebase Console:
1. Ve a Authentication > Users
2. Haz clic en "Add user"
3. Ingresa email y contraseña
4. Haz clic en "Add user"

Opción B - Desde Django:
```bash
cd backend
python manage.py shell

from apps.authentication.models import User, Role
role = Role.objects.get(name='ADMIN')
user = User.objects.create_user(
    email='test@example.com',
    password='TestPassword123!',
    first_name='Test',
    last_name='User',
    rut='12345678-9',
    role=role
)
```

### 3.4 Probar Login

1. Ve a la página de login del frontend
2. Ingresa las credenciales del usuario de prueba
3. Deberías poder iniciar sesión exitosamente
4. Verifica en las herramientas de desarrollador:
   - Network tab: Las peticiones deben incluir `Authorization: Bearer <token>`
   - Application tab > Local Storage: Debe haber un `firebaseToken`

---

## Paso 4: Migrar Usuarios Existentes

### 4.1 Backup de la Base de Datos

**¡IMPORTANTE!** Siempre haz un backup antes de migrar:

```bash
# SQLite
cp backend/db.sqlite3 backend/db.sqlite3.backup

# PostgreSQL
pg_dump -U usuario -d nombre_db > backup_$(date +%Y%m%d).sql
```

### 4.2 Ejecutar Migración en Modo Dry-Run

Primero, ejecuta en modo prueba para ver qué pasará:

```bash
cd backend
python manage.py migrate_users_to_firebase --dry-run
```

Revisa la salida. Deberías ver:
- Número de usuarios a migrar
- Lista de usuarios que se migrarán
- Sin errores

### 4.3 Ejecutar Migración Real

Si todo se ve bien, ejecuta la migración real:

```bash
python manage.py migrate_users_to_firebase
```

El comando te pedirá confirmación. Escribe `yes` y presiona Enter.

Verás:
- Progreso de la migración
- ✓ para usuarios migrados exitosamente
- ✗ para usuarios con errores
- Resumen final

### 4.4 Revisar el Reporte

La migración genera dos archivos en `backend/migration_reports/`:

1. **firebase_migration_YYYYMMDD_HHMMSS.json**
   - Reporte completo en formato JSON
   - Lista de usuarios exitosos y fallidos

2. **temp_passwords_YYYYMMDD_HHMMSS.txt**
   - Contraseñas temporales generadas
   - **¡ELIMINAR DESPUÉS DE ENVIAR EMAILS!**

### 4.5 Verificar en Firebase Console

1. Ve a Firebase Console > Authentication > Users
2. Deberías ver todos los usuarios migrados
3. Verifica que los emails sean correctos

---

## Paso 5: Enviar Emails de Recuperación de Contraseña

### 5.1 Enviar a un Usuario de Prueba

Primero, prueba con un solo usuario:

```bash
python manage.py send_migration_emails --email=test@example.com
```

Verifica que el email llegue correctamente.

### 5.2 Enviar a Todos los Usuarios

Si el email de prueba funcionó, envía a todos:

```bash
python manage.py send_migration_emails
```

El comando te pedirá confirmación. Escribe `yes` y presiona Enter.

### 5.3 Monitorear el Envío

El comando mostrará:
- Progreso del envío
- ✓ para emails enviados exitosamente
- ✗ para emails con errores
- Resumen final

### 5.4 Eliminar Contraseñas Temporales

**¡IMPORTANTE!** Una vez enviados los emails, elimina el archivo de contraseñas:

```bash
rm backend/migration_reports/temp_passwords_*.txt
```

---

## Paso 6: Comunicar a los Usuarios

### 6.1 Preparar Comunicación

Envía un email o mensaje a todos los usuarios informando:

```
Asunto: Actualización del Sistema CMMS - Nueva Forma de Acceso

Estimado usuario,

Hemos actualizado nuestro sistema de autenticación para mejorar la seguridad.

ACCIÓN REQUERIDA:
1. Revisa tu correo electrónico
2. Busca un email de "Firebase" o "CMMS Somacor"
3. Haz clic en el enlace para restablecer tu contraseña
4. Crea una nueva contraseña segura

IMPORTANTE:
- Tu usuario sigue siendo el mismo (tu email)
- Debes crear una nueva contraseña
- El enlace expira en 24 horas

Si tienes problemas, contacta a soporte.

Saludos,
Equipo CMMS
```

### 6.2 Preparar Soporte

Asegúrate de que el equipo de soporte esté listo para:
- Ayudar con problemas de login
- Reenviar emails de recuperación
- Resolver problemas de contraseñas

---

## Paso 7: Monitoreo Post-Migración

### 7.1 Monitorear Firebase Console

Durante los primeros días, revisa:
- Authentication > Users: Usuarios activos
- Authentication > Sign-in method: Intentos de login
- Busca patrones de errores

### 7.2 Monitorear Logs de Django

```bash
cd backend
tail -f logs/django.log
```

Busca:
- Errores de autenticación
- Problemas de sincronización
- Errores de Firebase

### 7.3 Métricas Clave

Monitorea:
- Tasa de éxito de login
- Usuarios que restablecieron contraseña
- Errores de autenticación
- Tiempo de respuesta de API

---

## 🆘 Solución de Problemas Comunes

### Problema: "Firebase: Error (auth/invalid-api-key)"

**Solución:**
1. Verifica que el API Key en `frontend/.env` sea correcto
2. Asegúrate de que no haya espacios extra
3. Reinicia el servidor de desarrollo

### Problema: "Firebase: Error (auth/unauthorized-domain)"

**Solución:**
1. Ve a Firebase Console > Authentication > Settings
2. Agrega tu dominio a "Authorized domains"
3. Espera unos minutos para que se propague

### Problema: Usuario no puede iniciar sesión

**Solución:**
1. Verifica que el usuario exista en Firebase Console
2. Verifica que el usuario tenga `firebase_uid` en Django
3. Verifica que el usuario esté activo (`is_active=True`)
4. Intenta restablecer la contraseña

### Problema: Email de recuperación no llega

**Solución:**
1. Verifica la carpeta de spam
2. Verifica que el email esté correcto en Firebase Console
3. Verifica las plantillas de email en Firebase Console
4. Intenta reenviar el email:
   ```bash
   python manage.py send_migration_emails --email=usuario@example.com
   ```

### Problema: Error al migrar usuarios

**Solución:**
1. Revisa el reporte de migración en `backend/migration_reports/`
2. Verifica los logs de Django
3. Verifica que Firebase Admin SDK esté configurado correctamente
4. Intenta migrar usuarios individualmente

---

## ✅ Checklist Final

Antes de considerar la migración completa, verifica:

- [ ] Credenciales web de Firebase configuradas en `frontend/.env`
- [ ] Email/Password authentication habilitado en Firebase Console
- [ ] Dominios autorizados configurados
- [ ] Email templates personalizados (opcional)
- [ ] Frontend funciona correctamente con Firebase
- [ ] Usuario de prueba puede iniciar sesión
- [ ] Backup de base de datos realizado
- [ ] Migración de usuarios completada exitosamente
- [ ] Emails de recuperación enviados
- [ ] Archivo de contraseñas temporales eliminado
- [ ] Usuarios notificados del cambio
- [ ] Equipo de soporte preparado
- [ ] Monitoreo activo de logs y métricas

---

## 📞 Soporte

Si encuentras problemas que no puedes resolver:

1. Revisa la documentación:
   - `FIREBASE_AUTHENTICATION_IMPLEMENTATION_SUMMARY.md`
   - `FIREBASE_WEB_CREDENTIALS_SETUP.md`

2. Revisa los logs:
   - Django: `backend/logs/django.log`
   - Firebase Console: Authentication > Usage

3. Ejecuta los tests:
   ```bash
   cd backend
   python test_firebase_user_sync.py
   ```

---

**¡Éxito con la migración!** 🎉

Una vez completados estos pasos, tu sistema CMMS estará completamente integrado con Firebase Authentication, proporcionando una autenticación más segura y escalable.
