import streamlit as st
import pandas as pd
import datetime
from utils.database_unified import insert_coordinator, insert_verifier, insert_warehouse, load_csv_to_verifiers, load_csv_to_warehouses, insert_incident, get_coordinators, get_verifiers, get_warehouses, get_incidents, insert_incident_record, get_incident_records, insert_incident_action, get_incident_actions, get_incident_record_details, search_incident_by_code, get_incident_records_by_incident_code

def coordinator_form():
    st.subheader('Alta de Coordinador')
    
    if 'coord_form_counter' not in st.session_state:
        st.session_state.coord_form_counter = 0
    
    name = st.text_input('Nombre', key=f'coord_name_{st.session_state.coord_form_counter}', help='Ingrese un nombre válido (mínimo 2 caracteres)')
    surnames = st.text_input('Apellidos', key=f'coord_surnames_{st.session_state.coord_form_counter}', help='Ingrese apellidos válidos (mínimo 2 caracteres)')
    
    if st.button('Guardar Coordinador'):
        if name and len(name) >= 2 and surnames and len(surnames) >= 2:
            insert_coordinator(name, surnames)
            st.success('Coordinador guardado exitosamente.')
            st.session_state.coord_form_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete todos los campos con valores válidos (mínimo 2 caracteres cada uno).')

def verifier_form():
    st.subheader('Alta de Verificador')
    
    if 'verif_form_counter' not in st.session_state:
        st.session_state.verif_form_counter = 0
    
    name = st.text_input('Nombre', key=f'verif_name_{st.session_state.verif_form_counter}', help='Mínimo 2 caracteres')
    surnames = st.text_input('Apellidos', key=f'verif_surnames_{st.session_state.verif_form_counter}', help='Mínimo 2 caracteres')
    phone = st.text_input('Teléfono', key=f'verif_phone_{st.session_state.verif_form_counter}', help='Formato: 9 dígitos')
    zones = ['PENEDES', 'ALT CAMP', 'CONCA', 'ALMENDRALEJO', 'REQUENA', 'CARIÑENA']
    zone = st.selectbox('Zona', options=zones, key=f'verif_zone_{st.session_state.verif_form_counter}')
    
    if st.button('Guardar Verificador'):
        if name and len(name) >= 2 and surnames and len(surnames) >= 2 and (phone.isdigit() and len(phone) == 9 or not phone):
            insert_verifier(name, surnames, phone, zone)
            st.success('Verificador guardado exitosamente.')
            st.session_state.verif_form_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete nombre y apellidos con mínimo 2 caracteres, y teléfono con 9 dígitos si se proporciona.')

def warehouse_form():
    st.subheader('Alta de Bodega')
    
    if 'warehouse_form_counter' not in st.session_state:
        st.session_state.warehouse_form_counter = 0
    
    name = st.text_input('Nombre', key=f'wh_name_{st.session_state.warehouse_form_counter}', help='Mínimo 3 caracteres')
    nif = st.text_input('NIF', key=f'wh_nif_{st.session_state.warehouse_form_counter}', help='Formato válido de NIF')
    zones = ['PENEDES', 'ALT CAMP', 'CONCA', 'ALMENDRALEJO', 'REQUENA', 'CARIÑENA']
    zone = st.selectbox('Zona', options=zones, key=f'wh_zone_{st.session_state.warehouse_form_counter}')
    if st.button('Guardar Bodega'):
        if name and len(name) >= 3 and nif and len(nif) >= 8:
            insert_warehouse(name, nif, zone)
            st.success('Bodega guardada exitosamente.')
            st.session_state.warehouse_form_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete nombre (mín. 3 char) y NIF (mín. 8 char).')

def csv_upload(section):
    st.subheader(f'Carga de {section} desde CSV')
    with st.form(key=f'csv_upload_{section}', clear_on_submit=True):
        uploaded_file = st.file_uploader(f'Seleccione CSV para {section}', type='csv')
        separator = st.selectbox('Separador del CSV', [',', ';'], index=0)
        submit = st.form_submit_button('Cargar CSV')
        if submit and uploaded_file is not None:
            try:
                if section == 'Verificadores':
                    df = pd.read_csv(uploaded_file, sep=separator, encoding='latin1')
                    required_columns = ['name', 'surnames']
                    if not all(col in df.columns for col in required_columns):
                        raise ValueError(f'El CSV debe contener las columnas: {', '.join(required_columns)}')
                    load_csv_to_verifiers(uploaded_file, sep=separator)
                elif section == 'Bodegas':
                    df = pd.read_csv(uploaded_file, sep=separator, encoding='latin1')
                    required_columns = ['name', 'nif']
                    if not all(col in df.columns for col in required_columns):
                        raise ValueError(f'El CSV debe contener las columnas: {', '.join(required_columns)}')
                    load_csv_to_warehouses(uploaded_file, sep=separator)
                st.success(f'{section} cargados exitosamente desde CSV.')
            except Exception as e:
                st.error(f'Error al cargar el CSV: {str(e)}')

