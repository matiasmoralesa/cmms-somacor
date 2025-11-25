# 🚀 Acceso al Sistema CMMS - Producción

## 📍 URL Principal del Sistema

```
https://storage.googleapis.com/cmms-frontend-somacorv2/index.html
```

---

## 🔐 Credenciales de Acceso

### Usuario Administrador
- **Usuario**: `admin`
- **Contraseña**: La que configuraste en la base de datos

### Usuarios de Prueba
Si creaste usuarios adicionales, puedes acceder con sus credenciales.

---

## 🎯 Módulos Disponibles

Una vez que inicies sesión, tendrás acceso a:

### 1. Dashboard
- Estadísticas en tiempo real
- Gráficos de tendencias de mantenimiento
- Órdenes de trabajo por prioridad
- Estado de salud de activos

### 2. Checklists
- 5 plantillas profesionales basadas en PDFs reales
- 266 items de inspección en total
- Plantillas para:
  - Camionetas MDO (F-PR-020-CH01)
  - Retroexcavadora MDO (F-PR-034-CH01)
  - Cargador Frontal MDO (F-PR-037-CH01)
  - Minicargador MDO (F-PR-040-CH01)
  - Camión Supersucker (SUPERSUCKER-CH01)

### 3. Activos
- Gestión de vehículos y equipos
- Historial de mantenimiento
- Estado operacional
- Ubicaciones

### 4. Órdenes de Trabajo
- Creación y asignación de órdenes
- Seguimiento de estado
- Prioridades
- Historial completo

### 5. Mantenimiento
- Planes de mantenimiento preventivo
- Programación automática
- Alertas de vencimiento

### 6. Inventario
- Gestión de repuestos
- Control de stock
- Movimientos de inventario
- Alertas de stock bajo

### 7. Reportes
- KPIs (MTBF, MTTR, OEE)
- Reportes de órdenes de trabajo
- Downtime de activos
- Consumo de repuestos
- Exportación a CSV

---

## 🔗 URLs del Sistema

### Frontend (Interfaz de Usuario)
```
https://storage.googleapis.com/cmms-frontend-somacorv2/index.html
```

### Backend API
```
https://cmms-backend-service-888881509782.us-central1.run.app/api/v1/
```

### Documentación API (Swagger)
```
https://cmms-backend-service-888881509782.us-central1.run.app/api/docs/
```

### Documentación API (ReDoc)
```
https://cmms-backend-service-888881509782.us-central1.run.app/api/redoc/
```

---

## 📱 Características del Sistema

### Diseño Moderno
- ✅ Interfaz limpia y profesional
- ✅ Diseño responsive (móvil, tablet, desktop)
- ✅ Tema claro con colores corporativos
- ✅ Animaciones suaves

### Funcionalidad Completa
- ✅ Autenticación JWT
- ✅ Refresh automático de tokens
- ✅ Manejo de errores robusto
- ✅ Validación de formularios
- ✅ Feedback visual

### Datos en Tiempo Real
- ✅ Dashboard con estadísticas actualizadas
- ✅ Gráficos interactivos
- ✅ Alertas y notificaciones
- ✅ Estado de activos en vivo

---

## 🛠️ Arquitectura del Sistema

### Frontend
- **Tecnología**: React + TypeScript + Vite
- **Hosting**: Google Cloud Storage (Static Website)
- **UI**: Tailwind CSS + Recharts
- **Estado**: Zustand

### Backend
- **Tecnología**: Django + Django REST Framework
- **Hosting**: Google Cloud Run
- **Base de Datos**: Cloud SQL (PostgreSQL)
- **Autenticación**: JWT (Simple JWT)

### Infraestructura
- **Cloud Provider**: Google Cloud Platform
- **Región**: us-central1
- **Tier**: Free Tier optimizado
- **Escalabilidad**: Automática (Cloud Run)

---

## 📊 Datos Disponibles

El sistema viene pre-cargado con:

### Checklists
- 5 plantillas profesionales
- 266 items de inspección
- Basados en PDFs reales de la empresa

### Usuarios
- Administradores
- Técnicos
- Operadores

### Activos
- Vehículos de diferentes tipos
- Equipos y maquinaria
- Ubicaciones asignadas

### Órdenes de Trabajo
- Preventivas
- Correctivas
- Predictivas

### Inventario
- Repuestos
- Materiales
- Movimientos de stock

---

## 🔍 Cómo Usar el Sistema

### 1. Acceso Inicial
1. Abre el navegador
2. Ve a: `https://storage.googleapis.com/cmms-frontend-somacorv2/index.html`
3. Ingresa tus credenciales
4. Haz clic en "Iniciar Sesión"

### 2. Navegación
- Usa el menú lateral para acceder a los diferentes módulos
- El dashboard es la página principal
- Cada módulo tiene su propia interfaz

### 3. Crear una Orden de Trabajo
1. Ve a "Órdenes de Trabajo"
2. Haz clic en "Nueva Orden"
3. Completa el formulario
4. Asigna un técnico
5. Guarda

### 4. Completar un Checklist
1. Ve a "Checklists"
2. Selecciona una plantilla
3. Completa los items
4. Marca como completado
5. Guarda

### 5. Ver Reportes
1. Ve a "Reportes"
2. Selecciona el tipo de reporte
3. Ajusta el rango de fechas
4. Visualiza o exporta

---

## 🆘 Soporte

### Problemas Comunes

#### No puedo iniciar sesión
- Verifica que estés usando las credenciales correctas
- Asegúrate de que el backend esté funcionando
- Limpia la caché del navegador

#### El dashboard no carga
- Verifica tu conexión a internet
- Refresca la página (F5)
- Revisa la consola del navegador (F12)

#### Los datos no se actualizan
- Refresca la página
- Cierra sesión y vuelve a iniciar
- Verifica que tengas permisos

### Logs y Debugging

Para ver los logs del backend:
```bash
gcloud run services logs read cmms-backend-service --region=us-central1 --limit=50
```

Para ver el estado del servicio:
```bash
gcloud run services describe cmms-backend-service --region=us-central1
```

---

## 📈 Monitoreo

### Cloud Console
Puedes monitorear el sistema desde:
```
https://console.cloud.google.com/run?project=cmms-somacorv2
```

### Métricas Disponibles
- Solicitudes por segundo
- Latencia
- Errores
- Uso de CPU y memoria
- Conexiones a base de datos

---

## 🔒 Seguridad

### Características de Seguridad
- ✅ Autenticación JWT
- ✅ HTTPS obligatorio
- ✅ CORS configurado
- ✅ Rate limiting
- ✅ Validación de entrada
- ✅ Sanitización de datos
- ✅ Headers de seguridad

### Recomendaciones
- Cambia las contraseñas por defecto
- Usa contraseñas fuertes
- No compartas credenciales
- Cierra sesión al terminar
- Revisa los logs regularmente

---

## 🎉 ¡Listo para Usar!

El sistema CMMS está completamente funcional y listo para ser usado en producción. Todos los módulos están operativos y los datos se cargan en tiempo real desde la base de datos.

**¡Disfruta del sistema!** 🚀
