# 📊 Qué Esperar Durante el Despliegue

**Proyecto**: argon-edge-478500-i8  
**Tiempo Total**: ~20-25 minutos

---

## 🎬 Proceso de Despliegue

### Inicio
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     Desplegando CMMS en Google Cloud Platform            ║
║     Proyecto: argon-edge-478500-i8                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Verificando configuración...
✓ Proyecto: argon-edge-478500-i8
✓ Cuenta: electronightx@gmail.com
```

---

## 📋 Fase 1: Habilitar APIs (3-5 minutos)

Verás mensajes como:
```
═══════════════════════════════════════════════════════════
Habilitando APIs necesarias (3-5 minutos)...
═══════════════════════════════════════════════════════════

Habilitando sqladmin.googleapis.com...
Operation "operations/acat.p2-..." finished successfully.
✓ sqladmin.googleapis.com habilitada

Habilitando run.googleapis.com...
Operation "operations/acat.p2-..." finished successfully.
✓ run.googleapis.com habilitada

... (continúa con más APIs)
```

**Qué está pasando**: Se están habilitando los servicios de GCP que necesita el sistema.

---

## 📋 Fase 2: Configurar Base de Datos

El script te pedirá:
```
═══════════════════════════════════════════════════════════
Configuración de Base de Datos
═══════════════════════════════════════════════════════════

Necesitas elegir una contraseña segura para la base de datos.
Ejemplo: CMMS2025!Secure

Ingresa contraseña para la base de datos: ********
```

**Qué hacer**: 
- Escribe una contraseña segura (mínimo 8 caracteres)
- Ejemplo: `CMMS2025!Secure` o `MiPassword123!`
- **IMPORTANTE**: Guarda esta contraseña, la necesitarás después

Luego verás:
```
═══════════════════════════════════════════════════════════
Iniciando Despliegue
═══════════════════════════════════════════════════════════

Esto tomará aproximadamente 20-25 minutos.
Puedes ver el progreso en tiempo real.

Presiona Enter para continuar...
```

**Qué hacer**: Presiona Enter para comenzar

---

## 📋 Fase 3: Crear Cloud SQL (8-10 minutos)

```
═══════════════════════════════════════════════════════════
Paso 1/5: Creando Cloud SQL (8-10 minutos)
═══════════════════════════════════════════════════════════

