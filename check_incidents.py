from utils.database import get_db_connection
import sqlite3

def check_incident_records():
    try:
        conn = get_db_connection()
        
        # Verificar registros de incidencias que usan el mismo código
        query = '''
        SELECT 
            ir.id,
            ir.date,
            i.code,
            i.description,
            w.name as warehouse,
            v.name || " " || v.surnames as verifier,
            c.name || " " || c.surnames as coordinator
        FROM incident_records ir
        JOIN incidents i ON ir.incident_id = i.id
        JOIN warehouses w ON ir.warehouse_id = w.id
        JOIN verifiers v ON ir.causing_verifier_id = v.id
        JOIN coordinators c ON ir.assigned_coordinator_id = c.id
        ORDER BY i.code, ir.date
        '''
        
        cursor = conn.execute(query)
        records = cursor.fetchall()
        
        print('Registros de incidencias por código:')
        print('-' * 80)
        
        # Agrupar por código de incidencia
        records_by_code = {}
        for record in records:
            code = record['code']
            if code not in records_by_code:
                records_by_code[code] = []
            records_by_code[code].append(record)
        
        # Mostrar registros agrupados
        for code, code_records in records_by_code.items():
            print(f'\nCódigo: {code} ({len(code_records)} registros)')
            for record in code_records:
                print(f'  ID: {record["id"]} | Fecha: {record["date"]} | Bodega: {record["warehouse"]} | Verificador: {record["verifier"]} | Coordinador: {record["coordinator"]}')
        
        # Verificar si hay múltiples registros con el mismo código
        duplicates = {code: records for code, records in records_by_code.items() if len(records) > 1}
        
        if duplicates:
            print('\n¡MÚLTIPLES REGISTROS CON EL MISMO CÓDIGO DE INCIDENCIA!')
            print('-' * 80)
            for code, dup_records in duplicates.items():
                print(f'Código {code} tiene {len(dup_records)} registros:')
                for record in dup_records:
                    print(f'  - ID: {record["id"]}, Fecha: {record["date"]}, Bodega: {record["warehouse"]}')
        else:
            print('\nTodos los registros tienen códigos únicos.')
            
        conn.close()
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_incident_records()