"""
Script para probar endpoints disponibles
"""
import requests

BACKEND_URL = "https://cmms-backend-888881509782.us-central1.run.app"

# Login
response = requests.post(
    f"{BACKEND_URL}/api/v1/auth/login/",
    json={"email": "admin@cmms.com", "password": "admin123"}
)

token = response.json()["access"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Probar endpoints
endpoints = [
    ("GET", "/api/v1/assets/"),
    ("GET", "/api/v1/assets/locations/"),
    ("POST", "/api/v1/assets/locations/", {"name": "Test", "code": "TEST"}),
    ("GET", "/api/v1/auth/users/"),
    ("GET", "/api/v1/inventory/spare-parts/"),
    ("GET", "/api/v1/work-orders/"),
    ("GET", "/api/v1/maintenance/plans/"),
]

print("Probando endpoints...\n")

for method, endpoint, *data in endpoints:
    url = f"{BACKEND_URL}{endpoint}"
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data[0] if data else {})
    
    print(f"{method} {endpoint}")
    print(f"  Status: {response.status_code}")
    if response.status_code not in [200, 201]:
        print(f"  Error: {response.text[:200]}")
    print()
