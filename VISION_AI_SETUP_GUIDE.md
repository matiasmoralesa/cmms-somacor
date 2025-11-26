# Google Cloud Vision AI Setup Guide

Esta guía te ayudará a configurar Google Cloud Vision AI para el análisis automático de imágenes en el sistema CMMS.

## Requisitos Previos

- Cuenta de Google Cloud Platform (GCP)
- Proyecto de GCP creado
- Permisos de administrador del proyecto
- Tarjeta de crédito registrada (para habilitar APIs de pago)

## Paso 1: Habilitar Cloud Vision API

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Selecciona tu proyecto o crea uno nuevo
3. En el menú de navegación, ve a **APIs & Services > Library**
4. Busca "Cloud Vision API"
5. Haz clic en "Cloud Vision API"
6. Haz clic en "ENABLE" (Habilitar)
7. Espera unos segundos mientras se habilita la API

## Paso 2: Crear Service Account

1. Ve a **IAM & Admin > Service Accounts**
2. Haz clic en "CREATE SERVICE ACCOUNT"
3. Configura la cuenta de servicio:
   - **Service account name**: `cmms-vision-ai`
   - **Service account ID**: `cmms-vision-ai` (se genera automáticamente)
   - **Description**: `Service account for CMMS Vision AI image analysis`
4. Haz clic en "CREATE AND CONTINUE"

## Paso 3: Asignar Roles

Asigna los siguientes roles a la service account:

1. **Cloud Vision AI User** (`roles/cloudvision.user`)
   - Permite usar la API de Vision AI
   
2. **Storage Object Viewer** (`roles/storage.objectViewer`)
   - Permite leer imágenes desde Cloud Storage
   
3. **Storage Object Creator** (`roles/storage.objectCreator`)
   - Permite guardar resultados procesados

Haz clic en "CONTINUE" y luego en "DONE"

## Paso 4: Crear y Descargar Clave

1. En la lista de Service Accounts, encuentra `cmms-vision-ai`
2. Haz clic en los tres puntos (⋮) a la derecha
3. Selecciona "Manage keys"
4. Haz clic en "ADD KEY" > "Create new key"
5. Selecciona formato **JSON**
6. Haz clic en "CREATE"
7. Se descargará un archivo JSON con las credenciales
8. **IMPORTANTE**: Guarda este archivo de forma segura
9. Renombra el archivo a: `gcp-vision-ai-credentials.json`

## Paso 5: Configurar Variables de Entorno

Edita el archivo `backend/.env`:

```env
# Google Cloud Platform
GCP_PROJECT_ID=tu-proyecto-id
GOOGLE_APPLICATION_CREDENTIALS=/ruta/completa/a/gcp-vision-ai-credentials.json

# Google Cloud Vision AI
VISION_AI_ENABLED=True
VISION_AI_MAX_RESULTS=10
```

### Encontrar tu Project ID:

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. En la parte superior, verás el nombre del proyecto
3. Haz clic en el selector de proyectos
4. Copia el **Project ID** (no el nombre del proyecto)

## Paso 6: Configurar Cloud Storage Bucket

Las imágenes deben estar en Cloud Storage para que Vision AI pueda accederlas:

1. Ve a **Cloud Storage > Buckets**
2. Haz clic en "CREATE BUCKET"
3. Configura el bucket:
   - **Name**: `cmms-somacor-images` (debe ser único globalmente)
   - **Location type**: Region
   - **Location**: `southamerica-east1` (São Paulo) o `us-central1`
   - **Storage class**: Standard
   - **Access control**: Uniform
4. Haz clic en "CREATE"

### Configurar Permisos del Bucket

1. Selecciona el bucket creado
2. Ve a la pestaña "PERMISSIONS"
3. Haz clic en "GRANT ACCESS"
4. Agrega la service account `cmms-vision-ai@[PROJECT_ID].iam.gserviceaccount.com`
5. Asigna el rol "Storage Object Viewer"
6. Haz clic en "SAVE"

## Paso 7: Actualizar Configuración de Django

Edita `backend/.env`:

```env
GCP_STORAGE_BUCKET_NAME=cmms-somacor-images
```

## Paso 8: Verificar la Configuración

Ejecuta el siguiente script de prueba:

