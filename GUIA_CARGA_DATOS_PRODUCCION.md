# 📊 Guía para Cargar Datos en Producción

## 🎯 Objetivo

Esta guía te ayudará a poblar la base de datos de producción con datos de ejemplo completos para el sistema CMMS.

---

## 📋 Datos que se Cargarán

### 👥 Usuarios y Roles
- **3 Roles:** ADMIN, SUPERVISOR, OPERADOR
- **9 Usuarios:**
  - 2 Administradores
  - 2 Supervisores
  - 5 Operadores (con licencias)

### 📍 Ubicaciones
- 5 Ubicaciones físicas para los activos

### 🚜 Activos (15 vehículos)
- 3 Camiones Supersucker
- 3 Camionetas MDO
- 3 Retroexcavadoras MDO
- 3 Cargadores Frontales MDO
- 3 Minicargadores MDO

### 🔧 Inventario
- 27 Repuestos diferentes
- Movimientos de entrada y salida
- Alertas de stock bajo

### 📝 Operaciones
- 75-225 Órdenes de trabajo (históricas y activas)
- Planes de mantenimiento preventivo
- 5 Plantillas de checklist (una por tipo de vehículo)

### 📊 Estados de Máquinas
- Historial de estados por activo
- Registros de odómetro
- Niveles de combustible
- Notas de condición

---

## 🚀 Método 1: Script Automático (Recomendado)

### Paso 1: Abrir PowerShell en el directorio backend

```powershell
cd backend
```

### Paso 2: Ejecutar el script maestro

```powershell
.\CARGAR_TODO_PRODUCCION.ps1
```

### Paso 3: Confirmar la operación

Cuando se te solicite, escribe `SI` y presiona Enter.

### Paso 4: Esperar a que termine

El proceso tomará aproximadamente 2-5 minutos dependiendo de la conexión.

---

## 🔧 Método 2: Paso a Paso Manual

Si prefieres ejecutar cada paso manualmente:

### 1. Configurar variables de entorno

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.production"
$env:DATABASE_URL = "postgresql://cmms_user:Somacor2024!@34.31.236.19:5432/cmms_prod"
```

### 2. Cargar datos base

```powershell
python populate_data.py
```

Este script carga:
- Roles y usuarios
- Ubicaciones
- Activos
- Repuestos
- Órdenes de trabajo
- Planes de mantenimiento
- Plantillas de checklist

### 3. Agregar estados de máquinas

```powershell
python agregar_machine_status.py
```

Este script agrega:
- Historial de estados por activo
- Registros de odómetro y combustible

---

## ✅ Verificación

Después de cargar los datos, verifica que todo esté correcto:

### Opción 1: Desde PowerShell

```powershell
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()
from django.contrib.auth import get_user_model
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
print('Usuarios:', get_user_model().objects.count())
print('Activos:', Asset.objects.count())
print('Órdenes:', WorkOrder.objects.count())
"
```

### Opción 2: Desde la aplicación web

1. Accede a la aplicación
2. Inicia sesión con: `admin@cmms.com` / `admin123`
3. Verifica que veas:
   - Activos en el dashboard
   - Órdenes de trabajo
   - Reportes con datos

---

## 🔑 Credenciales de Acceso

### Administrador
- **Email:** admin@cmms.com
- **Password:** admin123
- **Permisos:** Acceso completo al sistema

### Supervisor
- **Email:** carlos.rodriguez@somacor.com
- **Password:** password123
- **Permisos:** Gestión de operaciones y reportes

### Operador
- **Email:** juan.perez@somacor.com
- **Password:** password123
- **Permisos:** Actualización de estados y órdenes asignadas

---

## 📊 Datos Generados

### Estadísticas Esperadas

| Categoría | Cantidad |
|-----------|----------|
| Usuarios | 9 |
| Ubicaciones | 5 |
| Activos | 15 |
| Repuestos | 27 |
| Órdenes de Trabajo | 75-225 |
| Planes de Mantenimiento | 30-60 |
| Estados de Máquinas | 45-120 |
| Movimientos de Inventario | 100-200 |

---

## ⚠️ Advertencias

### Antes de Ejecutar

1. **Backup:** Asegúrate de tener un backup de la base de datos si ya tiene datos
2. **Conexión:** Verifica que tengas conexión a Cloud SQL
3. **Permisos:** Asegúrate de tener permisos de escritura en la base de datos

### Durante la Ejecución

- No interrumpas el proceso
- No cierres la ventana de PowerShell
- Espera a que termine completamente

### Después de Ejecutar

- Los datos son de ejemplo y pueden ser modificados
- Las contraseñas son genéricas, cámbialas en producción real
- Revisa que todos los datos se hayan cargado correctamente

---

## 🔄 Recargar Datos

Si necesitas recargar los datos:

### Opción 1: Limpiar y recargar

```powershell
# Limpiar base de datos (¡CUIDADO!)
python manage.py flush --no-input

# Ejecutar migraciones
python manage.py migrate

# Cargar datos nuevamente
.\CARGAR_TODO_PRODUCCION.ps1
```

### Opción 2: Solo agregar datos faltantes

Los scripts verifican si los datos ya existen antes de crearlos, por lo que puedes ejecutarlos múltiples veces sin duplicar datos.

---

## 🐛 Solución de Problemas

### Error: "No se puede conectar a la base de datos"

**Solución:**
1. Verifica que Cloud SQL esté activo
2. Verifica las credenciales en `DATABASE_URL`
3. Verifica que tu IP esté autorizada en Cloud SQL

### Error: "Module not found"

**Solución:**
```powershell
pip install -r requirements.txt
```

### Error: "Permission denied"

**Solución:**
1. Verifica que el usuario `cmms_user` tenga permisos de escritura
2. Verifica que estés usando las credenciales correctas

### Los datos no aparecen en la aplicación

**Solución:**
1. Verifica que estés conectado a la base de datos correcta
2. Limpia la caché del navegador
3. Verifica los logs del backend

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs en la consola
2. Verifica la conexión a Cloud SQL
3. Consulta la documentación del proyecto
4. Contacta al equipo de desarrollo

---

## ✨ Próximos Pasos

Después de cargar los datos:

1. **Explora el sistema:**
   - Dashboard principal
   - Lista de activos
   - Órdenes de trabajo
   - Reportes y KPIs

2. **Prueba funcionalidades:**
   - Crear nuevas órdenes de trabajo
   - Actualizar estados de máquinas
   - Generar reportes
   - Usar el bot de Telegram (si está configurado)

3. **Personaliza:**
   - Cambia las contraseñas
   - Agrega más usuarios
   - Configura notificaciones
   - Ajusta los planes de mantenimiento

---

## 📝 Notas Finales

- Los datos son realistas pero ficticios
- Las fechas son relativas a la fecha de ejecución
- Los números de serie y placas son generados aleatoriamente
- Los costos y precios son aproximados

**¡Disfruta explorando el sistema CMMS!** 🎉
