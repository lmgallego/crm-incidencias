CREATE TABLE IF NOT EXISTS coordinators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surnames TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surnames TEXT NOT NULL,
    phone TEXT,
    zone TEXT
);

CREATE TABLE IF NOT EXISTS warehouses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    codigo_consejo TEXT,
    zone TEXT
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incident_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    registering_coordinator_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    causing_verifier_id INTEGER NOT NULL,
    incident_id INTEGER NOT NULL,
    assigned_coordinator_id INTEGER NOT NULL,
    explanation TEXT,
    status TEXT NOT NULL,
    responsible TEXT NOT NULL,
    FOREIGN KEY (registering_coordinator_id) REFERENCES coordinators(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (causing_verifier_id) REFERENCES verifiers(id),
    FOREIGN KEY (incident_id) REFERENCES incidents(id),
    FOREIGN KEY (assigned_coordinator_id) REFERENCES coordinators(id)
);

CREATE TABLE IF NOT EXISTS incident_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_record_id INTEGER NOT NULL,
    action_date DATE NOT NULL,
    action_description TEXT NOT NULL,
    new_status TEXT,
    performed_by INTEGER NOT NULL,
    FOREIGN KEY (incident_record_id) REFERENCES incident_records(id),
    FOREIGN KEY (performed_by) REFERENCES coordinators(id)
);

CREATE INDEX IF NOT EXISTS idx_warehouses_zone ON warehouses(zone);
CREATE INDEX IF NOT EXISTS idx_verifiers_zone ON verifiers(zone);
CREATE INDEX IF NOT EXISTS idx_incident_records_status ON incident_records(status);
CREATE INDEX IF NOT EXISTS idx_incident_records_warehouse_id ON incident_records(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_incident_records_causing_verifier_id ON incident_records(causing_verifier_id);
CREATE INDEX IF NOT EXISTS idx_incident_records_incident_id ON incident_records(incident_id);