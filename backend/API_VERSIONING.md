# Estrategia de Versionado de API

## Descripción General

La API CMMS utiliza versionado basado en URL para mantener compatibilidad hacia atrás y permitir evolución controlada de la API.

## Formato de Versión

Las versiones se especifican en la URL con el formato `/api/v{número}/`:

```
https://api.cmms.com/api/v1/assets/
https://api.cmms.com/api/v2/assets/  (futura)
```

## Versión Actual

**v1.0.0** - Versión inicial de producción

## Política de Versionado

### Cuándo Crear una Nueva Versión Mayor

Se crea una nueva versión mayor (v1 → v2) cuando hay cambios que rompen compatibilidad:

- **Eliminación de campos** en respuestas
- **Cambio de tipos de datos** (string → integer)
- **Cambio de estructura** de respuestas
- **Eliminación de endpoints**
- **Cambio de comportamiento** fundamental

### Cambios que NO Requieren Nueva Versión

Los siguientes cambios son compatibles hacia atrás:

- **Agregar nuevos campos** a respuestas (los clientes los ignoran)
- **Agregar nuevos endpoints**
- **Agregar parámetros opcionales**
- **Hacer campos opcionales** (que antes eran requeridos)
- **Corrección de bugs** que no cambian comportamiento esperado

## Ciclo de Vida de Versiones

### Fase 1: Activa
- Versión actual recomendada
- Recibe nuevas características
- Soporte completo

### Fase 2: Deprecada
- Aún funcional pero no recomendada
- No recibe nuevas características
- Solo corrección de bugs críticos
- Duración mínima: 6 meses

### Fase 3: Descontinuada
- Ya no disponible
- Retorna error 410 Gone

## Deprecación de Endpoints

Cuando un endpoint será deprecado:

1. Se agrega header `Deprecation: true` en respuestas
2. Se agrega header `Sunset: fecha` indicando cuándo será removido
3. Se documenta en changelog
4. Se notifica a usuarios con 6 meses de anticipación

Ejemplo:
```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Wed, 01 Jun 2025 00:00:00 GMT
Link: </api/v2/assets/>; rel="successor-version"
```

## Implementación Técnica

### Estructura de URLs

```python
# config/urls.py
urlpatterns = [
    # API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/assets/', include('apps.assets.urls')),
    # ... otros módulos
    
    # API v2 (futura)
    # path('api/v2/auth/', include('apps.authentication.v2.urls')),
]
```

### Versionado de Serializers

Para cambios mayores, crear nuevos serializers:

```python
# v1/serializers.py
class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'status']

# v2/serializers.py (futura)
class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'status', 'health_score']  # nuevo campo
```

### Versionado de Vistas

```python
# v1/views.py
class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    # lógica v1

# v2/views.py (futura)
class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializerV2
    # lógica v2 con mejoras
```

## Negociación de Contenido (Alternativa)

Aunque actualmente usamos versionado por URL, el sistema está preparado para soportar versionado por header:

```http
GET /api/assets/
Accept: application/vnd.cmms.v1+json
```

## Migración Entre Versiones

### Para Desarrolladores de API

1. Mantener ambas versiones funcionando durante período de transición
2. Documentar diferencias en changelog
3. Proveer guías de migración
4. Ofrecer herramientas de migración si es posible

### Para Consumidores de API

1. Revisar changelog antes de actualizar
2. Probar en ambiente de desarrollo
3. Actualizar código para nueva versión
4. Migrar en producción antes de fecha de sunset

## Changelog de Versiones

### v1.0.0 (2024-11-13)

**Lanzamiento Inicial**

Módulos incluidos:
- Autenticación y autorización
- Gestión de activos
- Órdenes de trabajo
- Mantenimiento preventivo
- Inventario de repuestos
- Checklists
- Predicciones ML
- Notificaciones
- Reportes y KPIs
- Configuración

## Ejemplos de Uso

### Cliente Especificando Versión

```python
import requests

# Usar v1
response = requests.get(
    'https://api.cmms.com/api/v1/assets/',
    headers={'Authorization': 'Bearer token'}
)

# Cuando v2 esté disponible
response = requests.get(
    'https://api.cmms.com/api/v2/assets/',
    headers={'Authorization': 'Bearer token'}
)
```

### Verificar Versión Actual

```http
GET /api/v1/
```

Respuesta:
```json
{
  "version": "1.0.0",
  "status": "active",
  "documentation": "/api/docs/",
  "endpoints": {
    "auth": "/api/v1/auth/",
    "assets": "/api/v1/assets/",
    "work_orders": "/api/v1/work-orders/",
    ...
  }
}
```

## Mejores Prácticas

### Para Consumidores

1. **Siempre especificar versión** en URL
2. **No asumir estructura** de respuestas
3. **Manejar campos desconocidos** gracefully
4. **Monitorear headers de deprecación**
5. **Actualizar regularmente** a versiones nuevas

### Para Desarrolladores

1. **Documentar todos los cambios**
2. **Mantener compatibilidad** cuando sea posible
3. **Dar tiempo suficiente** para migración
4. **Proveer herramientas** de migración
5. **Comunicar cambios** proactivamente

## Soporte de Versiones

| Versión | Estado | Lanzamiento | Deprecación | Fin de Soporte |
|---------|--------|-------------|-------------|----------------|
| v1.0.0 | Activa | 2024-11-13 | - | - |

## Contacto

Para preguntas sobre versionado:
- Email: api@cmms.com
- Documentación: /api/docs/
