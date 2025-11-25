# 🚀 GUÍA RÁPIDA - Cargar Datos en 10 Minutos

## Paso 1: Acceder al Admin (1 min)

1. Abre tu navegador
2. Ve a: **https://cmms-backend-ufxpd3tbia-uc.a.run.app/admin/**
3. Login:
   - Email: `admin@cmms.com`
   - Password: `admin123`

---

## Paso 2: Crear Ubicaciones (2 min)

1. Click en **"Locations"** (Ubicaciones)
2. Click en **"ADD LOCATION"** (botón verde arriba a la derecha)
3. Crea estas 3 ubicaciones:

### Ubicación 1:
- **Name:** `Faena La Coipa`
- **Address:** `Región de Atacama`
- **Description:** `Faena principal`
- Click **SAVE**

### Ubicación 2:
- **Name:** `Taller Mecánico`
- **Address:** `Faena La Coipa`
- **Description:** `Taller`
- Click **SAVE**

### Ubicación 3:
- **Name:** `Patio de Equipos`
- **Address:** `Faena La Coipa`
- **Description:** `Patio`
- Click **SAVE**

---

## Paso 3: Crear Activos (5 min)

1. Click en **"Assets"** (Activos/Vehículos)
2. Click en **"ADD ASSET"**
3. Crea estos 5 activos (copia y pega los datos):

### Activo 1: Camión Supersucker
```
Name: Camión Supersucker SS-001
Asset code: SS-001
Vehicle type: Camión Supersucker
Location: Faena La Coipa
Manufacturer: Volvo
Model: FMX 500
Serial number: VLV2023SS001
License plate: HJKL-12
Status: Operativo
Criticality: Crítica
```

### Activo 2: Camioneta
```
Name: Camioneta MDO CM-001
Asset code: CM-001
Vehicle type: Camioneta MDO
Location: Faena La Coipa
Manufacturer: Toyota
Model: Hilux 4x4
Serial number: TOY2023CM001
License plate: ABCD-34
Status: Operativo
Criticality: Alta
```

### Activo 3: Retroexcavadora
```
Name: Retroexcavadora RE-001
Asset code: RE-001
Vehicle type: Retroexcavadora MDO
Location: Faena La Coipa
Manufacturer: Caterpillar
Model: 420F2
Serial number: CAT2022RE001
License plate: WXYZ-56
Status: Operativo
Criticality: Alta
```

### Activo 4: Cargador Frontal
```
Name: Cargador Frontal CF-001
Asset code: CF-001
Vehicle type: Cargador Frontal MDO
Location: Faena La Coipa
Manufacturer: Komatsu
Model: WA320-8
Serial number: KOM2023CF001
License plate: PQRS-78
Status: Operativo
Criticality: Crítica
```

### Activo 5: Minicargador
```
Name: Minicargador MC-001
Asset code: MC-001
Vehicle type: Minicargador MDO
Location: Faena La Coipa
Manufacturer: Bobcat
Model: S650
Serial number: BOB2023MC001
License plate: MNOP-90
Status: Operativo
Criticality: Media
```

---

## Paso 4: Crear Órdenes de Trabajo (2 min)

1. Click en **"Work Orders"** (Órdenes de Trabajo)
2. Click en **"ADD WORK ORDER"**
3. Crea estas 2 órdenes:

### Orden 1:
```
Title: Mantenimiento Preventivo SS-001
Description: Revisión de 500 horas
Asset: Camión Supersucker SS-001
Work order type: Preventive
Priority: High
Status: Pending
Created by: admin@cmms.com
```

### Orden 2:
```
Title: Reparación Hidráulica RE-001
Description: Fuga en cilindro
Asset: Retroexcavadora RE-001
Work order type: Corrective
Priority: Urgent
Status: In Progress
Created by: admin@cmms.com
```

---

## ✅ LISTO!

Ahora ve al frontend y verifica:

**Frontend:** https://cmms-somacor-produccion.web.app/

1. **Dashboard** - Debería mostrar:
   - 5 activos
   - 2 órdenes de trabajo
   - Gráficos con datos

2. **Checklists** - Debería:
   - Permitir seleccionar activos
   - Mostrar los 5 vehículos

3. **Activos** - Debería:
   - Listar los 5 activos
   - Mostrar detalles de cada uno

---

## 🎯 Resumen de lo Creado

| Tipo | Cantidad |
|------|----------|
| Ubicaciones | 3 |
| Activos | 5 |
| Órdenes | 2 |

**Tiempo total:** ~10 minutos

---

## 📸 Capturas para Wireframes

Después de cargar los datos, toma capturas de:

1. **Dashboard** - Con KPIs y gráficos
2. **Lista de Activos** - Tabla con los 5 vehículos
3. **Detalle de Activo** - Vista de un vehículo específico
4. **Checklist** - Formulario con activo seleccionado
5. **Órdenes de Trabajo** - Lista con las 2 órdenes

---

## ❓ Problemas?

- **No puedo acceder al admin:** Verifica la URL y credenciales
- **No aparece "Locations":** Scroll down en el menú del admin
- **Error al guardar activo:** Asegúrate de seleccionar una ubicación
- **Dashboard sigue vacío:** Refresca la página (Ctrl+F5)

---

**¡Éxito!** 🎉
