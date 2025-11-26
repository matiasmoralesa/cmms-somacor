# Plan de Despliegue - CMMS Somacor v3

## Información del Proyecto

- **Proyecto GCP**: `cmms-somacor-v3`
- **Número de Proyecto**: `487419690858`
- **Cuenta**: `matilqsabe@gmail.com`
- **Cuenta de Facturación**: `01BB05-89A92F-50D74C`
- **Estado**: ✅ Activo con facturación habilitada

## APIs Habilitadas

✅ Cloud Run API
✅ Cloud SQL Admin API
✅ Secret Manager API
✅ Cloud Build API
✅ Artifact Registry API
✅ AI Platform API (Gemini Pro)

## Arquitectura del Sistema

### 1. Base de Datos
- **Servicio**: Cloud SQL (PostgreSQL 15)
- **Tier**: db-f1-micro (Free Tier)
- **Región**: us-central1
- **Nombre**: cmms-db-v3

### 2. Backend
- **Servicio**: Cloud Run
- **Framework**: Django + DRF
- **Autenticación**: Firebase Authentication
- **IA**: Gemini Pro para análisis predictivo
- **Región**: us-central1

### 3. Frontend
- **Servicio**: Firebase Hosting
- **Framework**: React + Vite
- **Autenticación**: Firebase SDK

### 4. Almacenamiento
- **Servicio**: Firebase Storage
- **Uso**: Fotos de licencias, documentos, imágenes

### 5. IA y Machine Learning
- **Servicio**: Vertex AI (Gemini Pro)
- **Uso**: 
  - Análisis predictivo de mantenimiento
  - Procesamiento de imágenes
  - Generación de reportes inteligentes
  - Chatbot de soporte

## Pasos de Despliegue

### Fase 1: Configuración de Firebase
1. Crear nuevo proyecto Firebase vinculado a `cmms-somacor-v3`
2. Habilitar Authentication (Email/Password)
3. Habilitar Firestore (opcional para caché)
4. Habilitar Storage
5. Habilitar Hosting
6. Obtener credenciales del Admin SDK

### Fase 2: Configuración de Cloud SQL
1. Crear instancia PostgreSQL 15
2. Configurar usuario y contraseña
3. Crear base de datos `cmms_db`
4. Configurar conexión desde Cloud Run

### Fase 3: Configuración de Secrets
1. Crear secret para Firebase credentials
2. Crear secret para Django secret key
3. Crear secret para database URL
4. Crear secret para Gemini API key

### Fase 4: Despliegue del Backend
1. Construir imagen Docker
2. Desplegar a Cloud Run
3. Configurar variables de entorno
4. Conectar a Cloud SQL
5. Ejecutar migraciones
6. Crear usuarios iniciales

### Fase 5: Configuración de Gemini Pro
1. Habilitar Vertex AI API
2. Configurar credenciales
3. Implementar endpoints de IA:
   - `/api/v1/ai/predict-maintenance/`
   - `/api/v1/ai/analyze-image/`
   - `/api/v1/ai/generate-report/`
   - `/api/v1/ai/chat/`

### Fase 6: Despliegue del Frontend
1. Configurar Firebase config
2. Compilar aplicación
3. Desplegar a Firebase Hosting
4. Configurar dominio personalizado (opcional)

## Características con Gemini Pro

### 1. Mantenimiento Predictivo
```python
# Análisis de patrones de fallas
# Predicción de próximas fallas
# Recomendaciones de mantenimiento preventivo
```

### 2. Procesamiento de Imágenes
```python
# Análisis de fotos de equipos
# Detección de anomalías visuales
# Verificación de licencias
```

### 3. Generación de Reportes
```python
# Reportes automáticos con insights
# Resúmenes ejecutivos
# Análisis de tendencias
```

### 4. Chatbot Inteligente
```python
# Asistente virtual para operadores
# Respuestas a preguntas frecuentes
# Guía de procedimientos
```

## Ventajas del Nuevo Proyecto

1. **Limpio**: Sin configuraciones conflictivas del proyecto anterior
2. **Gemini Pro**: Acceso completo a capacidades de IA
3. **Free Tier**: Optimizado para costos mínimos
4. **Escalable**: Arquitectura preparada para crecer
5. **Moderno**: Últimas versiones de todas las tecnologías

## Costos Estimados

### Free Tier (Primeros 90 días)
- Cloud Run: $0 (hasta 2M requests)
- Cloud SQL: $0 (db-f1-micro)
- Firebase: $0 (Spark plan)
- Gemini Pro: $0 (cuota gratuita generosa)

### Después del Free Tier
- Cloud Run: ~$5-10/mes
- Cloud SQL: ~$7/mes
- Firebase: ~$0-5/mes
- Gemini Pro: ~$10-20/mes (según uso)

**Total estimado**: $22-42/mes

## Próximos Pasos

1. ✅ Proyecto GCP creado
2. ✅ APIs habilitadas
3. ⏳ Crear proyecto Firebase
4. ⏳ Configurar Cloud SQL
5. ⏳ Desplegar backend
6. ⏳ Desplegar frontend
7. ⏳ Integrar Gemini Pro

## Comandos Útiles

### Verificar proyecto actual
```bash
gcloud config get-value project
```

### Cambiar proyecto
```bash
gcloud config set project cmms-somacor-v3
```

### Ver servicios habilitados
```bash
gcloud services list --enabled
```

### Ver logs
```bash
gcloud logging read --limit=50
```

---

**Fecha de Creación**: 26 de Noviembre de 2025
**Estado**: 🚀 Listo para comenzar despliegue
