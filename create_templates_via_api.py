import requests
import json

# Backend URL
BACKEND_URL = "https://cmms-backend-232652686658.us-central1.run.app"

# Templates data
templates = [
    {
        "code": "CHK-CSS",
        "name": "Checklist Camión Supersucker",
        "vehicle_type": "CAMION_SUPERSUCKER",
        "description": "Plantilla de checklist para Checklist Camión Supersucker",
        "items": [
            {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Motor", "order": 2, "question": "Nivel de refrigerante", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Sistema Hidráulico", "order": 3, "question": "Nivel de aceite hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Sistema Hidráulico", "order": 4, "question": "Fugas en mangueras", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Neumáticos", "order": 5, "question": "Presión de neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Seguridad", "order": 6, "question": "Luces funcionando", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
        ],
        "is_system_template": True,
        "passing_score": 80
    },
    {
        "code": "CHK-CMD",
        "name": "Checklist Camioneta MDO",
        "vehicle_type": "CAMIONETA_MDO",
        "description": "Plantilla de checklist para Checklist Camioneta MDO",
        "items": [
            {"section": "Motor", "order": 1, "question": "Nivel de aceite", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Frenos", "order": 2, "question": "Nivel de líquido de frenos", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Neumáticos", "order": 3, "question": "Estado de neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Seguridad", "order": 4, "question": "Cinturones de seguridad", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
        ],
        "is_system_template": True,
        "passing_score": 80
    },
    {
        "code": "CHK-RMD",
        "name": "Checklist Retroexcavadora MDO",
        "vehicle_type": "RETROEXCAVADORA_MDO",
        "description": "Plantilla de checklist para Checklist Retroexcavadora MDO",
        "items": [
            {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Hidráulico", "order": 2, "question": "Nivel de aceite hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Hidráulico", "order": 3, "question": "Estado de cilindros", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Estructura", "order": 4, "question": "Estado de brazos y cucharón", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
        ],
        "is_system_template": True,
        "passing_score": 80
    },
    {
        "code": "CHK-CFM",
        "name": "Checklist Cargador Frontal MDO",
        "vehicle_type": "CARGADOR_FRONTAL_MDO",
        "description": "Plantilla de checklist para Checklist Cargador Frontal MDO",
        "items": [
            {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Transmisión", "order": 2, "question": "Nivel de aceite transmisión", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Hidráulico", "order": 3, "question": "Sistema hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Neumáticos", "order": 4, "question": "Estado de neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
        ],
        "is_system_template": True,
        "passing_score": 80
    },
    {
        "code": "CHK-MCM",
        "name": "Checklist Minicargador MDO",
        "vehicle_type": "MINICARGADOR_MDO",
        "description": "Plantilla de checklist para Checklist Minicargador MDO",
        "items": [
            {"section": "Motor", "order": 1, "question": "Nivel de aceite", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Hidráulico", "order": 2, "question": "Sistema hidráulico", "response_type": "yes_no_na", "required": True, "observations_allowed": True},
            {"section": "Orugas/Neumáticos", "order": 3, "question": "Estado de orugas/neumáticos", "response_type": "yes_no_na", "required": True, "observations_allowed": True}
        ],
        "is_system_template": True,
        "passing_score": 80
    }
]

# First, login to get a token
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

# Create templates
for template in templates:
    print(f"\nCreating template: {template['code']}")
    response = requests.post(
        f"{BACKEND_URL}/api/v1/checklists/templates/",
        headers=headers,
        json=template
    )
    
    if response.status_code in [200, 201]:
        print(f"✓ Created: {template['name']}")
    elif response.status_code == 400 and "already exists" in response.text.lower():
        print(f"  Template already exists: {template['name']}")
    else:
        print(f"✗ Error creating {template['name']}: {response.status_code} - {response.text}")

print("\n✓ Done!")
