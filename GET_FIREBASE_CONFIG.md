# Obtener Configuración de Firebase para Frontend

## 📋 Pasos para obtener la configuración

### 1. Ve a Firebase Console
https://console.firebase.google.com/

### 2. Selecciona tu proyecto
**CMMS Somacor Production** (cmms-somacor-prod)

### 3. Ve a Project Settings
- Haz clic en el ⚙️ (engranaje) junto a "Project Overview"
- O ve directamente a: https://console.firebase.google.com/project/cmms-somacor-prod/settings/general

### 4. Busca "Your apps" o "Tus apps"
- Desplázate hacia abajo hasta la sección "Your apps"
- Deberías ver una app web (ícono </>)

### 5. Si NO ves una app web:
1. Haz clic en el ícono </> (Web)
2. Dale un nombre: "CMMS Web App"
3. NO marques "Firebase Hosting"
4. Haz clic en "Register app"

### 6. Copia la configuración
Verás algo como esto:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "cmms-somacor-prod.firebaseapp.com",
  projectId: "cmms-somacor-prod",
  storageBucket: "cmms-somacor-prod.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
};
```

### 7. Pégame esos valores aquí

Una vez que me los pases, actualizaré automáticamente el archivo `frontend/.env` con la configuración correcta.

## 🔍 Valores que necesito:

- `apiKey`: AIzaSy...
- `authDomain`: cmms-somacor-prod.firebaseapp.com
- `projectId`: cmms-somacor-prod
- `storageBucket`: cmms-somacor-prod.appspot.com
- `messagingSenderId`: 123456789012
- `appId`: 1:123456789012:web:...

## 📝 Nota

Estos valores son seguros para compartir - son públicos y están diseñados para usarse en el frontend. No son credenciales secretas.