def incident_form():
    st.subheader('Alta de Incidencia')
    
    if 'incident_form_counter' not in st.session_state:
        st.session_state.incident_form_counter = 0
    
    # Opción para código personalizado o automático
    col1, col2 = st.columns([1, 3])
    with col1:
        auto_code = st.checkbox('Código automático', value=True, key=f'auto_code_{st.session_state.incident_form_counter}', help='Generar código automáticamente o introducir uno personalizado')
    
    with col2:
        if auto_code:
            st.info('Se generará automáticamente un código secuencial (ej: 001, 002, etc.)')
            custom_code = None
        else:
            custom_code = st.text_input('Código de Incidencia', key=f'inc_code_{st.session_state.incident_form_counter}', help='Introduzca un código único para la incidencia (ej: INC-2025-001)', max_chars=20)
    
    description = st.text_area('Descripción de la Incidencia', key=f'inc_description_{st.session_state.incident_form_counter}', help='Proporcione una descripción detallada de la incidencia (mínimo 10 caracteres)')
    
    if st.button('Guardar Incidencia'):
        if description and len(description) >= 10:
            if not auto_code and (not custom_code or len(custom_code.strip()) < 3):
                st.error('Por favor, ingrese un código válido de al menos 3 caracteres o active la generación automática.')
            else:
                code_to_use = custom_code.strip() if not auto_code else None
                result = insert_incident(description, code_to_use)
                if result['success']:
                    st.success(f'Incidencia guardada exitosamente con código: {result["code"]}')
                    st.session_state.incident_form_counter += 1
                    st.rerun()
                else:
                    st.error(result['error'])
        else:
            st.error('Por favor, ingrese una descripción con al menos 10 caracteres.')

