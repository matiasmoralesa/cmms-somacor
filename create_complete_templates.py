import requests
import json

# Backend URL
BACKEND_URL = "https://cmms-backend-232652686658.us-central1.run.app"

# Login
print("Logging in...")
login_response = requests.post(
    f"{BACKEND_URL}/api/v1/auth/login/",
    json={"email": "luis.sanchez@somacor.com", "password": "password123"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("✓ Login successful")
print("\nCreating checklist templates from PDFs...")

# Template 1: Camionetas MDO (F-PR-020-CH01)
template_camionetas = {
    "code": "F-PR-020-CH01",
    "name": "Check List Camionetas MDO",
    "vehicle_type": "CAMIONETA_MDO",
    "description": "Checklist diario para Camionetas MDO",
    "is_system_template": True,
    "passing_score": 80,
    "items": []
}

# I - Auto Evaluación del Operador
items_camionetas = [
    {"section": "I - Auto Evaluación", "order": 1, "question": "Cumplo con descanso suficiente y condiciones para manejo seguro", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "I - Auto Evaluación", "order": 2, "question": "Cumplo con condiciones físicas adecuadas sin dolencias", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "I - Auto Evaluación", "order": 3, "question": "Consciente de responsabilidad al conducir", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "II - Documentación Operador", "order": 4, "question": "Licencia Municipal", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "II - Documentación Operador", "order": 5, "question": "Licencia interna de Faena", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
]

template_camionetas["items"] = items_camionetas

print(f"\nTemplate data prepared: {template_camionetas['name']}")
print(f"Total items: {len(template_camionetas['items'])}")

# Add more items for Camionetas
more_items = [
    {"section": "III - Requisitos", "order": 6, "question": "Permiso de Circulación", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 7, "question": "Revisión Técnica", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 8, "question": "Seguro Obligatorio", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 9, "question": "Cinturones de Seguridad en buen estado", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 10, "question": "Espejos interior y exterior limpios", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 11, "question": "Frenos (incluye freno de mano) operativos", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 12, "question": "Neumáticos en buen estado (incluye repuestos)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 13, "question": "Luces (Altas, Bajas, Frenos, intermitentes)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 14, "question": "Vidrios y parabrisas limpios", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "III - Requisitos", "order": 15, "question": "Gata y llave de rueda disponible", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 16, "question": "Baliza y pértiga funcionando", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 17, "question": "Radio Base funciona en todos los canales", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 18, "question": "Limpiaparabrisas funciona", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 19, "question": "Bocina en buen estado", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 20, "question": "Orden y Aseo interior", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 21, "question": "Estado carrocería y parachoques", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 22, "question": "Cuñas de seguridad (2)", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
    {"section": "IV - Complementarios", "order": 23, "question": "Aire acondicionado/calefacción", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
]

template_camionetas["items"].extend(more_items)

# Save templates to file for manual creation
templates_to_create = [template_camionetas]

with open('templates_data.json', 'w', encoding='utf-8') as f:
    json.dump(templates_to_create, f, indent=2, ensure_ascii=False)

print(f"\n✓ Templates data saved to templates_data.json")
print(f"Total templates: {len(templates_to_create)}")
print(f"Camionetas items: {len(template_camionetas['items'])}")
