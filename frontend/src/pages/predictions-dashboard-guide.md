# Prediction Dashboard - Guía de Uso

## Descripción General

El Dashboard de Predicciones es una interfaz completa para monitorear y gestionar las predicciones de fallas de activos utilizando Machine Learning.

## Componentes Principales

### 1. PredictionStatsCard
Tarjeta de estadísticas que muestra métricas clave:
- Activos monitoreados
- Probabilidad promedio de falla
- Activos de alto riesgo
- Alertas críticas

**Props:**
```typescript
{
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: { value: number; direction: 'up' | 'down' };
  color?: 'blue' | 'green' | 'amber' | 'red';
}
```

### 2. RiskDistributionChart
Gráfico de barras que muestra la distribución de riesgo por nivel:
- Bajo (Verde)
- Medio (Ámbar)
- Alto (Naranja)
- Crítico (Rojo)

**Props:**
```typescript
{
  distribution: Record<string, number>;
}
```

### 3. TrendingRisksTable
Tabla que muestra los activos con tendencias de riesgo:
- Nombre y código del activo
- Probabilidad actual de falla
- Tendencia (↑ aumentando, ↓ disminuyendo, → estable)
- Número de predicciones

**Props:**
```typescript
{
  assets: TrendingAsset[];
  onAssetClick?: (assetId: string) => void;
}
```

### 4. AlertsList
Lista de alertas con opciones de gestión:
- Alertas críticas sin resolver
- Marcar como leída
- Resolver alerta
- Filtrado por severidad

**Props:**
```typescript
{
  alerts: Alert[];
  onAlertClick?: (alert: Alert) => void;
  onMarkAsRead?: (alertId: string) => void;
  onResolve?: (alertId: string) => void;
  maxItems?: number;
}
```

### 5. PredictionDetailModal
Modal que muestra detalles completos de una predicción:
- Nivel de riesgo
- Probabilidad de falla
- Confianza del modelo
- Fechas de predicción
- Recomendaciones
- Características de entrada

**Props:**
```typescript
{
  prediction: FailurePrediction | null;
  isOpen: boolean;
  onClose: () => void;
}
```

## Endpoints API Utilizados

### Dashboard Stats
```
GET /api/v1/predictions/predictions/dashboard_stats/
```
Retorna estadísticas generales del dashboard.

### Trending Risks
```
GET /api/v1/predictions/predictions/trending_risks/
```
Retorna activos con tendencias de riesgo en los últimos 30 días.

### Critical Alerts
```
GET /api/v1/predictions/alerts/critical/
```
Retorna alertas críticas sin resolver.

### Mark Alert as Read
```
POST /api/v1/predictions/alerts/{id}/mark_read/
```
Marca una alerta como leída.

### Resolve Alert
```
POST /api/v1/predictions/alerts/{id}/resolve/
```
Resuelve una alerta.

## Flujo de Uso

1. **Carga Inicial:**
   - El dashboard carga automáticamente las estadísticas, tendencias y alertas
   - Muestra un spinner de carga mientras obtiene los datos

2. **Visualización:**
   - Las tarjetas de estadísticas muestran métricas clave
   - El gráfico de distribución muestra el estado general de riesgo
   - La tabla de tendencias identifica activos que requieren atención
   - Las alertas muestran notificaciones críticas

3. **Interacción:**
   - Click en un activo en la tabla de tendencias → navega a detalles del activo
   - Click en una alerta → muestra detalles de la alerta
   - Botón "Marcar como leída" → marca la alerta como leída
   - Botón "Resolver" → resuelve la alerta
   - Botón "Actualizar" → recarga todos los datos del dashboard

4. **Actualización:**
   - Los datos se pueden actualizar manualmente con el botón "Actualizar"
   - Las alertas se actualizan automáticamente después de marcarlas o resolverlas

## Estilos y Colores

### Niveles de Riesgo
- **LOW (Bajo):** Verde (#10B981)
- **MEDIUM (Medio):** Ámbar (#F59E0B)
- **HIGH (Alto):** Naranja (#F97316)
- **CRITICAL (Crítico):** Rojo (#EF4444)

### Severidad de Alertas
- **INFO:** Azul
- **WARNING:** Ámbar
- **ERROR:** Naranja
- **CRITICAL:** Rojo

## Ejemplo de Uso

```typescript
import Predictions from './pages/Predictions';

// En tu router
<Route path="/predictions" element={<Predictions />} />
```

## Manejo de Errores

El dashboard incluye manejo de errores robusto:
- Muestra mensajes de error claros
- Permite reintentar la carga de datos
- Registra errores en la consola para debugging

## Responsive Design

El dashboard es completamente responsive:
- **Desktop:** Grid de 4 columnas para stats, 3 columnas para contenido principal
- **Tablet:** Grid de 2 columnas para stats, 2 columnas para contenido
- **Mobile:** Grid de 1 columna, componentes apilados verticalmente

## Próximas Mejoras

- [ ] Filtros avanzados para alertas
- [ ] Exportación de reportes
- [ ] Gráficos de tendencias temporales
- [ ] Notificaciones en tiempo real
- [ ] Configuración de umbrales de alerta
- [ ] Integración con calendario de mantenimiento
