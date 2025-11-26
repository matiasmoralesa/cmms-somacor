# Migración de PostgreSQL a MySQL

## ✅ Cambios Realizados

1. **Requirements actualizados**:
   - ❌ Removido: `psycopg2-binary` (PostgreSQL)
   - ✅ Agregado: `mysqlclient` (MySQL)

2. **Configuración de Railway actualizada**:
   - Soporte para variables MySQL de Railway
   - Soporte para `DATABASE_URL` en formato MySQL

---

## 🚀 Opciones de Base de Datos MySQL

### Opción 1: Railway MySQL ($10/mes)

**Pasos:**
1. Ve a tu proyecto en Railway
2. Click **"+ New"** → **"Database"** → **"Add MySQL"**
3. Railway creará automáticamente estas variables:
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`
   - `DATABASE_URL` (formato MySQL)

4. Redesplegar automáticamente

**Costo:** $10/mes
- 10GB storage
- Backups automáticos
- Alta disponibilidad

---

### Opción 2: PlanetScale (GRATIS)

**Mejor opción gratuita para MySQL:**

1. Ve a https://planetscale.com
2. Crea una cuenta (gratis)
3. Crea una nueva base de datos
4. Obtén la connection string

**Plan Gratis incluye:**
- ✅ 5GB storage
- ✅ 1 billion row reads/mes
- ✅ 10 million row writes/mes
- ✅ Backups automáticos
- ✅ Branching de BD (como Git!)
- ✅ Sin tarjeta de crédito

**Connection String:**
```
mysql://user:password@host.us-east-3.psdb.cloud/database?sslaccept=strict
```

5. En Railway, agrega la variable de entorno:
   ```
   DATABASE_URL=mysql://user:password@host.psdb.cloud/database?sslaccept=strict
   ```

---

### Opción 3: Aiven MySQL (GRATIS)

**Otra opción gratuita:**

1. Ve a https://aiven.io
2. Crea cuenta gratis
3. Crea servicio MySQL (Free tier)

**Plan Gratis:**
- ✅ 1GB storage
- ✅ Backups automáticos
- ✅ SSL incluido
- ✅ 30 días gratis, luego $9/mes

---

### Opción 4: MySQL Local (NO RECOMENDADO)

Si insistes en usar MySQL local:

**Requisitos:**
1. MySQL instalado en tu PC
2. IP estática o servicio como ngrok
3. Configurar firewall y router
4. PC encendida 24/7

**Variables de entorno en Railway:**
```
MYSQLHOST=tu-ip-publica
MYSQLPORT=3306
MYSQLUSER=tu_usuario
MYSQLPASSWORD=tu_password
MYSQLDATABASE=cmms_db
```

**⚠️ Problemas:**
- IP dinámica cambia constantemente
- Latencia alta
- Seguridad comprometida
- Sin backups automáticos
- PC debe estar siempre encendida

---

## 🎯 Mi Recomendación

**1. PlanetScale (GRATIS)** - Mejor opción
   - Gratis para siempre
   - 5GB storage
   - Profesional y confiable
   - Branching de BD

**2. Railway MySQL ($10/mes)** - Más simple
   - Todo en un lugar
   - Configuración automática
   - Mismo proveedor

**3. Aiven (GRATIS 30 días)** - Alternativa
   - Buen free tier
   - Luego $9/mes

---

## 📝 Próximos Pasos

1. **Elige tu opción de BD**
2. **Configura las variables de entorno en Railway**
3. **Commit y push los cambios**:
   ```bash
   git add -A
   git commit -m "Migrar de PostgreSQL a MySQL"
   git push origin main
   ```
4. **Railway redesplega automáticamente**
5. **Las migraciones se ejecutan automáticamente**

---

## ⚠️ Importante

- Las migraciones de Django funcionan igual en MySQL
- No necesitas cambiar código de la aplicación
- Django maneja las diferencias automáticamente
- Perderás los datos actuales (si los hay)

---

## 🆘 Si Tienes Problemas

1. Verifica las variables de entorno en Railway
2. Revisa los logs de deployment
3. Asegúrate de que el formato de `DATABASE_URL` sea correcto:
   ```
   mysql://usuario:password@host:puerto/database
   ```

¿Qué opción prefieres? Te ayudo a configurarla.
