import sqlite3
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = 'db/cavacrm.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(os.path.join('db', 'schema.sql'), 'r') as f:
        cursor.executescript(f.read())
    conn.commit()
    # Chequeo de integridad
    integrity_result = cursor.execute('PRAGMA integrity_check').fetchone()[0]
    if integrity_result != 'ok':
        logger.error(f"Integrity check failed: {integrity_result}")
        raise sqlite3.IntegrityError("Database integrity check failed")
    else:
        logger.info("Database integrity check passed")
    conn.close()

def insert_coordinator(name, surnames):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO coordinators (name, surnames) VALUES (?, ?)', (name, surnames))
        conn.commit()
        logger.info(f"Inserted coordinator: {name} {surnames}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting coordinator: {e}")
    finally:
        conn.close()

def insert_verifier(name, surnames, phone, zone):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO verifiers (name, surnames, phone, zone) VALUES (?, ?, ?, ?)', (name, surnames, phone, zone))
        conn.commit()
        logger.info(f"Inserted verifier: {name} {surnames}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting verifier: {e}")
    finally:
        conn.close()

def insert_warehouse(name, nif, zone):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO warehouses (name, nif, zone) VALUES (?, ?, ?)', (name, nif, zone))
        conn.commit()
        logger.info(f"Inserted warehouse: {name} with NIF {nif}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting warehouse: {e}")
    finally:
        conn.close()

def load_csv_to_verifiers(csv_file, sep=','):
    df = pd.read_csv(csv_file, sep=sep)
    conn = get_db_connection()
    for _, row in df.iterrows():
        name = row['name']
        surnames = row['surnames']
        cursor = conn.execute('SELECT COUNT(*) FROM verifiers WHERE name = ? AND surnames = ?', (name, surnames))
        if cursor.fetchone()[0] == 0:
            insert_verifier(name, surnames, row.get('phone', ''), row.get('zone', ''))
        else:
            print(f"Verifier {name} {surnames} already exists, skipping.")
    conn.close()

def load_csv_to_warehouses(csv_file, sep=','):
    df = pd.read_csv(csv_file, sep=sep, encoding='latin1')
    conn = get_db_connection()
    for _, row in df.iterrows():
        nif = row['nif']
        cursor = conn.execute('SELECT COUNT(*) FROM warehouses WHERE nif = ?', (nif,))
        if cursor.fetchone()[0] == 0:
            insert_warehouse(row['name'], nif, row.get('zone', ''))
        else:
            print(f"Warehouse with NIF {nif} already exists, skipping.")
    conn.close()

def insert_incident(description):
    try:
        conn = get_db_connection()
        cursor = conn.execute('SELECT COUNT(*) FROM incidents')
        count = cursor.fetchone()[0]
        code = f"{count + 1:03d}"
        conn.execute('INSERT INTO incidents (code, description) VALUES (?, ?)', (code, description))
        conn.commit()
        logger.info(f"Inserted incident with code {code}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting incident: {e}")
    finally:
        conn.close()

def get_coordinators():
    try:
        conn = get_db_connection()
        coordinators = conn.execute('SELECT id, name || " " || surnames AS full_name FROM coordinators').fetchall()
        return [(row['id'], row['full_name']) for row in coordinators]
    except sqlite3.Error as e:
        print(f"Error getting coordinators: {e}")
        return []
    finally:
        conn.close()

def get_verifiers():
    conn = get_db_connection()
    verifiers = conn.execute('SELECT id, name || " " || surnames AS full_name FROM verifiers').fetchall()
    conn.close()
    return [(row['id'], row['full_name']) for row in verifiers]

def get_warehouses():
    conn = get_db_connection()
    warehouses = conn.execute('SELECT id, name FROM warehouses').fetchall()
    conn.close()
    return [(row['id'], row['name']) for row in warehouses]

def get_incidents():
    conn = get_db_connection()
    incidents = conn.execute('SELECT id, code || " - " || description AS label FROM incidents').fetchall()
    conn.close()
    return [(row['id'], row['label']) for row in incidents]

def insert_incident_record(date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, status, responsible):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO incident_records (date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, status, responsible) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                     (date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, status, responsible))
        conn.commit()
        logger.info(f"Inserted incident record on date {date}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting incident record: {e}")
    finally:
        conn.close()

