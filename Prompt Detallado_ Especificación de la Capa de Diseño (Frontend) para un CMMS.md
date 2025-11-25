# Prompt Detallado: Especificación de la Capa de Diseño (Frontend) para un CMMS

## 🎯 Objetivo del Diseño

Crear la **Capa de Diseño (Frontend)** completa para un Sistema de Gestión de Mantenimiento Computarizado (CMMS) avanzado. El diseño debe replicar el estilo visual, la estructura de componentes y la experiencia de usuario de una aplicación moderna de gestión empresarial (SaaS/Dashboard), tal como se observa en el proyecto `cmms-somacorv2`.

## 🛠️ Stack Tecnológico de Diseño

El diseño debe ser implementado utilizando el siguiente stack tecnológico para el frontend:

| Componente | Tecnología Requerida | Propósito |
| :--- | :--- | :--- |
| **Framework UI** | **React** (versión 18+ o 19+) | Base para la construcción de la Interfaz de Usuario (SPA). |
| **Lenguaje** | **TypeScript** | Tipado estático para mayor robustez del código. |
| **Estilización** | **Tailwind CSS** | Framework de utilidad-first para un diseño rápido y responsivo. |
| **Componentes Base** | **Radix UI Primitives** | Librería de componentes sin estilo para construir elementos accesibles y funcionales (ej. modales, menús, botones). |
| **Visualización de Datos** | **recharts** o **Nivo** | Librería para la creación de gráficos interactivos en el Dashboard. |

## 🎨 Especificaciones de Estilo Visual y Paleta de Colores

El diseño debe ser **moderno, limpio y de alto contraste**, optimizado para largas jornadas de uso en un entorno de gestión industrial.

### 1. Estilo General

*   **Look & Feel:** Profesional, funcional, con una estética de aplicación de gestión de datos (Dashboard/SaaS).
*   **Diseño Responsivo:** El layout debe ser completamente responsivo y funcional en dispositivos de escritorio y tabletas.
*   **Layout:** Utilizar un layout de dashboard estándar con una barra lateral de navegación (posiblemente oscura) y un área de contenido principal (clara).

### 2. Paleta de Colores

*   **Fondo Principal:** Utilizar un esquema de alto contraste. Se recomienda un **fondo oscuro** (gris oscuro o negro) para la barra lateral y el encabezado, y un **fondo claro** (blanco o gris muy claro) para el área de contenido principal y las tarjetas.
*   **Color de Acento:** Un color primario vibrante (ej. azul eléctrico, verde lima) para botones principales, enlaces y elementos interactivos.
*   **Codificación de Colores para Estado (KPIs e Indicadores):**
    *   **Verde:** Estado OK, Tarea Completada, Cumplimiento.
    *   **Amarillo/Naranja:** Advertencia, Pendiente, Alerta Predictiva (Próximo a fallar).
    *   **Rojo:** Crítico, Falla, Tarea Vencida.

### 3. Tipografía

*   **Fuente:** Una fuente sans-serif moderna y altamente legible (ej. Inter, Roboto, o similar) para garantizar la claridad de los datos.

## 🖼️ Componentes y Vistas Clave

El diseño debe incluir la maqueta (mockup) y la implementación de los siguientes componentes de interfaz:

1.  **Dashboard Principal:**
    *   Tarjetas de métricas grandes y claras (KPIs: MTBF, MTTR, Órdenes Abiertas).
    *   Gráficos interactivos (usando `recharts`) que muestren tendencias de fallas y cumplimiento de mantenimiento.
2.  **Tabla de Gestión de Equipos/Activos:**
    *   Tabla de datos con filtros, búsqueda y paginación.
    *   Fila de equipo con indicadores de estado codificados por color.
3.  **Formulario de Creación/Edición de Órdenes de Trabajo (OT):**
    *   Formulario limpio y estructurado, preferiblemente en un modal o barra lateral.
    *   Uso de componentes de Radix UI para selectores y campos de entrada.
4.  **Barra de Navegación Lateral:**
    *   Iconografía clara para cada módulo (Equipos, OTs, Inventario, Reportes, IA).
    *   Diseño que soporte el sistema de roles (aunque la lógica de permisos no es necesaria en el diseño, el layout debe contemplarla).
5.  **Sistema de Notificaciones:**
    *   Componente de "Toast" o "Banner" para mostrar alertas en tiempo real (ej. "Alerta de Falla Predictiva").
