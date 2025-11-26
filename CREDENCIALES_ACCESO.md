# 🔐 Credenciales de Acceso - CMMS Somacor

## URLs del Sistema

### Frontend (Aplicación Web)
**URL**: https://cmms-somacor-prod.web.app

### Backend API
**URL**: https://cmms-backend-service-888881509782.us-central1.run.app

### Firebase Console
**URL**: https://console.firebase.google.com/project/cmms-somacor-prod

### Google Cloud Console
**URL**: https://console.cloud.google.com/run?project=cmms-somacorv2

---

## 👥 Usuarios de Prueba

### 1. Administrador
- **Email**: admin@somacor.cl
- **Contraseña**: Admin123!
- **Rol**: ADMIN
- **Firebase UID**: yD9roANaOITWAysyczjmBgMls5f1
- **Permisos**: Acceso completo al sistema

### 2. Supervisor
- **Email**: supervisor@somacor.cl
- **Contraseña**: Super123!
- **Rol**: SUPERVISOR
- **Firebase UID**: WQisFpxLYGhpYzZS70H4qvDBUq32
- **Permisos**: Gestión de mantenimiento y equipos

### 3. Operador
- **Email**: operador@somacor.cl
- **Contraseña**: Opera123!
- **Rol**: OPERADOR
- **Firebase UID**: a0EA2lWbEwXEnItTOFDUvYwX9Tm2
- **Permisos**: Operación básica del sistema

---

## 🚀 Cómo Iniciar Sesión

1. Abre el navegador y ve a: https://cmms-somacor-prod.web.app
2. Ingresa el email y contraseña de uno de los usuarios de prueba
3. Haz clic en "Iniciar Sesión"
4. El sistema te redirigirá al dashboard

---

## 🔄 Sincronización Automática

Los usuarios creados en Firebase se sincronizarán automáticamente con la base de datos Django cuando:
- Inicien sesión por primera vez en el frontend
- El backend recibirá el token de Firebase
- Se creará automáticamente el registro en Django
- Se asignarán los permisos correspondientes según el rol

---

## 🛠️ Gestión de Usuarios

### Crear Nuevos Usuarios

#### Opción 1: Firebase Console (Recomendado)
1. Ve a: https://console.firebase.google.com/project/cmms-somacor-prod
2. Navega a Authentication > Users
3. Haz clic en "Add user"
4. Ingresa email y contraseña
5. El usuario se sincronizará automáticamente al iniciar sesión

#### Opción 2: Script Python
```bash
python create_firebase_users_only.py
```

### Restablecer Contraseñas

#### Desde el Frontend
1. En la página de login, haz clic en "¿Olvidaste tu contraseña?"
2. Ingresa el email del usuario
3. Se enviará un email con el link de restablecimiento

#### Desde Firebase Console
1. Ve a Authentication > Users
2. Busca el usuario
3. Haz clic en los tres puntos (⋮)
4. Selecciona "Reset password"
5. Se enviará un email al usuario

### Eliminar Usuarios

#### Desde Firebase Console
1. Ve a Authentication > Users
2. Busca el usuario
3. Haz clic en los tres puntos (⋮)
4. Selecciona "Delete account"

---

## 🔒 Seguridad

### Cambiar Contraseñas en Producción
**IMPORTANTE**: Las contraseñas de prueba deben cambiarse antes de usar el sistema en producción.

Para cambiar una contraseña:
1. Inicia sesión con el usuario
2. Ve a Perfil > Cambiar Contraseña
3. Ingresa la contraseña actual y la nueva
4. Guarda los cambios

### Roles y Permisos

#### ADMIN
- Gestión completa de usuarios
- Configuración del sistema
- Acceso a todos los módulos
- Reportes y estadísticas

#### SUPERVISOR
- Gestión de órdenes de trabajo
- Asignación de tareas
- Supervisión de operadores
- Reportes de mantenimiento

#### OPERADOR
- Ejecución de órdenes de trabajo
- Registro de actividades
- Consulta de equipos
- Actualización de estados

---

## 📊 Monitoreo

### Ver Logs de Autenticación
```bash
# Logs del backend
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cmms-backend-service" --project=cmms-somacorv2 --limit=50

# Logs de Firebase
# Ve a Firebase Console > Authentication > Users
# Haz clic en un usuario para ver su historial
```

### Verificar Usuarios Activos
1. Firebase Console > Authentication > Users
2. Verás la lista de todos los usuarios registrados
3. Última fecha de inicio de sesión
4. Estado de verificación de email

---

## 🆘 Solución de Problemas

### No puedo iniciar sesión
1. Verifica que el email y contraseña sean correctos
2. Revisa que el usuario exista en Firebase Console
3. Verifica que el usuario esté habilitado (no deshabilitado)
4. Limpia el caché del navegador
5. Intenta en modo incógnito

### Error "Usuario no encontrado"
- El usuario no existe en Firebase
- Crea el usuario desde Firebase Console

### Error "Contraseña incorrecta"
- La contraseña es incorrecta
- Usa la opción "¿Olvidaste tu contraseña?" para restablecerla

### Error de conexión
- Verifica tu conexión a internet
- Verifica que el backend esté funcionando
- Revisa los logs en Cloud Console

---

## 📝 Notas Importantes

1. **Primera vez**: Los usuarios se sincronizan automáticamente con Django al primer login
2. **Custom Claims**: Los roles se almacenan como custom claims en Firebase
3. **Tokens**: Los tokens de Firebase se renuevan automáticamente
4. **Sesión**: La sesión permanece activa hasta que el usuario cierre sesión
5. **Seguridad**: Todas las comunicaciones usan HTTPS

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs en Cloud Console
2. Verifica la configuración en Firebase Console
3. Consulta la documentación en `.kiro/specs/firebase-authentication/`

---

**Fecha de Creación**: 25 de Noviembre de 2025
**Última Actualización**: 25 de Noviembre de 2025
**Estado**: ✅ Activo y Funcionando