```bash
cd backend
python manage.py shell
```

Luego ejecuta:

```python
from apps.images.services.vision_ai_client import vision_ai_client

# Verificar que Vision AI está disponible
print(f"Vision AI disponible: {vision_ai_client.is_available()}")

# Probar detección de etiquetas con una imagen de prueba
# Usa una imagen pública de ejemplo
test_image_url = "gs://cloud-samples-data/vision/label/wakeupcat.jpg"

try:
    labels = vision_ai_client.detect_labels(test_image_url)
    print(f"\nEtiquetas detectadas: {len(labels)}")
    for label in labels[:5]:
        print(f"  - {label['description']}: {label['score']:.2%}")
except Exception as e:
    print(f"Error: {str(e)}")
```

## Paso 9: Configurar Límites y Presupuesto

Para evitar costos inesperados:

### Configurar Alertas de Presupuesto

1. Ve a **Billing > Budgets & alerts**
2. Haz clic en "CREATE BUDGET"
3. Configura:
   - **Name**: `Vision AI Monthly Budget`
   - **Budget amount**: $300 (ajusta según necesidad)
   - **Threshold rules**: 50%, 80%, 100%
4. Configura notificaciones por email
5. Haz clic en "FINISH"

### Configurar Cuotas

1. Ve a **IAM & Admin > Quotas**
2. Busca "Cloud Vision API"
3. Selecciona las siguientes cuotas:
   - **Requests per minute**: 1800 (máximo en capa gratuita)
   - **Requests per day**: Ilimitado (pero monitorea costos)
4. Haz clic en "EDIT QUOTAS" si necesitas ajustar

## Funcionalidades de Vision AI Disponibles

### 1. Label Detection (Detección de Etiquetas)
Identifica objetos, conceptos y categorías en la imagen.

**Ejemplo de uso**:
```python
labels = vision_ai_client.detect_labels(image_url)
# Resultado: [{'description': 'Vehicle', 'score': 0.95}, ...]
```

### 2. Text Detection (OCR)
Extrae texto de imágenes (medidores, placas, etiquetas).

**Ejemplo de uso**:
```python
texts = vision_ai_client.detect_text(image_url)
# Resultado: [{'description': 'ABC-1234', 'bounding_box': [...]}]
```

### 3. Object Localization
Detecta y localiza objetos con bounding boxes.

**Ejemplo de uso**:
```python
objects = vision_ai_client.detect_objects(image_url)
# Resultado: [{'name': 'Tire', 'score': 0.89, 'bounding_box': [...]}]
```

### 4. Image Properties
Analiza propiedades como colores dominantes.

**Ejemplo de uso**:
```python
properties = vision_ai_client.analyze_image_properties(image_url)
# Resultado: {'dominant_colors': [{'red': 255, 'green': 0, 'blue': 0}]}
```

### 5. Safe Search Detection
Detecta contenido inapropiado.

**Ejemplo de uso**:
```python
safe_search = vision_ai_client.detect_safe_search(image_url)
# Resultado: {'adult': 'VERY_UNLIKELY', 'violence': 'UNLIKELY'}
```

## Costos de Vision AI

### Capa Gratuita

Las primeras 1,000 unidades por mes son **GRATIS** para:
- Label Detection
- Text Detection
- Image Properties
- Safe Search Detection
- Object Localization

### Precios Después de la Capa Gratuita

| Funcionalidad | Precio por 1,000 imágenes |
|--------------|---------------------------|
| Label Detection | $1.50 |
| Text Detection (OCR) | $1.50 |
| Object Localization | $1.50 |
| Image Properties | $1.00 |
| Safe Search | $1.00 |

### Estimación de Costos Mensuales

Para **10,000 imágenes/mes**:
- Primeras 1,000: Gratis
- Siguientes 9,000: ~$13.50
- **Total estimado**: $13.50/mes

Para **50,000 imágenes/mes**:
- Primeras 1,000: Gratis
- Siguientes 49,000: ~$73.50
- **Total estimado**: $73.50/mes

## Optimización de Costos

### 1. Caché de Resultados

El sistema ya implementa caché de 30 días:

```python
# En settings.py
VISION_AI_CACHE_DAYS = 30
```

