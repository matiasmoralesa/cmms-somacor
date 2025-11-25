"""
Script para probar login con diferentes credenciales
"""
import requests

BACKEND_URL = "https://cmms-backend-ufxpd3tbia-uc.a.run.app"

# Intentar con diferentes credenciales comunes
credentials = [
    ("admin@cmms.com", "admin123"),
    ("admin@somacor.com", "Admin123!"),
    ("luis.sanchez@somacor.com", "password123"),
]

print("Probando credenciales existentes...\n")

for email, password in credentials:
    print(f"Intentando: {email} / {password}")
    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login/",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        print(f"✓ LOGIN EXITOSO!")
        print(f"  Token: {response.json()['access'][:50]}...")
        print(f"  Usuario: {response.json().get('user', {})}")
        print("\nUsando estas credenciales para cargar datos...")
        break
    else:
        print(f"  ✗ Falló: {response.status_code}")
else:
    print("\n✗ Ninguna credencial funcionó")
    print("Necesitamos crear el usuario admin primero")