Verificando si la instancia ya existe...
Creando instancia de PostgreSQL...
```

Verás una barra de progreso:
```
Create request issued for: [cmms-db]
Waiting for operation to complete...done.
Created [https://sqladmin.googleapis.com/sql/v1beta4/projects/argon-edge-478500-i8/instances/cmms-db].
```

Luego:
```
✓ Instancia de Cloud SQL creada

Creando base de datos...
✓ Base de datos creada

Creando usuario...
✓ Usuario creado
```

**Qué está pasando**: Se está creando tu base de datos PostgreSQL en la nube.

---

## 📋 Fase 4: Crear Cloud Storage (1-2 minutos)

```
═══════════════════════════════════════════════════════════
Paso 2/5: Creando Cloud Storage Buckets (1-2 minutos)
═══════════════════════════════════════════════════════════

Creando bucket: argon-edge-478500-i8-cmms-documents
✓ Bucket argon-edge-478500-i8-cmms-documents creado

Creando bucket: argon-edge-478500-i8-cmms-ml-models
✓ Bucket argon-edge-478500-i8-cmms-ml-models creado

Creando bucket: argon-edge-478500-i8-cmms-reports
✓ Bucket argon-edge-478500-i8-cmms-reports creado

Creando bucket: argon-edge-478500-i8-cmms-backups
✓ Bucket argon-edge-478500-i8-cmms-backups creado
```

**Qué está pasando**: Se están creando 4 buckets para almacenar archivos.

---

## 📋 Fase 5: Configurar Pub/Sub (1 minuto)

```
═══════════════════════════════════════════════════════════
Paso 3/5: Configurando Cloud Pub/Sub (1 minuto)
═══════════════════════════════════════════════════════════

Creando topic: notifications
✓ Topic notifications creado
Creando subscription: notifications-sub
✓ Subscription notifications-sub creada

Creando topic: events
✓ Topic events creado
Creando subscription: events-sub
✓ Subscription events-sub creada

Creando topic: alerts
✓ Topic alerts creado
Creando subscription: alerts-sub
✓ Subscription alerts-sub creada
```

**Qué está pasando**: Se está configurando el sistema de mensajería.

---

## 📋 Fase 6: Desplegar Backend (8-10 minutos)

```
═══════════════════════════════════════════════════════════
Paso 4/5: Desplegando Backend a Cloud Run (8-10 minutos)
═══════════════════════════════════════════════════════════

Creando Dockerfile...
✓ Dockerfile creado

Desplegando backend (esto puede tomar 8-10 minutos)...
```

Verás mucha actividad:
```
Building using Dockerfile and deploying container to Cloud Run service [cmms-backend]...
⠹ Building and deploying... Building Container.
  ✓ Creating Container Repository...
  ✓ Uploading sources...
  ✓ Building Container... Logs are available at [https://console.cloud.google.com/...]
  ✓ Creating Revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
```

Finalmente:
```
✓ Backend desplegado
✓ Backend URL: https://cmms-backend-xxxxx-uc.a.run.app
```

**Qué está pasando**: 
1. Se construye una imagen Docker con tu código
2. Se sube a Google Container Registry
3. Se despliega en Cloud Run
4. Se configura la conexión a la base de datos

---

## 🎉 Finalización

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ✓ Despliegue Completado Exitosamente                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

URLs de la Aplicación:
  Backend:  https://cmms-backend-xxxxx-uc.a.run.app
  API Docs: https://cmms-backend-xxxxx-uc.a.run.app/api/docs/

Recursos Creados:
  ✓ Cloud SQL: argon-edge-478500-i8:us-central1:cmms-db
  ✓ Cloud Storage: 4 buckets
  ✓ Cloud Pub/Sub: 3 topics + subscriptions
  ✓ Cloud Run: cmms-backend

Próximos Pasos:
  1. Crear superusuario para acceder al admin
  2. Probar la API en: https://cmms-backend-xxxxx-uc.a.run.app/api/docs/

¡Despliegue completado! 🎉

✓ Información guardada en: deployment-info.txt
```

---

## 📝 Archivo Generado

Se creará un archivo `deployment-info.txt` con toda la información:
```
Información del Despliegue
==========================
Fecha: 2025-11-16 21:45:00
Proyecto: argon-edge-478500-i8
Cuenta: electronightx@gmail.com
Backend URL: https://cmms-backend-xxxxx-uc.a.run.app
Connection Name: argon-edge-478500-i8:us-central1:cmms-db
Región: us-central1

Credenciales de Base de Datos:
- Host: /cloudsql/argon-edge-478500-i8:us-central1:cmms-db
- Database: cmms_prod
- User: cmms_user
- Password: [guardada en variables de entorno de Cloud Run]
```

---

## ⚠️ Posibles Mensajes de Advertencia (Normales)

### "API not enabled"
```
ERROR: (gcloud.services.enable) FAILED_PRECONDITION: ...
```
**Solución**: El script reintentará automáticamente.

### "Bucket already exists"
```
⚠ Bucket argon-edge-478500-i8-cmms-documents ya existe o error
```
**Solución**: Normal si ya ejecutaste el script antes. Continúa sin problema.

### "Instance already exists"
```
⚠ La instancia cmms-db ya existe
¿Deseas usar la instancia existente? (y/n):
```
**Solución**: Escribe `y` para usar la existente o `n` para cancelar.

---

## 🆘 Si Algo Sale Mal

### Error en Cloud SQL
```
✗ Error al crear Cloud SQL
```
**Qué hacer**:
1. Verificar que la facturación esté habilitada
2. Verificar que tengas permisos de Editor/Owner
3. Intentar nuevamente

### Error en Cloud Run
```
✗ Error al desplegar backend
```
**Qué hacer**:
1. Ver los logs: `gcloud builds list`
2. Ver detalles del error: `gcloud builds log BUILD_ID`
3. Verificar que el Dockerfile sea correcto

### Timeout
Si el proceso se detiene por mucho tiempo:
1. Presiona Ctrl+C
2. Verifica el estado en Cloud Console
3. Reintenta el paso específico

---

## 📊 Monitoreo Durante el Despliegue

Puedes abrir otra terminal y ejecutar:

```powershell
# Ver logs de Cloud Build
gcloud builds list --project=argon-edge-478500-i8

# Ver estado de Cloud SQL
gcloud sql instances describe cmms-db --project=argon-edge-478500-i8

# Ver servicios de Cloud Run
gcloud run services list --project=argon-edge-478500-i8
```

O abrir Cloud Console:
```powershell
Start-Process "https://console.cloud.google.com/home/dashboard?project=argon-edge-478500-i8"
```

---

## ✅ Checklist de Progreso

- [ ] APIs habilitadas (3-5 min)
- [ ] Contraseña de BD ingresada
- [ ] Cloud SQL creado (8-10 min)
- [ ] Cloud Storage creado (1-2 min)
- [ ] Pub/Sub configurado (1 min)
- [ ] Backend desplegado (8-10 min)
- [ ] URL del backend obtenida
- [ ] Archivo deployment-info.txt creado

---

**Tiempo Total Esperado**: 20-25 minutos

**¡Ten paciencia! El despliegue toma tiempo pero es automático.**

🚀 **¡Buena suerte!**
