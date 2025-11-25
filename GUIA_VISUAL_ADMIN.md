# 🎯 GUÍA VISUAL - Admin Django (10 minutos)

## 🔐 PASO 1: Login (1 min)

1. **URL:** https://cmms-backend-888881509782.us-central1.run.app/admin/
2. **Email:** `admin@cmms.com`
3. **Password:** `admin123`
4. Click **"Log in"**

---

## 📍 PASO 2: Crear Ubicaciones (2 min)

### Ubicación 1:
1. En el menú lateral, busca **"ASSETS"** → **"Locations"**
2. Click botón verde **"ADD LOCATION +"** (arriba derecha)
3. Llena el formulario:
   ```
   Name: Faena La Coipa
   Address: Región de Atacama
   Description: Faena principal Gold Fields
   Is active: ✓ (checked)
   ```
4. Click **"SAVE"** (abajo)

### Ubicación 2:
1. Click **"ADD LOCATION +"** nuevamente
2. Llena:
   ```
   Name: Taller Mecánico
   Address: Faena La Coipa
   Description: Taller de mantenimiento
   Is active: ✓
   ```
3. Click **"SAVE"**

### Ubicación 3:
1. Click **"ADD LOCATION +"**
2. Llena:
   ```
   Name: Patio de Equipos
   Address: Faena La Coipa
   Description: Área de estacionamiento
   Is active: ✓
   ```
3. Click **"SAVE"**

✅ **Verificación:** Deberías ver 3 ubicaciones en la lista

---

## 🚛 PASO 3: Crear Activos (5 min)

### Activo 1: Camión Supersucker
1. En el menú lateral: **"ASSETS"** → **"Assets"**
2. Click **"ADD ASSET +"**
3. Llena el formulario:
   ```
   Name: Camión Supersucker SS-001
   Asset code: SS-001
   Vehicle type: Camión Supersucker (selecciona del dropdown)
   Location: Faena La Coipa (selecciona del dropdown)
   Manufacturer: Volvo
   Model: FMX 500
   Serial number: VLV2023SS001
   License plate: HJKL-12
   Status: Operativo (selecciona del dropdown)
   Criticality: Crítica (selecciona del dropdown)
   Is active: ✓
   ```
4. Click **"SAVE"**

### Activo 2: Camioneta
1. Click **"ADD ASSET +"**
2. Llena:
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
   Is active: ✓
   ```
3. Click **"SAVE"**

### Activo 3: Retroexcavadora
1. Click **"ADD ASSET +"**
2. Llena:
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
   Is active: ✓
   ```
3. Click **"SAVE"**

### Activo 4: Cargador Frontal
1. Click **"ADD ASSET +"**
2. Llena:
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
   Is active: ✓
   ```
3. Click **"SAVE"**

### Activo 5: Minicargador
1. Click **"ADD ASSET +"**
2. Llena:
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
   Is active: ✓
   ```
3. Click **"SAVE"**

✅ **Verificación:** Deberías ver 5 activos en la lista

---

## 📋 PASO 4: Crear Órdenes de Trabajo (2 min)

### Orden 1:
1. En el menú lateral: **"WORK ORDERS"** → **"Work orders"**
2. Click **"ADD WORK ORDER +"**
3. Llena:
   ```
   Title: Mantenimiento Preventivo SS-001
   Description: Revisión programada de 500 horas
   Asset: Camión Supersucker SS-001 (selecciona del dropdown)
   Work order type: Preventive
   Priority: High
   Status: Pending
   Created by: admin@cmms.com (selecciona del dropdown)
   ```
4. Click **"SAVE"**

### Orden 2:
1. Click **"ADD WORK ORDER +"**
2. Llena:
   ```
   Title: Reparación Hidráulica RE-001
   Description: Fuga detectada en cilindro principal
   Asset: Retroexcavadora RE-001
   Work order type: Corrective
   Priority: Urgent
   Status: In Progress
   Created by: admin@cmms.com
   ```
3. Click **"SAVE"**

✅ **Verificación:** Deberías ver 2 órdenes en la lista

---

## 🎉 PASO 5: Verificar en el Frontend

1. Abre: https://cmms-somacor-produccion.web.app/
2. Login: `admin@cmms.com` / `admin123`
3. Verifica:
   - ✅ **Dashboard** muestra datos
   - ✅ **Activos** lista los 5 vehículos
   - ✅ **Checklists** permite seleccionar activos
   - ✅ **Órdenes** muestra las 2 órdenes

---

## 📸 PASO 6: Tomar Capturas para Wireframes

Toma screenshots de:

1. **Dashboard completo** (con KPIs y gráficos)
2. **Lista de Activos** (tabla con los 5 vehículos)
3. **Detalle de un Activo** (click en uno)
4. **Formulario de Checklist** (con activo seleccionado)
5. **Lista de Órdenes de Trabajo**
6. **Formulario de Orden de Trabajo**

---

## ⚠️ TIPS IMPORTANTES

- **Campos obligatorios:** Tienen asterisco rojo (*)
- **Dropdowns:** Click en la flecha para ver opciones
- **Errores:** Aparecen en rojo arriba del formulario
- **Guardar:** Siempre click en "SAVE" al final
- **Volver:** Click en el nombre del modelo en la breadcrumb

---

## 🆘 Problemas Comunes

### "This field is required"
→ Llena todos los campos con asterisco (*)

### "Asset with this Asset code already exists"
→ Cambia el código (ej: SS-002 en vez de SS-001)

### No veo "Locations" en el menú
→ Scroll down en el menú lateral izquierdo

### Error 403 CSRF
→ Refresca la página (F5) y vuelve a intentar

---

## ✅ CHECKLIST FINAL

- [ ] 3 Ubicaciones creadas
- [ ] 5 Activos creados
- [ ] 2 Órdenes de Trabajo creadas
- [ ] Dashboard carga con datos
- [ ] Checklists funcionan
- [ ] Capturas tomadas para wireframes

---

**Tiempo total:** ~10 minutos  
**Dificultad:** Fácil  
**Resultado:** Sistema con datos reales para demos y wireframes

¡Éxito! 🎉
