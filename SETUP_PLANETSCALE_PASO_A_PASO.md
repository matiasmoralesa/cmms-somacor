# 🚀 Configurar PlanetScale - Guía Paso a Paso

## Paso 1: Crear Cuenta (2 minutos)

1. Ve a: **https://planetscale.com**
2. Click en **"Sign up"**
3. Opciones:
   - **GitHub** (recomendado - 1 click)
   - **Email** (requiere verificación)
4. Completa el registro

---

## Paso 2: Crear Base de Datos (1 minuto)

1. Una vez dentro, click en **"Create a database"**
2. Configuración:
   - **Name:** `cmms-somacor` (o el nombre que prefieras)
   - **Region:** `US East (Ohio)` o el más cercano
   - **Plan:** `Hobby` (gratis)
3. Click en **"Create database"**
4. Espera 30 segundos mientras se crea

---

## Paso 3: Obtener Connection String (30 segundos)

1. En tu base de datos, ve a **"Connect"**
2. Selecciona:
   - **Connect with:** `Django`
   - **Branch:** `main`
3. Verás algo como:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cmms-somacor',
        'USER': 'xxxxxxxxxx',
        'PASSWORD': 'pscale_pw_xxxxxxxxxx',
        'HOST': 'aws.connect.psdb.cloud',
        'PORT': '3306',
        'OPTIONS': {
            'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}
        }
    }
}
```

4. **COPIA estos valores** (los necesitarás)

---

## Paso 4: Configurar Railway (1 minuto)

1. Ve a tu proyecto en Railway
2. Click en tu servicio **web**
3. Ve a **Variables**
4. Agrega estas variables:

```
MYSQLHOST=aws.connect.psdb.cloud
MYSQLPORT=3306
MYSQLUSER=xxxxxxxxxx
MYSQLPASSWORD=pscale_pw_xxxxxxxxxx
MYSQLDATABASE=cmms-somacor
```

*(Usa los valores que copiaste de PlanetScale)*

5. Click en **"Add"** para cada variable

---

## Paso 5: Actualizar Configuración Django (Opcional)

PlanetScale requiere SSL. Actualiza `railway.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQLDATABASE'),
        'USER': os.getenv('MYSQLUSER'),
        'PASSWORD': os.getenv('MYSQLPASSWORD'),
        'HOST': os.getenv('MYSQLHOST'),
        'PORT': os.getenv('MYSQLPORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'ssl_mode': 'REQUIRED',
        },
    }
}
```

---

## Paso 6: Desplegar (30 segundos)

```bash
git add -A
git commit -m "Configurar PlanetScale como base de datos"
git push origin main
```

Railway redesplega automáticamente.

---

## Paso 7: Verificar (1 minuto)

1. Ve a los logs de Railway
2. Busca:
   - ✅ `"Running migrations..."`
   - ✅ `"Superusuario admin@somacor.cl creado"`
   - ✅ `"Listening at: http://0.0.0.0:8080"`

3. Si ves errores de SSL, ve al Paso 5

---

## 🎉 ¡Listo!

Tu aplicación ahora usa PlanetScale:
- ✅ Base de datos en la nube
- ✅ Backups automáticos
- ✅ 5GB gratis
- ✅ Sin mantenimiento
- ✅ Alta disponibilidad

---

## 📊 Monitorear tu Base de Datos

En PlanetScale puedes ver:
- **Insights:** Queries más lentas
- **Branches:** Crear copias de la BD
- **Backups:** Restaurar datos
- **Usage:** Cuánto espacio usas

---

## 🆘 Solución de Problemas

### Error: "SSL connection error"

Actualiza `railway.py`:
```python
'OPTIONS': {
    'ssl_mode': 'REQUIRED',
}
```

### Error: "Access denied"

Verifica las variables en Railway:
- MYSQLUSER
- MYSQLPASSWORD
- MYSQLDATABASE

### Error: "Can't connect to MySQL server"

Verifica:
- MYSQLHOST=aws.connect.psdb.cloud
- MYSQLPORT=3306

---

## 💡 Próximos Pasos

1. ✅ Configurar PlanetScale
2. ✅ Desplegar a Railway
3. ✅ Probar el login
4. ✅ Cargar datos de prueba
5. ✅ ¡Usar tu aplicación!

---

¿Listo? ¡Empieza con el Paso 1!
