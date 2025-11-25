"""
Script para probar el endpoint dashboard_summary y ver el error específico
"""
import requests
import json

# URL del backend
BASE_URL = "https://cmms-backend-888881509782.us-central1.run.app/api/v1"

# 1. Login para obtener token
print("1. Obteniendo token de autenticación...")
login_response = requests.post(
    f"{BASE_URL}/auth/login/",
    json={"email": "admin@cmms.com", "password": "admin123"},
    headers={"Content-Type": "application/json"}
)

if login_response.status_code == 200:
    token = login_response.json()["access"]
    print(f"✓ Token obtenido: {token[:20]}...")
else:
    print(f"✗ Error en login: {login_response.status_code}")
    print(login_response.text)
    exit(1)

# 2. Probar endpoint dashboard_summary
print("\n2. Probando endpoint dashboard_summary...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

dashboard_response = requests.get(
    f"{BASE_URL}/reports/dashboard_summary/",
    headers=headers
)

print(f"Status Code: {dashboard_response.status_code}")
print(f"Response:")
print(json.dumps(dashboard_response.json(), indent=2))

if dashboard_response.status_code != 200:
    print("\n✗ Error detectado!")
    print(f"Detalles: {dashboard_response.text}")
else:
    print("\n✓ Endpoint funcionando correctamente!")
