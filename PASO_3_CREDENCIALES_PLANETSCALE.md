# Paso 3: Obtener Credenciales de PlanetScale

## Una vez que la BD esté creada:

### 1. En el Dashboard de tu Base de Datos

Verás algo como:
```
cmms-somacor
Status: Ready
Region: us-east-1
```

### 2. Click en "Connect"

Busca el botón "Connect" (usualmente arriba a la derecha)

### 3. Configurar la Conexión

En la ventana que se abre:

**a) Select your language/framework:**
- Selecciona: **Django** o **Python**

**b) Connect from:**
- Selecciona: **General** o **External**

**c) Branch:**
- Deja: **main**

### 4. Copiar Credenciales

Verás algo como:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cmms-somacor',
        'USER': 'xxxxxxxxxxxxxxxxx',
        'PASSWORD': 'pscale_pw_xxxxxxxxxxxxxxxxxxxxxxxxx',
        'HOST': 'aws.connect.psdb.cloud',
        'PORT': '3306',
        'OPTIONS': {
            'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}
        }
    }
}
```

### 5. Anotar Estos Valores:

```
MYSQLHOST=aws.connect.psdb.cloud
MYSQLPORT=3306
MYSQLUSER=xxxxxxxxxxxxxxxxx
MYSQLPASSWORD=pscale_pw_xxxxxxxxxxxxxxxxxxxxxxxxx
MYSQLDATABASE=cmms-somacor
```

**IMPORTANTE:** Guarda estos valores, los necesitarás para Railway.

---

## Alternativa: Connection String

Si ves una "Connection String" como:

```
mysql://user:password@aws.connect.psdb.cloud:3306/cmms-somacor?sslaccept=strict
```

También funciona. La usaremos como `DATABASE_URL` en Railway.

---

## Siguiente Paso

Una vez que tengas las credenciales, las agregaremos a Railway.
