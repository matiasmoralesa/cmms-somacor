# Guía de Optimización de Performance - Frontend

## Optimizaciones Implementadas

### 1. Build Optimizations

#### Code Splitting
- Vendor chunks separados (React, Charts, Utils)
- Lazy loading de rutas
- Dynamic imports para componentes pesados

#### Minification
- Terser para minificación de JavaScript
- Eliminación de console.log en producción
- Tree shaking automático

### 2. Runtime Optimizations

#### React Optimizations
```typescript
// Usar React.memo para componentes que no cambian frecuentemente
const MyComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
});

// Usar useMemo para cálculos costosos
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// Usar useCallback para funciones que se pasan como props
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);
```

#### Custom Hooks
- `useDebounce`: Debounce de valores (búsqueda, filtros)
- `useIntersectionObserver`: Lazy loading e infinite scroll
- `useLocalStorage`: Persistencia con sincronización entre tabs

### 3. Image Optimization

#### LazyImage Component
```typescript
import LazyImage from '@/components/common/LazyImage';

<LazyImage
  src="/path/to/image.jpg"
  alt="Description"
  className="w-full h-auto"
/>
```

#### Mejores Prácticas
- Usar formatos modernos (WebP, AVIF)
- Comprimir imágenes antes de subir
- Usar tamaños apropiados (no cargar 4K para thumbnails)
- Implementar placeholders mientras cargan

### 4. API Optimization

#### Request Caching
```typescript
// Usar React Query o SWR para caching automático
import { useQuery } from 'react-query';

const { data, isLoading } = useQuery('assets', fetchAssets, {
  staleTime: 5 * 60 * 1000, // 5 minutos
  cacheTime: 10 * 60 * 1000, // 10 minutos
});
```

#### Debouncing
```typescript
import { useDebounce } from '@/hooks/useDebounce';

const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebounce(searchTerm, 500);

useEffect(() => {
  if (debouncedSearch) {
    performSearch(debouncedSearch);
  }
}, [debouncedSearch]);
```

### 5. Bundle Size Optimization

#### Análisis de Bundle
```bash
# Analizar tamaño del bundle
npm run build
npx vite-bundle-visualizer

# Ver tamaño de chunks
ls -lh dist/assets/
```

#### Reducir Tamaño
- Importar solo lo necesario de librerías grandes
- Usar alternativas más ligeras cuando sea posible
- Lazy load de componentes no críticos

```typescript
// ❌ Malo - importa toda la librería
import _ from 'lodash';

// ✅ Bueno - importa solo lo necesario
import debounce from 'lodash/debounce';

// ✅ Mejor - usa alternativa nativa
const debounce = (fn, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};
```

### 6. Rendering Optimization

#### Virtualization
Para listas largas, usar virtualización:

```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>{items[index]}</div>
  )}
</FixedSizeList>
```

#### Pagination
Preferir paginación sobre infinite scroll para datasets grandes:

```typescript
const [page, setPage] = useState(1);
const pageSize = 20;

const { data } = useQuery(['items', page], () => 
  fetchItems({ page, pageSize })
);
```

### 7. Network Optimization

#### Prefetching
```typescript
// Prefetch de datos que probablemente se necesitarán
const queryClient = useQueryClient();

const handleMouseEnter = () => {
  queryClient.prefetchQuery('asset-details', fetchAssetDetails);
};
```

#### Request Batching
```typescript
// Agrupar múltiples requests en uno solo
const fetchMultiple = async (ids: string[]) => {
  return api.post('/batch', { ids });
};
```

### 8. State Management

#### Evitar Re-renders Innecesarios
```typescript
// ❌ Malo - causa re-render en cada cambio
const [state, setState] = useState({ a: 1, b: 2, c: 3 });

// ✅ Bueno - solo re-render cuando cambia lo necesario
const [a, setA] = useState(1);
const [b, setB] = useState(2);
const [c, setC] = useState(3);
```

#### Context Optimization
```typescript
// Dividir contextos grandes en contextos más pequeños
// ❌ Malo - un contexto para todo
<AppContext.Provider value={{ user, settings, data }}>

// ✅ Bueno - contextos separados
<UserContext.Provider value={user}>
  <SettingsContext.Provider value={settings}>
    <DataContext.Provider value={data}>
```

## Métricas de Performance

### Core Web Vitals

#### LCP (Largest Contentful Paint)
- **Objetivo:** < 2.5s
- **Optimizaciones:**
  - Optimizar imágenes
  - Usar CDN
  - Implementar SSR/SSG si es necesario

#### FID (First Input Delay)
- **Objetivo:** < 100ms
- **Optimizaciones:**
  - Code splitting
  - Lazy loading
  - Reducir JavaScript bloqueante

#### CLS (Cumulative Layout Shift)
- **Objetivo:** < 0.1
- **Optimizaciones:**
  - Especificar dimensiones de imágenes
  - Reservar espacio para contenido dinámico
  - Evitar insertar contenido sobre contenido existente

### Herramientas de Medición

```bash
# Lighthouse
npm install -g lighthouse
lighthouse https://your-app.com --view

# Web Vitals
npm install web-vitals
```

```typescript
// Medir Web Vitals en la app
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

## Checklist de Performance

### Antes de Deploy

- [ ] Analizar bundle size
- [ ] Verificar que no hay console.log en producción
- [ ] Comprobar que las imágenes están optimizadas
- [ ] Verificar que el código está minificado
- [ ] Probar en conexión lenta (3G)
- [ ] Verificar Core Web Vitals
- [ ] Comprobar que lazy loading funciona
- [ ] Verificar que el caching está configurado

### Monitoreo Continuo

- [ ] Configurar alertas de performance
- [ ] Monitorear bundle size en CI/CD
- [ ] Revisar métricas de usuarios reales
- [ ] Analizar reportes de Lighthouse periódicamente

## Recursos

- [Web.dev Performance](https://web.dev/performance/)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Vite Performance](https://vitejs.dev/guide/performance.html)
- [Bundle Phobia](https://bundlephobia.com/) - Analizar tamaño de paquetes npm
