# 🔐 Instrucciones para Crear Usuario Admin

## Problema

No puedes iniciar sesión porque no hay usuarios en la base de datos.

---

## ✅ Solución Rápida - Usar el Endpoint de Setup

### Paso 1: Llamar al Endpoint

Usa este comando en PowerShell:

```powershell
Invoke-RestMethod -Uri "https://cmms-backend-232652686658.us-central1.run.app/api/v1/auth/setup/create-admin/" -Method Post -Body (@{secret_key="CMMS2025Setup"} | ConvertTo-Json) -ContentType "application/json"
```

O usa curl:

```bash
curl -X POST https://cmms-backend-232652686658.us-central1.run.app/api/v1/auth/setup/create-admin/ \
  -H "Content-Type: application/json" \
  -d '{"secret_key":"CMMS2025Setup"}'
```

O usa Postman/Insomnia:
- **URL:** `https://cmms-backend-232652686658.us-central1.run.app/api/v1/auth/setup/create-admin/`
- **Method:** POST
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "secret_key": "CMMS2025Setup"
}
```

### Paso 2: Iniciar Sesión

Ve a: https://cmms-somacor-prod.web.app

**Credenciales:**
- **Email:** admin@cmms.com
- **Password:** admin123

---

## 🔧 Alternativa - Usar el Admin de Django

### Opción 1: Acceder al Admin de Django

1. Ve a: https://cmms-backend-232652686658.us-central1.run.app/admin/

2. Si no tienes credenciales, necesitas crear un superusuario primero (ver opciones abajo)

### Opción 2: Crear Superusuario desde Cloud Console

1. Ve a [Cloud Run Console](https://console.cloud.google.com/run/detail/us-central1/cmms-backend?project=argon-edge-478500-i8)

2. Click en la pestaña "LOGS"

3. Abre Cloud Shell (icono >_ en la parte superior)

4. Ejecuta:
```bash
gcloud run services proxy cmms-backend --region us-central1 --project argon-edge-478500-i8
```

5. En otra terminal de Cloud Shell, ejecuta:
```bash
# Conectarse al contenedor
gcloud run services exec cmms-backend \
  --region us-central1 \
  --project argon-edge-478500-i8 \
  -- python manage.py createsuperuser
```

6. Sigue las instrucciones para crear el superusuario

---

## 📝 Credenciales por Defecto

Si el endpoint de setup funciona, se creará:

| Campo | Valor |
|-------|-------|
| **Email** | admin@cmms.com |
| **Password** | admin123 |
| **Nombre** | Admin |
| **Apellido** | Sistema |
| **Rol** | ADMIN |

---

## ⚠️ Importante

1. **Cambia la contraseña inmediatamente** después del primer inicio de sesión
2. El endpoint de setup solo funciona si NO existe ningún usuario admin
3. El endpoint requiere la clave secreta `CMMS2025Setup`

---

## 🔍 Verificar que Funcionó

1. Ve a: https://cmms-somacor-prod.web.app
2. Ingresa: admin@cmms.com / admin123
3. Deberías ver el dashboard

---

## 🆘 Si Nada Funciona

Contacta al equipo de desarrollo con:
- Captura de pantalla del error
- Logs del navegador (F12 → Console)
- URL que estás intentando acceder

---

## 📞 Soporte

- **Email:** matilqsabe@gmail.com
- **GitHub:** https://github.com/matiasmoralesa/cmms-sistema-mantenimiento

---

**Última actualización:** 18 de Noviembre, 2024
