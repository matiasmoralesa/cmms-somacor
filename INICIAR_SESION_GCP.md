# 🔐 Iniciar Sesión en Google Cloud Platform

**Project ID**: `argon-edge-478500-i8`

---

## ⚠️ IMPORTANTE: Abrir Nueva Terminal

El SDK está instalado pero esta terminal no lo reconoce. Necesitas:

1. **Cerrar esta terminal PowerShell**
2. **Abrir una NUEVA terminal PowerShell**
3. **Seguir los pasos de abajo**

---

## 📋 Pasos para Iniciar Sesión

### Paso 1: Verificar Instalación
```powershell
# En la NUEVA terminal, verificar que gcloud funcione
gcloud --version

# Deberías ver algo como:
# Google Cloud SDK 456.0.0
# bq 2.0.99
# core 2023.11.10
```

### Paso 2: Iniciar Sesión
```powershell
# Este comando abrirá tu navegador
gcloud auth login

# Se abrirá tu navegador automáticamente
# 1. Selecciona tu cuenta de Google (la que usaste para GCP)
# 2. Haz clic en "Permitir"
# 3. Verás "You are now authenticated with the gcloud CLI!"
# 4. Puedes cerrar la ventana del navegador
```

### Paso 3: Configurar Proyecto
```powershell
# Configurar tu proyecto
gcloud config set project argon-edge-478500-i8

# Deberías ver:
# Updated property [core/project].
```

### Paso 4: Configurar Región
```powershell
# Configurar región predeterminada
gcloud config set compute/region us-central1

# Deberías ver:
# Updated property [compute/region].
```

### Paso 5: Verificar Configuración
```powershell
# Ver configuración actual
gcloud config list

# Deberías ver:
# [compute]
# region = us-central1
# [core]
# account = tu-email@gmail.com
# project = argon-edge-478500-i8
```

---

## ✅ Verificación Rápida

```powershell
# Verificar que todo esté bien
gcloud projects describe argon-edge-478500-i8

# Deberías ver información de tu proyecto
```

---

## 🚀 Después de Iniciar Sesión

Una vez que hayas iniciado sesión y configurado el proyecto, ejecuta:

```powershell
# Navegar al directorio del proyecto
cd "C:\Users\elect.DESKTOP-S2LKP0V\OneDrive\Escritorio\proyecto v2"

# Habilitar APIs necesarias
gcloud services enable sqladmin.googleapis.com run.googleapis.com cloudbuild.googleapis.com storage-api.googleapis.com pubsub.googleapis.com --project=argon-edge-478500-i8

# Desplegar el sistema
cd deployment\gcp
.\deploy-windows.ps1 -ProjectId "argon-edge-478500-i8"
```

---

## 🆘 Si gcloud Sigue Sin Funcionar

### Opción 1: Agregar al PATH Manualmente
```powershell
# Agregar Google Cloud SDK al PATH de esta sesión
$env:Path += ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"

# Verificar
gcloud --version
```

### Opción 2: Usar Ruta Completa
```powershell
# Usar ruta completa al ejecutar gcloud
& "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" --version
```

### Opción 3: Reinstalar SDK
Si nada funciona, reinstala el SDK:
1. Ir a: https://cloud.google.com/sdk/docs/install#windows
2. Descargar `GoogleCloudSDKInstaller.exe`
3. Ejecutar instalador
4. Marcar "Run 'gcloud init'" al finalizar
5. Cerrar TODAS las terminales
6. Abrir nueva terminal PowerShell

---

## 📝 Resumen de Comandos

```powershell
# 1. Cerrar esta terminal y abrir NUEVA terminal PowerShell

# 2. En la nueva terminal:
gcloud auth login
gcloud config set project argon-edge-478500-i8
gcloud config set compute/region us-central1
gcloud config list

# 3. Habilitar APIs
gcloud services enable sqladmin.googleapis.com run.googleapis.com cloudbuild.googleapis.com storage-api.googleapis.com pubsub.googleapis.com

# 4. Desplegar
cd "C:\Users\elect.DESKTOP-S2LKP0V\OneDrive\Escritorio\proyecto v2\deployment\gcp"
.\deploy-windows.ps1 -ProjectId "argon-edge-478500-i8"
```

---

## ✅ Checklist

- [ ] Cerrar terminal actual
- [ ] Abrir NUEVA terminal PowerShell
- [ ] Ejecutar `gcloud --version` (debe funcionar)
- [ ] Ejecutar `gcloud auth login`
- [ ] Configurar proyecto: `gcloud config set project argon-edge-478500-i8`
- [ ] Configurar región: `gcloud config set compute/region us-central1`
- [ ] Verificar: `gcloud config list`
- [ ] Habilitar APIs
- [ ] Ejecutar despliegue

---

**Próximo paso**: Cierra esta terminal, abre una nueva, y ejecuta los comandos de arriba.

🚀 **¡Casi listo para desplegar!**
