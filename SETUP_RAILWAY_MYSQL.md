# 🚀 Configurar Railway MySQL - Guía Rápida

## Paso 1: Agregar MySQL a Railway (1 minuto)

1. Ve a tu proyecto en Railway: https://railway.app
2. Abre tu proyecto (donde está tu backend)
3. Click en **"+ New"** (botón morado arriba a la derecha)
4. Selecciona **"Database"**
5. Click en **"Add MySQL"**
6. Espera 30 segundos mientras se crea

---

## Paso 2: Verificar Variables (30 segundos)

Railway automáticamente crea estas variables en tu servicio web:

```
DATABASE_URL=mysql://root:password@containers.railway.app:port/railway
MYSQLHOST=containers.railway.app
MYSQLPORT=XXXX
MYSQLUSER=root
MYSQLPASSWORD=XXXXXXXXXX
MYSQLDATABASE=railway
```

**No necesitas hacer nada**, Railway las conecta automáticamente.

---

## Paso 3: Verificar Conexión (Opcional)

1. Ve a tu servicio **web** en Railway
2. Click en **"Variables"**
3. Verifica que existan las variables MySQL

Si no aparecen automáticamente:
1. Ve al servicio MySQL
2. Click en **"Connect"**
3. Selecciona tu servicio web
4. Railway las agregará automáticamente

---

## Paso 4: Redesplegar (30 segundos)

Railway redesplega automáticamente cuando detecta la nueva BD.

Si no lo hace:
1. Ve a tu servicio web
2. Click en **"Deployments"**
3. Click en **"Deploy"** (o espera el auto-deploy)

---

## Paso 5: Verificar Logs (1 minuto)

En los logs de tu servicio web busca:

```
✅ "Running migrations..."
✅ "Superusuario admin@somacor.cl creado"
✅ "Listening at: http://0.0.0.0:8080"
```

---

## 💰 Costo

- **MySQL Database:** $5/mes
- **Backend (web service):** Incluido en tu plan actual
- **Total:** $5/mes

---

## 📊 Incluye

- 1GB storage
- Backups automáticos
- Alta disponibilidad
- Monitoreo
- Métricas

---

## 🎉 ¡Listo!

Tu aplicación ahora tiene:
- ✅ Backend en Railway
- ✅ Base de datos MySQL en Railway
- ✅ Todo conectado automáticamente
- ✅ Variables configuradas
- ✅ Listo para usar

---

## 🆘 Si Algo Sale Mal

### Error: "Can't connect to MySQL"
- Verifica que las variables existan en el servicio web
- Reconecta la BD desde el panel de MySQL

### Error: "Access denied"
- Railway debería configurar esto automáticamente
- Si persiste, verifica MYSQLUSER y MYSQLPASSWORD

### No veo las variables
- Ve al servicio MySQL → Connect → Selecciona tu servicio web

---

¡Empecemos!
