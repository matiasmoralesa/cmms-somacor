# ⚠️ NOTA IMPORTANTE - Alcance de las Pruebas

## 🎯 ¿Qué se probó?

### ✅ BACKEND (APIs REST)

Las pruebas ejecutadas validaron **únicamente el backend** del sistema mediante llamadas a las APIs REST:

- Endpoints de autenticación
- Endpoints de gestión de usuarios
- Endpoints de activos y ubicaciones
- Endpoints de inventario
- Endpoints de órdenes de trabajo
- Endpoints de planes de mantenimiento
- Endpoints de checklists
- Endpoints de notificaciones

**Método**: Llamadas HTTP directas usando Python `requests`

---

## ❌ ¿Qué NO se probó?

### Frontend (Interfaz de Usuario Web)

**NO se probaron** los siguientes aspectos del frontend:

- ❌ Interfaz de usuario web (https://cmms-somacor-prod.web.app)
- ❌ Navegación entre páginas
- ❌ Formularios y validaciones en la UI
- ❌ Experiencia de usuario (UX)
- ❌ Diseño responsive (móvil, tablet, desktop)
- ❌ Funcionalidad de botones, menús y componentes
- ❌ Visualización de datos en tablas, gráficos y dashboards
- ❌ Interacciones del usuario con la aplicación
- ❌ Flujos completos de usuario (user journeys)
- ❌ Compatibilidad entre navegadores
- ❌ Rendimiento de carga de páginas
- ❌ Accesibilidad (WCAG)

---

## 📋 Pruebas Adicionales Recomendadas

### 1. Pruebas Manuales de Frontend (Urgente)

**Objetivo**: Validar que la interfaz de usuario funciona correctamente

**Casos de Prueba Sugeridos**:

#### Login y Autenticación
- [ ] Abrir https://cmms-somacor-prod.web.app
- [ ] Intentar login con credenciales correctas
- [ ] Intentar login con credenciales incorrectas
- [ ] Verificar que se muestra el dashboard después del login
- [ ] Verificar que el token se guarda correctamente
- [ ] Probar logout

#### Gestión de Activos
- [ ] Navegar a la sección de activos
- [ ] Verificar que se muestran los 5 activos
- [ ] Filtrar activos por tipo de vehículo
- [ ] Ver detalles de un activo
- [ ] Intentar crear un nuevo activo (si hay permisos)
- [ ] Intentar editar un activo existente

#### Órdenes de Trabajo
- [ ] Navegar a órdenes de trabajo
- [ ] Verificar que se muestran las 3 órdenes
- [ ] Filtrar por prioridad
- [ ] Filtrar por tipo
- [ ] Ver detalles de una orden
- [ ] Intentar crear una nueva orden
- [ ] Cambiar estado de una orden

#### Checklists
- [ ] Navegar a checklists
- [ ] Verificar que se muestran las 5 plantillas
- [ ] Seleccionar una plantilla
- [ ] Intentar completar un checklist
- [ ] Verificar que se guarda correctamente

#### Inventario
- [ ] Navegar a inventario
- [ ] Verificar si se muestran repuestos
- [ ] Intentar agregar un repuesto
- [ ] Intentar registrar un movimiento de stock

#### Notificaciones
- [ ] Verificar icono de notificaciones en navbar
- [ ] Abrir panel de notificaciones
- [ ] Verificar si hay notificaciones
- [ ] Marcar una notificación como leída

---

### 2. Pruebas de Integración Frontend-Backend

**Objetivo**: Validar que el frontend se comunica correctamente con el backend

**Casos de Prueba**:

- [ ] Verificar que el frontend usa la URL correcta del backend
- [ ] Verificar que los tokens JWT se envían correctamente
- [ ] Verificar manejo de errores 401 (no autenticado)
- [ ] Verificar manejo de errores 403 (sin permisos)
- [ ] Verificar manejo de errores 500 (error del servidor)
- [ ] Verificar que se muestran mensajes de error apropiados
- [ ] Verificar que se muestran mensajes de éxito

---

### 3. Pruebas de Usuario (UAT)

**Objetivo**: Validar que el sistema cumple con las expectativas de los usuarios finales

**Participantes Sugeridos**:
- 1 Administrador
- 1 Supervisor
- 2 Operadores

**Duración**: 2-3 horas por rol

**Escenarios**:

#### Escenario 1: Operador completa checklist diario
1. Login como operador
2. Seleccionar vehículo asignado
3. Abrir checklist correspondiente
4. Completar todas las preguntas
5. Agregar observaciones si es necesario
6. Enviar checklist
7. Verificar que se genera PDF

#### Escenario 2: Supervisor crea orden de trabajo
1. Login como supervisor
2. Navegar a órdenes de trabajo
3. Crear nueva orden preventiva
4. Asignar a un activo
5. Establecer prioridad y fecha
6. Guardar orden
7. Verificar que aparece en la lista

#### Escenario 3: Admin gestiona inventario
1. Login como admin
2. Navegar a inventario
3. Agregar nuevo repuesto
4. Registrar entrada de stock
5. Verificar alertas de stock bajo
6. Generar reporte de inventario

---

### 4. Pruebas de Compatibilidad

**Navegadores a Probar**:
- [ ] Chrome (última versión)
- [ ] Firefox (última versión)
- [ ] Safari (última versión)
- [ ] Edge (última versión)
- [ ] Chrome Mobile (Android)
- [ ] Safari Mobile (iOS)

**Dispositivos**:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

---

### 5. Pruebas de Rendimiento Frontend

**Métricas a Medir**:
- [ ] Tiempo de carga inicial
- [ ] Tiempo de carga de cada página
- [ ] Tiempo de respuesta de formularios
- [ ] Tamaño de bundle JavaScript
- [ ] Número de requests HTTP
- [ ] Uso de memoria del navegador

**Herramientas Sugeridas**:
- Google Lighthouse
- Chrome DevTools Performance
- WebPageTest

---

## 🔧 Herramientas Recomendadas para Pruebas de Frontend

### Pruebas Automatizadas
- **Cypress**: Para pruebas E2E automatizadas
- **Playwright**: Alternativa a Cypress
- **Jest + React Testing Library**: Para pruebas unitarias de componentes

### Pruebas Manuales
- **Chrome DevTools**: Para debugging
- **React DevTools**: Para inspeccionar componentes
- **Redux DevTools**: Si se usa Redux

### Pruebas de Accesibilidad
- **axe DevTools**: Extensión de Chrome
- **WAVE**: Evaluador de accesibilidad web

---

## 📊 Comparación: Backend vs Frontend Testing

| Aspecto | Backend (✅ Probado) | Frontend (❌ No Probado) |
|---------|---------------------|-------------------------|
| **Qué se prueba** | APIs REST, lógica de negocio | UI, UX, interacciones |
| **Cómo se prueba** | Llamadas HTTP directas | Navegador, clicks, formularios |
| **Herramientas** | Python requests, Postman | Cypress, Selenium, manual |
| **Cobertura actual** | 76.2% | 0% |
| **Tiempo estimado** | 2 horas (automatizado) | 8-16 horas (manual + auto) |
| **Prioridad** | ✅ Completado | 🔴 Pendiente |

---

## ⚠️ Riesgos de No Probar el Frontend

1. **Problemas de Integración**: El frontend podría no comunicarse correctamente con el backend
2. **Errores de UI**: Botones que no funcionan, formularios que no validan
3. **Problemas de UX**: Flujos confusos, navegación difícil
4. **Bugs Visuales**: Elementos mal posicionados, responsive roto
5. **Incompatibilidad**: Problemas en ciertos navegadores o dispositivos
6. **Rendimiento**: Carga lenta, aplicación que se congela

---

## ✅ Recomendación Inmediata

**Antes de considerar el sistema listo para producción**, se debe:

1. ✅ Corregir problemas del backend (ya identificados)
2. 🔴 **Realizar pruebas manuales del frontend** (2-4 horas)
3. 🟡 Ejecutar pruebas de usuario (UAT) (1 semana)
4. 🟡 Implementar pruebas automatizadas de frontend (2-3 días)

**Tiempo total estimado**: 1-2 semanas para cobertura completa

---

## 📞 Siguiente Paso Sugerido

**Opción 1: Pruebas Manuales Rápidas** (Hoy)
```
1. Abrir https://cmms-somacor-prod.web.app
2. Probar login con admin@cmms.com / admin123
3. Navegar por todas las secciones
4. Intentar crear/editar/eliminar datos
5. Documentar cualquier problema encontrado
```

**Opción 2: Crear Plan de Pruebas de Frontend** (Esta semana)
```
1. Definir casos de prueba específicos
2. Crear checklist de verificación
3. Asignar responsables
4. Ejecutar pruebas
5. Documentar resultados
```

**Opción 3: Implementar Pruebas Automatizadas** (Próximas 2 semanas)
```
1. Configurar Cypress o Playwright
2. Escribir tests E2E para flujos críticos
3. Integrar en CI/CD
4. Ejecutar en cada despliegue
```

---

**Conclusión**: Las pruebas actuales validan que el **backend funciona correctamente**, pero **no garantizan que el frontend funcione**. Se requieren pruebas adicionales del frontend antes de considerar el sistema completamente validado.

---

**Fecha**: 18 de Noviembre de 2025  
**Actualizado por**: Equipo de QA