Esto evita procesar la misma imagen múltiples veces.

### 2. Procesamiento por Lotes

Agrupa imágenes no urgentes:

```python
# En settings.py
BATCH_PROCESSING_ENABLED = True
BATCH_SIZE_IMAGES = 10
```

### 3. Procesamiento en Horarios de Bajo Costo

Procesa imágenes no críticas en horarios off-peak:

```python
# En settings.py
OFF_PEAK_HOURS_START = 22  # 10 PM
OFF_PEAK_HOURS_END = 6     # 6 AM
```

### 4. Límites de Presupuesto

Configura límites automáticos:

```python
# En settings.py
MONTHLY_BUDGET_LIMIT_USD = 300
BUDGET_WARNING_THRESHOLD = 0.80  # Alerta al 80%
BUDGET_THROTTLE_THRESHOLD = 0.90  # Throttle al 90%
```

## Monitoreo de Uso

### Dashboard de Métricas

1. Ve a **APIs & Services > Dashboard**
2. Selecciona "Cloud Vision API"
3. Verás gráficos de:
   - Requests por día
   - Latencia
   - Errores
   - Cuota utilizada

### Logs de Auditoría

1. Ve a **Logging > Logs Explorer**
2. Filtra por:
   ```
   resource.type="cloud_vision_api"
   ```
3. Revisa logs de requests y errores

### Alertas Personalizadas

Crea alertas para monitorear uso:

1. Ve a **Monitoring > Alerting**
2. Haz clic en "CREATE POLICY"
3. Configura condiciones:
   - Métrica: `vision.googleapis.com/api/request_count`
   - Threshold: 800 requests/día (80% de la cuota gratuita)
4. Configura notificaciones

## Solución de Problemas

### Error: "API not enabled"

```
google.api_core.exceptions.PermissionDenied: 403 Cloud Vision API has not been used
```

**Solución**: Habilita la API en Google Cloud Console

### Error: "Permission denied"

```
google.api_core.exceptions.PermissionDenied: 403 Permission denied
```

**Solución**: 
- Verifica que la service account tiene el rol `roles/cloudvision.user`
- Verifica que `GOOGLE_APPLICATION_CREDENTIALS` apunta al archivo correcto

### Error: "Invalid image URI"

```
google.api_core.exceptions.InvalidArgument: 400 Invalid image URI
```

**Solución**:
- Verifica que la imagen está en Cloud Storage
- Usa formato `gs://bucket-name/path/to/image.jpg`
- Verifica que la service account tiene acceso al bucket

### Error: "Quota exceeded"

```
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded
```

**Solución**:
- Espera hasta que se renueve la cuota (diaria o mensual)
- Solicita aumento de cuota en Google Cloud Console
- Implementa rate limiting en tu aplicación

## Mejores Prácticas

### 1. Compresión de Imágenes

Comprime imágenes antes de enviarlas a Vision AI:

```python
# Ya implementado en el sistema
MAX_IMAGE_SIZE_MB = 10
COMPRESSED_IMAGE_SIZE_MB = 2
```

### 2. Procesamiento Asíncrono

Usa Celery para procesamiento en background:

```python
from apps.images.tasks import process_inspection_photo

# Procesar de forma asíncrona
process_inspection_photo.delay(photo_id)
```

### 3. Manejo de Errores

Implementa retry logic con exponential backoff:

```python
# Ya configurado en Celery
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_RETRY_BACKOFF = True
```

### 4. Validación de Imágenes

Valida imágenes antes de enviarlas:

```python
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
```

## Recursos Adicionales

- [Documentación de Cloud Vision API](https://cloud.google.com/vision/docs)
- [Precios de Vision AI](https://cloud.google.com/vision/pricing)
- [Guía de Mejores Prácticas](https://cloud.google.com/vision/docs/best-practices)
- [Límites y Cuotas](https://cloud.google.com/vision/quotas)

## Próximos Pasos

Una vez completada la configuración de Vision AI:

1. Configura Vertex AI para modelos ML personalizados
2. Entrena el modelo de detección de anomalías
3. Entrena el modelo de clasificación de daños
4. Implementa el pipeline de mejora continua de modelos

¡Vision AI está listo para analizar imágenes! 🎯
