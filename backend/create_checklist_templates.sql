-- Create checklist templates for the 5 vehicle types

-- Camión Supersucker
INSERT INTO checklist_templates (id, code, name, vehicle_type, description, items, is_system_template, passing_score, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'CHK-CSS',
    'Checklist Camión Supersucker',
    'CAMION_SUPERSUCKER',
    'Plantilla de checklist para Checklist Camión Supersucker',
    '[
        {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Motor", "order": 2, "question": "Nivel de refrigerante", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Sistema Hidráulico", "order": 3, "question": "Nivel de aceite hidráulico", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Sistema Hidráulico", "order": 4, "question": "Fugas en mangueras", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Neumáticos", "order": 5, "question": "Presión de neumáticos", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Seguridad", "order": 6, "question": "Luces funcionando", "response_type": "yes_no_na", "required": true, "observations_allowed": true}
    ]'::jsonb,
    true,
    80,
    NOW(),
    NOW()
)
ON CONFLICT (code) DO NOTHING;

-- Camioneta MDO
INSERT INTO checklist_templates (id, code, name, vehicle_type, description, items, is_system_template, passing_score, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'CHK-CMD',
    'Checklist Camioneta MDO',
    'CAMIONETA_MDO',
    'Plantilla de checklist para Checklist Camioneta MDO',
    '[
        {"section": "Motor", "order": 1, "question": "Nivel de aceite", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Frenos", "order": 2, "question": "Nivel de líquido de frenos", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Neumáticos", "order": 3, "question": "Estado de neumáticos", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Seguridad", "order": 4, "question": "Cinturones de seguridad", "response_type": "yes_no_na", "required": true, "observations_allowed": true}
    ]'::jsonb,
    true,
    80,
    NOW(),
    NOW()
)
ON CONFLICT (code) DO NOTHING;

-- Retroexcavadora MDO
INSERT INTO checklist_templates (id, code, name, vehicle_type, description, items, is_system_template, passing_score, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'CHK-RMD',
    'Checklist Retroexcavadora MDO',
    'RETROEXCAVADORA_MDO',
    'Plantilla de checklist para Checklist Retroexcavadora MDO',
    '[
        {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Hidráulico", "order": 2, "question": "Nivel de aceite hidráulico", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Hidráulico", "order": 3, "question": "Estado de cilindros", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Estructura", "order": 4, "question": "Estado de brazos y cucharón", "response_type": "yes_no_na", "required": true, "observations_allowed": true}
    ]'::jsonb,
    true,
    80,
    NOW(),
    NOW()
)
ON CONFLICT (code) DO NOTHING;

-- Cargador Frontal MDO
INSERT INTO checklist_templates (id, code, name, vehicle_type, description, items, is_system_template, passing_score, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'CHK-CFM',
    'Checklist Cargador Frontal MDO',
    'CARGADOR_FRONTAL_MDO',
    'Plantilla de checklist para Checklist Cargador Frontal MDO',
    '[
        {"section": "Motor", "order": 1, "question": "Nivel de aceite motor", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Transmisión", "order": 2, "question": "Nivel de aceite transmisión", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Hidráulico", "order": 3, "question": "Sistema hidráulico", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Neumáticos", "order": 4, "question": "Estado de neumáticos", "response_type": "yes_no_na", "required": true, "observations_allowed": true}
    ]'::jsonb,
    true,
    80,
    NOW(),
    NOW()
)
ON CONFLICT (code) DO NOTHING;

-- Minicargador MDO
INSERT INTO checklist_templates (id, code, name, vehicle_type, description, items, is_system_template, passing_score, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'CHK-MCM',
    'Checklist Minicargador MDO',
    'MINICARGADOR_MDO',
    'Plantilla de checklist para Checklist Minicargador MDO',
    '[
        {"section": "Motor", "order": 1, "question": "Nivel de aceite", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Hidráulico", "order": 2, "question": "Sistema hidráulico", "response_type": "yes_no_na", "required": true, "observations_allowed": true},
        {"section": "Orugas/Neumáticos", "order": 3, "question": "Estado de orugas/neumáticos", "response_type": "yes_no_na", "required": true, "observations_allowed": true}
    ]'::jsonb,
    true,
    80,
    NOW(),
    NOW()
)
ON CONFLICT (code) DO NOTHING;
