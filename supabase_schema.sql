-- Script SQL para crear las tablas en Supabase
-- Ejecutar este script en el SQL Editor del dashboard de Supabase

-- Tabla de coordinadores
CREATE TABLE IF NOT EXISTS coordinators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surnames VARCHAR(200) NOT NULL
);

-- Tabla de verificadores
CREATE TABLE IF NOT EXISTS verifiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surnames VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    zone VARCHAR(100)
);

-- Tabla de bodegas
CREATE TABLE IF NOT EXISTS warehouses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    nif VARCHAR(50),
    zone VARCHAR(100)
);

-- Tabla de tipos de incidencias
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

-- Tabla de registros de incidencias
CREATE TABLE IF NOT EXISTS incident_records (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    registering_coordinator_id INTEGER REFERENCES coordinators(id),
    warehouse_id INTEGER REFERENCES warehouses(id),
    causing_verifier_id INTEGER REFERENCES verifiers(id),
    incident_id INTEGER REFERENCES incidents(id),
    assigned_coordinator_id INTEGER REFERENCES coordinators(id),
    explanation TEXT,
    status VARCHAR(50) DEFAULT 'Pendiente',
    responsible VARCHAR(200)
);

-- Tabla de acciones de incidencias
CREATE TABLE IF NOT EXISTS incident_actions (
    id SERIAL PRIMARY KEY,
    incident_record_id INTEGER REFERENCES incident_records(id) ON DELETE CASCADE,
    action_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action_description TEXT NOT NULL,
    new_status VARCHAR(50),
    performed_by VARCHAR(200)
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_incident_records_date ON incident_records(date);
CREATE INDEX IF NOT EXISTS idx_incident_records_status ON incident_records(status);
CREATE INDEX IF NOT EXISTS idx_incident_records_warehouse ON incident_records(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_incident_records_coordinator ON incident_records(assigned_coordinator_id);
CREATE INDEX IF NOT EXISTS idx_incident_actions_record ON incident_actions(incident_record_id);
CREATE INDEX IF NOT EXISTS idx_incident_actions_date ON incident_actions(action_date);

-- Las tablas se crean vacías, sin datos de prueba
-- Puedes agregar tus propios datos a través de la aplicación

-- Mensaje de confirmación
SELECT 'Tablas creadas exitosamente en Supabase' as resultado;