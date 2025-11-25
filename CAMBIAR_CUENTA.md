# 🔐 Cambiar a la Cuenta Correcta

## Problema Actual

Estás configurado con:
- **Cuenta:** electronightx@gmail.com ❌
- **Proyecto:** cmms-somacorv2 ✅

Necesitas:
- **Cuenta:** lucasgallardo497@gmail.com ✅
- **Proyecto:** cmms-somacorv2 ✅

---

## ✅ Solución: Cambiar de Cuenta

### Opción 1: Agregar Nueva Cuenta (Recomendado)

```powershell
# 1. Autenticar con la nueva cuenta
gcloud auth login

# Esto abrirá tu navegador
# Selecciona o ingresa: lucasgallardo497@gmail.com
```

### Opción 2: Cambiar Cuenta Activa (Si Ya Está Agregada)

```powershell
# Ver todas las cuentas disponibles
gcloud auth list

# Cambiar a la cuenta correcta
gcloud config set account lucasgallardo497@gmail.com
```

---

## 🔍 Verificar Configuración

Después de autenticarte, verifica:

```powershell
gcloud config list
```

Deberías ver:
```
[core]
account = lucasgallardo497@gmail.com
project = cmms-somacorv2
```

---

## 🚀 Continuar con el Despliegue

Una vez autenticado correctamente, ejecuta:

```powershell
# Habilitar APIs necesarias
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# Crear Cloud SQL (si no existe)
gcloud sql instances create cmms-db `
  --database-version=POSTGRES_15 `
  --tier=db-f1-micro `
  --region=us-central1 `
  --root-password=TuContraseñaSegura123

# Crear base de datos
gcloud sql databases create cmms_db --instance=cmms-db

# Crear usuario
gcloud sql users create cmms_user `
  --instance=cmms-db `
  --password=TuContraseñaUsuario123

# Desplegar backend
cd backend
.\deploy-nueva-cuenta.ps1
```

---

## ⚠️ Nota Importante

Si `lucasgallardo497@gmail.com` no tiene permisos en el proyecto `cmms-somacorv2`:

1. Ve a: https://console.cloud.google.com/iam-admin/iam?project=cmms-somacorv2
2. Agrega `lucasgallardo497@gmail.com` con rol **Owner** o **Editor**
3. Espera 1-2 minutos para que se propaguen los permisos
4. Intenta de nuevo

---

## 📞 ¿Necesitas Ayuda?

Si tienes problemas:
1. Verifica que el proyecto `cmms-somacorv2` existe
2. Verifica que tienes permisos en el proyecto
3. Asegúrate de estar autenticado con la cuenta correcta

```powershell
# Ver cuenta activa
gcloud config get-value account

# Ver proyecto activo
gcloud config get-value project
```