def get_incident_records():
    conn = get_db_connection()
    records = conn.execute('SELECT ir.id, ir.date, c.name || " " || c.surnames AS registering_coordinator, w.name AS warehouse, v.name || " " || v.surnames AS causing_verifier, i.code || " - " || i.description AS incident, ac.name || " " || ac.surnames AS assigned_coordinator, ir.explanation, ir.status, ir.responsible FROM incident_records ir JOIN coordinators c ON ir.registering_coordinator_id = c.id JOIN warehouses w ON ir.warehouse_id = w.id JOIN verifiers v ON ir.causing_verifier_id = v.id JOIN incidents i ON ir.incident_id = i.id JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id').fetchall()
    conn.close()
    return [(row['id'], f"ID: {row['id']} - Fecha: {row['date']} - Incidencia: {row['incident']}") for row in records]

def insert_incident_action(incident_record_id, action_date, action_description, new_status, performed_by):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO incident_actions (incident_record_id, action_date, action_description, new_status, performed_by) VALUES (?, ?, ?, ?, ?)', (incident_record_id, action_date, action_description, new_status, performed_by))
        if new_status:
            conn.execute('UPDATE incident_records SET status = ? WHERE id = ?', (new_status, incident_record_id))
        conn.commit()
        logger.info(f"Inserted action for incident record {incident_record_id}")
    except sqlite3.Error as e:
        logger.error(f"Error inserting incident action: {e}")
    finally:
        conn.close()

def get_incident_actions(incident_record_id):
    conn = get_db_connection()
    actions = conn.execute('SELECT ia.action_date, ia.action_description, ia.new_status, c.name || " " || c.surnames AS performed_by FROM incident_actions ia JOIN coordinators c ON ia.performed_by = c.id WHERE ia.incident_record_id = ? ORDER BY ia.action_date', (incident_record_id,)).fetchall()
    conn.close()
    return actions

def get_all_incident_records_df():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT ir.*, c.name || " " || c.surnames AS registering_coordinator, w.name AS warehouse, w.zone AS warehouse_zone, v.name || " " || v.surnames AS causing_verifier, v.zone AS verifier_zone, i.description AS incident_type, ac.name || " " || ac.surnames AS assigned_coordinator FROM incident_records ir JOIN coordinators c ON ir.registering_coordinator_id = c.id JOIN warehouses w ON ir.warehouse_id = w.id JOIN verifiers v ON ir.causing_verifier_id = v.id JOIN incidents i ON ir.incident_id = i.id JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id', conn)
    conn.close()
    return df

def get_all_verifiers_df():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM verifiers', conn)
    conn.close()
    return df

def get_all_warehouses_df():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM warehouses', conn)
    conn.close()
    return df

def get_incidents_by_zone():
    df = get_all_incident_records_df()
    return df.groupby('warehouse_zone').size().reset_index(name='count')

def get_incidents_by_verifier():
    df = get_all_incident_records_df()
    return df.groupby('causing_verifier').size().reset_index(name='count')

def get_incidents_by_warehouse():
    df = get_all_incident_records_df()
    return df.groupby('warehouse').size().reset_index(name='count')

def get_incidents_by_type():
    df = get_all_incident_records_df()
    return df.groupby('incident_type').size().reset_index(name='count')

def get_incidents_by_status():
    df = get_all_incident_records_df()
    return df.groupby('status').size().reset_index(name='count')

def get_assignments_by_verifier():
    df = get_all_incident_records_df()
    return df[df['responsible'] == 'Verificador'].groupby('causing_verifier').size().reset_index(name='count')

def reset_database():
    conn = get_db_connection()
    tables = ['coordinators', 'verifiers', 'warehouses', 'incidents', 'incident_records', 'incident_actions']
    for table in tables:
        conn.execute(f'DELETE FROM {table}')
    conn.commit()
    conn.close()

def get_incident_record_details(incident_record_id):
    conn = get_db_connection()
    row = conn.execute('SELECT ir.*, c.name || " " || c.surnames AS registering_coordinator, w.name AS warehouse, w.zone AS warehouse_zone, v.name || " " || v.surnames AS causing_verifier, v.zone AS verifier_zone, i.description AS incident_type, ac.name || " " || ac.surnames AS assigned_coordinator FROM incident_records ir JOIN coordinators c ON ir.registering_coordinator_id = c.id JOIN warehouses w ON ir.warehouse_id = w.id JOIN verifiers v ON ir.causing_verifier_id = v.id JOIN incidents i ON ir.incident_id = i.id JOIN coordinators ac ON ir.assigned_coordinator_id = ac.id WHERE ir.id = ?', (incident_record_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}