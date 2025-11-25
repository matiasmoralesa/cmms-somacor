# 🚀 Cargar Datos en Producción desde Cloud Shell

## ⚠️ Problema Detectado

No se puede conectar directamente a Cloud SQL desde tu máquina local por seguridad.

**Solución:** Usar Cloud Shell de Google Cloud para ejecutar los scripts.

---

## 📋 Método 1: Usar Cloud Shell (Recomendado)

### Paso 1: Abrir Cloud Shell

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Haz clic en el ícono de Cloud Shell (terminal) en la esquina superior derecha
3. Espera a que se active

### Paso 2: Clonar el repositorio

```bash
# Si tienes el código en GitHub
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo/backend

# O subir los archivos manualmente
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno

```bash
export DJANGO_SETTINGS_MODULE="config.settings.production"
export DATABASE_URL="postgresql://cmms_user:Somacor2024!@34.31.236.19:5432/cmms_prod"
export DB_NAME="cmms_prod"
export DB_USER="cmms_user"
export DB_HOST="34.31.236.19"
export DB_PORT="5432"
```

### Paso 5: Ejecutar scripts

```bash
# Cargar datos base
python populate_data.py

# Cargar estados de máquinas
python agregar_machine_status.py
```

---

## 📋 Método 2: Usar Cloud SQL Proxy (Local)

Si prefieres ejecutar desde tu máquina local:

### Paso 1: Descargar Cloud SQL Proxy

Ya tienes `cloud_sql_proxy.exe` en tu proyecto.

### Paso 2: Iniciar el proxy

```powershell
# En una terminal PowerShell
.\cloud_sql_proxy.exe -instances=tu-proyecto:us-central1:cmms-db=tcp:5432
```

### Paso 3: En otra terminal, ejecutar scripts

```powershell
# Configurar para usar localhost
$env:DATABASE_URL = "postgresql://cmms_user:Somacor2024!@localhost:5432/cmms_prod"

# Ejecutar scripts
python populate_data.py
python agregar_machine_status.py
```

---

## 📋 Método 3: Ejecutar desde Cloud Run Job

### Crear un Cloud Run Job

```bash
# Crear job para cargar datos
gcloud run jobs create cargar-datos \
  --image gcr.io/tu-proyecto/cmms-backend \
  --region us-central1 \
  --set-env-vars DATABASE_URL="postgresql://cmms_user:Somacor2024!@34.31.236.19:5432/cmms_prod" \
  --command python \
  --args populate_data.py

# Ejecutar el job
gcloud run jobs execute cargar-datos --region us-central1
```

---

## ✅ Verificar que los datos se cargaron

### Desde Cloud Shell o local (con proxy):

```bash
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder

User = get_user_model()

print('Usuarios:', User.objects.count())
print('Activos:', Asset.objects.count())
print('Ordenes:', WorkOrder.objects.count())
"
```

### Desde la aplicación web:

1. Ve a tu aplicación: https://tu-app.web.app
2. Inicia sesión con: `admin@cmms.com` / `admin123`
3. Verifica que veas datos en el dashboard

---

## 🔧 Script Simplificado para Cloud Shell

Crea un archivo `cargar_todo.sh`:

```bash
#!/bin/bash

echo "=========================================="
echo "CARGANDO DATOS EN PRODUCCION"
echo "=========================================="

# Configurar variables
export DJANGO_SETTINGS_MODULE="config.settings.production"
export DATABASE_URL="postgresql://cmms_user:Somacor2024!@34.31.236.19:5432/cmms_prod"

# Cargar datos
echo "Cargando datos base..."
python populate_data.py

if [ $? -eq 0 ]; then
    echo "✓ Datos base cargados"
    
    echo "Cargando estados de maquinas..."
    python agregar_machine_status.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Estados cargados"
    fi
fi

echo ""
echo "=========================================="
echo "PROCESO COMPLETADO"
echo "=========================================="
echo "Usuario: admin@cmms.com"
echo "Password: admin123"
```

Ejecutar:

```bash
chmod +x cargar_todo.sh
./cargar_todo.sh
```

---

## 📊 Datos que se Cargarán

- ✅ 3 Roles (ADMIN, SUPERVISOR, OPERADOR)
- ✅ 9 Usuarios
- ✅ 5 Ubicaciones
- ✅ 15 Activos (5 tipos de vehículos)
- ✅ 27 Repuestos
- ✅ 75-225 Órdenes de trabajo
- ✅ Planes de mantenimiento
- ✅ Movimientos de inventario
- ✅ 5 Plantillas de checklist
- ✅ Estados de máquinas

---

## 🆘 Solución de Problemas

### Error: "timeout expired"

**Causa:** No se puede conectar a Cloud SQL desde tu IP

**Solución:** Usa Cloud Shell o Cloud SQL Proxy

### Error: "permission denied"

**Causa:** El usuario no tiene permisos

**Solución:** Verifica las credenciales en `DATABASE_URL`

### Error: "database does not exist"

**Causa:** La base de datos no existe

**Solución:**
```bash
# Crear la base de datos
gcloud sql databases create cmms_prod --instance=cmms-db
```

---

## 🎯 Recomendación

**Usa Cloud Shell** - Es la forma más rápida y segura de cargar datos en producción.

1. Abre Cloud Shell
2. Sube los archivos `populate_data.py` y `agregar_machine_status.py`
3. Ejecuta los scripts
4. Verifica en la aplicación web

¡Listo! 🎉