def search_incident_form():
    """Formulario para buscar incidencias por código"""
    st.header("🔍 Buscar Incidencia por Código")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_code = st.text_input(
            "Código de Incidencia",
            placeholder="Ej: 001, INC-2024-001",
            help="Introduzca el código de la incidencia que desea buscar"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("🔍 Buscar", type="primary")
    
    if search_button and search_code.strip():
        # Buscar la incidencia
        incident_result = search_incident_by_code(search_code.strip())
        
        if incident_result['success']:
            incident = incident_result['incident']
            
            # Mostrar información de la incidencia
            st.success(f"✅ Incidencia encontrada: **{incident['code']}**")
            
            with st.expander("📋 Detalles de la Incidencia", expanded=True):
                st.write(f"**Código:** {incident['code']}")
                st.write(f"**Descripción:** {incident['description']}")
                st.write(f"**Fecha de creación:** {incident.get('created_at', 'No disponible')}")
            
            # Buscar registros asociados
            records_result = get_incident_records_by_incident_code(search_code.strip())
            
            if records_result['success']:
                records = records_result['records']
                st.subheader(f"📊 Registros Asociados ({len(records)})")
                
                for i, record in enumerate(records, 1):
                    with st.expander(f"Registro #{i} - {record['warehouse']} ({record['status']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Fecha:** {record['date']}")
                            st.write(f"**Almacén:** {record['warehouse']} - {record['warehouse_zone']}")
                            st.write(f"**Estado:** {record['status']}")
                            st.write(f"**Tipo:** {record['incident_type']}")
                        
                        with col2:
                            st.write(f"**Coordinador Registrante:** {record['registering_coordinator']}")
                            st.write(f"**Verificador Causante:** {record['causing_verifier']}")
                            st.write(f"**Coordinador Asignado:** {record['assigned_coordinator']}")
                        
                        if record.get('observations'):
                            st.write(f"**Observaciones:** {record['observations']}")
            else:
                st.info("ℹ️ No se encontraron registros asociados a esta incidencia")
                
        else:
            st.error(f"❌ {incident_result['error']}")
    
    elif search_button and not search_code.strip():
        st.warning("⚠️ Por favor, ingrese un código de incidencia para buscar")

def incident_record_form():
    st.subheader('Registro de Incidencia')
    
    if 'incident_record_counter' not in st.session_state:
        st.session_state.incident_record_counter = 0
    
    date = st.date_input('Fecha', datetime.date.today(), key=f'inc_rec_date_{st.session_state.incident_record_counter}', help='Seleccione la fecha de la incidencia')
    coordinators = get_coordinators()
    if not coordinators:
        st.warning('No hay coordinadores disponibles. Por favor, registre uno primero.')
        return
    registering_coordinator_id = st.selectbox('Coordinador que registra', options=coordinators, format_func=lambda x: x[1], key=f'inc_rec_reg_coord_{st.session_state.incident_record_counter}')[0]
    warehouses = get_warehouses()
    if not warehouses:
        st.warning('No hay bodegas disponibles. Por favor, registre una primero.')
        return
    warehouse_id = st.selectbox('Bodega', options=warehouses, format_func=lambda x: x[1], key=f'inc_rec_warehouse_{st.session_state.incident_record_counter}')[0]
    verifiers = get_verifiers()
    if not verifiers:
        st.warning('No hay verificadores disponibles. Por favor, registre uno primero.')
        return
    causing_verifier_id = st.selectbox('Verificador que provocó la incidencia', options=verifiers, format_func=lambda x: x[1], key=f'inc_rec_verifier_{st.session_state.incident_record_counter}')[0]
    incidents = get_incidents()
    if not incidents:
        st.warning('No hay incidencias disponibles. Por favor, registre una primero.')
        return
    incident_id = st.selectbox('Incidencia', options=incidents, format_func=lambda x: x[1], key=f'inc_rec_incident_{st.session_state.incident_record_counter}')[0]
    assigned_coordinator_id = st.selectbox('Coordinador asignado', options=coordinators, format_func=lambda x: x[1], key=f'inc_rec_assigned_coord_{st.session_state.incident_record_counter}')[0]
    explanation = st.text_area('Explicación', key=f'inc_rec_explanation_{st.session_state.incident_record_counter}', help='Explique los detalles de la incidencia')
    status = st.selectbox('Status', ['Pendiente', 'En Proceso', 'Solucionado', 'Asignado a Técnicos', 'RRHH'], key=f'inc_rec_status_{st.session_state.incident_record_counter}', help='Seleccione el estado actual')
    responsible = st.selectbox('Responsable', ['Bodega', 'Verificador', 'RRHH', 'Coordinacion', 'Servicios Informáticos'], key=f'inc_rec_responsible_{st.session_state.incident_record_counter}', help='Indique quién es responsable')
    if st.button('Guardar Registro de Incidencia'):
        if all([date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, status, responsible]):
            insert_incident_record(date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, status, responsible)
            st.success('Registro de incidencia guardado exitosamente.')
            # Incrementar contador para limpiar formulario
            st.session_state.incident_record_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete todos los campos obligatorios.')

def manage_incident_actions_form():
    st.subheader('Gestión de Acciones de Incidencia')
    
    if 'incident_actions_counter' not in st.session_state:
        st.session_state.incident_actions_counter = 0
    
    incident_records = get_incident_records()
    if not incident_records:
        st.warning('No hay registros de incidencias disponibles. Por favor, registre uno primero.')
        return
    selected_record = st.selectbox('Seleccionar Registro de Incidencia', options=incident_records, format_func=lambda x: x[1], key=f'inc_act_record_{st.session_state.incident_actions_counter}')
    incident_record_id = selected_record[0]
    
    # Mostrar información original de la incidencia
    details = get_incident_record_details(incident_record_id)
    if details:
        df = pd.DataFrame([details])
        column_mapping = {
            'date': 'Fecha',
            'explanation': 'Explicación',
            'status': 'Estado',
            'responsible': 'Responsable',
            'registering_coordinator': 'Coordinador Registrador',
            'assigned_coordinator': 'Coordinador Asignado',
            'causing_verifier': 'Verificador Causante',
            'warehouse': 'Bodega',
            'incident_description': 'Descripción de Incidencia',
            'causing_person': 'Persona Causante',
            'pending': 'Pendiente'
        }
        df = df.rename(columns=column_mapping)
        display_columns = [col for col in df.columns if not col.endswith('_id') and col != 'id']
        st.subheader('Información Original de la Incidencia')
        st.dataframe(df[display_columns])
    
    actions = get_incident_actions(incident_record_id)
    st.subheader('Historial de Acciones')
    for action in actions:
        st.write(f"Fecha: {action['action_date']}, Descripción: {action['action_description']}, Nuevo Status: {action['new_status'] or 'N/A'}, Realizado por: {action['performed_by']}")
    st.subheader('Añadir Nueva Acción')
    action_date = st.date_input('Fecha de la Acción', datetime.date.today(), key=f'inc_act_date_{st.session_state.incident_actions_counter}', help='Fecha en que se realizó la acción')
    action_description = st.text_area('Descripción de la Acción', key=f'inc_act_desc_{st.session_state.incident_actions_counter}', help='Describa la acción tomada')
    new_status = st.selectbox('Nuevo Status (opcional)', [None, 'Pendiente', 'En Proceso', 'Solucionado', 'Asignado a Técnicos', 'RRHH'], index=0, key=f'inc_act_status_{st.session_state.incident_actions_counter}', help='Actualice el estado si es necesario')
    coordinators = get_coordinators()
    performed_by = st.selectbox('Realizado por', options=coordinators, format_func=lambda x: x[1], key=f'inc_act_by_{st.session_state.incident_actions_counter}')[0]
    if st.button('Guardar Acción'):
        if action_date and action_description and performed_by:
            insert_incident_action(incident_record_id, action_date, action_description, new_status, performed_by)
            st.success('Acción guardada exitosamente.')
            # Incrementar contador para limpiar formulario
            st.session_state.incident_actions_counter += 1
            st.rerun()
        else:
            st.error('Por favor, complete fecha, descripción y realizado por.')