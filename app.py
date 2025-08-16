import streamlit as st
st.set_page_config(layout="wide", page_title="Gestión de Incidencias")
st.markdown("""
    <style>
        .main {max-width: 100%;}
        @media (max-width: 768px) {
            .main {padding: 0 10px;}
            .stButton > button {width: 100%;}
        }
        section[data-testid="stSidebar"] {
            background-color: #f5f5f5 !important;
            font-size: 0.7rem !important;
        }
        section[data-testid="stSidebar"] * {
            color: #000000 !important;
        }
        section[data-testid="stSidebar"] .block-container {
            background-color: #f5f5f5 !important;
        }
        section[data-testid="stSidebar"] button[kind="primary"] {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        /* For option menu */
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] .row-widget {
            background-color: #f5f5f5 !important;
            color: #000000 !important;
            font-size: 0.7rem !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] .row-widget button {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] a.nav-link {
            background-color: #f5f5f5 !important;
            color: #000000 !important;
        }
        section[data-testid="stSidebar"] a.nav-link.active {
            background-color: #D3D3D3 !important;
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

from streamlit_option_menu import option_menu
from utils.database import init_db
from components.forms import coordinator_form, verifier_form, warehouse_form, csv_upload, incident_form, incident_record_form, manage_incident_actions_form, search_incident_form
from components.analytics import analytics_incidents, analytics_verifiers, analytics_warehouses
from components.delete import delete_test_data_form, backup_database_form, export_excel_form, restore_database_form
from components.dashboard import dashboard_main, handle_dashboard_navigation
import hashlib
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializar la base de datos
logger.info("Initializing database from app.py...")
init_db()
logger.info("Database initialization completed.")

# Inicializar datos por defecto en entornos de deploy
try:
    from config import is_deployed_environment
    if is_deployed_environment():
        from init_default_data import run_default_initialization
        logger.info("Deploy environment detected, checking for default data...")
        run_default_initialization()
except ImportError:
    logger.info("Default data initialization not available")

# Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        stored_hash = hashlib.sha256("Cava1234!".encode()).hexdigest()
        if username == "coordinador" and hashed_password == stored_hash:
            st.session_state.logged_in = True
            st.session_state.role = "coordinador"
            st.rerun()
        elif username == "admin" and hashed_password == stored_hash:
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    role = st.session_state.get('role', 'coordinador')
    
    # Manejar navegación desde dashboard
    dashboard_nav = handle_dashboard_navigation()
    if dashboard_nav:
        if dashboard_nav == 'manage_actions':
            st.session_state['main_menu_override'] = 'Incidencias'
            st.session_state['sub_menu_override'] = 'Gestión de Acciones'
        elif dashboard_nav == 'new_incident':
            st.session_state['main_menu_override'] = 'Altas'
            st.session_state['sub_menu_override'] = 'Alta Incidencia'
        elif dashboard_nav == 'analytics':
            st.session_state['main_menu_override'] = 'Consultas y Analítica'
        elif dashboard_nav == 'export':
            st.session_state['main_menu_override'] = 'Administración'
            st.session_state['sub_menu_override'] = 'Exportar a Excel'
    
    with st.sidebar:
        # Botón de logout en la parte superior
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            # Limpiar todas las variables de sesión relacionadas con login
            for key in list(st.session_state.keys()):
                if key in ['logged_in', 'role', 'main_menu_override', 'sub_menu_override']:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        main_options = ["Dashboard", "Altas", "Incidencias", "Consultas y Analítica", "Administración"]
        icons = ["speedometer2", "plus-circle", "exclamation-triangle", "bar-chart-line", "gear"]
        
        # Determinar índice por defecto basado en navegación
        default_idx = 0
        if 'main_menu_override' in st.session_state:
            override_menu = st.session_state['main_menu_override']
            if override_menu in main_options:
                default_idx = main_options.index(override_menu)
            del st.session_state['main_menu_override']
        
        main_selected = option_menu(
            menu_title="Menú Principal",
            options=main_options,
            icons=icons,
            menu_icon="cast",
            default_index=default_idx,
        )
    
    if main_selected == "Dashboard":
        dashboard_main()
    
    elif main_selected == "Altas":
        with st.sidebar:
            # Determinar índice por defecto para submenú
            sub_default_idx = 0
            if 'sub_menu_override' in st.session_state:
                sub_options = ["Alta Coordinador", "Alta Verificador", "Alta Bodega", "Cargar Verificadores CSV", "Cargar Bodegas CSV", "Alta Incidencia"]
                override_sub = st.session_state['sub_menu_override']
                if override_sub in sub_options:
                    sub_default_idx = sub_options.index(override_sub)
                del st.session_state['sub_menu_override']
            
            sub_selected = option_menu(
                menu_title="Altas",
                options=["Alta Coordinador", "Alta Verificador", "Alta Bodega", "Cargar Verificadores CSV", "Cargar Bodegas CSV", "Alta Incidencia"],
                icons=["person", "person-check", "building", "file-earmark-spreadsheet", "file-earmark-spreadsheet", "exclamation-triangle"],
                menu_icon="plus",
                default_index=sub_default_idx,
            )

        if sub_selected == "Alta Coordinador":
            coordinator_form()
        elif sub_selected == "Alta Verificador":
            verifier_form()
        elif sub_selected == "Alta Bodega":
            warehouse_form()
        elif sub_selected == "Cargar Verificadores CSV":
            csv_upload("Verificadores")
        elif sub_selected == "Cargar Bodegas CSV":
            csv_upload("Bodegas")
        elif sub_selected == "Alta Incidencia":
            incident_form()

    elif main_selected == "Incidencias":
        with st.sidebar:
            # Determinar índice por defecto para submenú
            sub_default_idx = 0
            if 'sub_menu_override' in st.session_state:
                sub_options = ["Registro de Incidencia", "Gestión de Acciones", "Buscar por Código"]
                override_sub = st.session_state['sub_menu_override']
                if override_sub in sub_options:
                    sub_default_idx = sub_options.index(override_sub)
                del st.session_state['sub_menu_override']
            
            sub_selected = option_menu(
                menu_title="Incidencias",
                options=["Registro de Incidencia", "Gestión de Acciones", "Buscar por Código"],
                icons=["clipboard-plus", "pencil-square", "search"],
                menu_icon="exclamation",
                default_index=sub_default_idx,
            )

        if sub_selected == "Registro de Incidencia":
            incident_record_form()
        elif sub_selected == "Gestión de Acciones":
            manage_incident_actions_form()
        elif sub_selected == "Buscar por Código":
            search_incident_form()

    elif main_selected == "Consultas y Analítica":
        with st.sidebar:
            sub_selected = option_menu(
                menu_title="Consultas y Analítica",
                options=["Analítica de Incidencias", "Analítica de Verificadores", "Analítica de Bodegas"],
                icons=["clipboard-data", "person-lines-fill", "building"],
                menu_icon="graph-up",
                default_index=0,
            )

        if sub_selected == "Analítica de Incidencias":
            analytics_incidents()
        elif sub_selected == "Analítica de Verificadores":
            analytics_verifiers()
        elif sub_selected == "Analítica de Bodegas":
            analytics_warehouses()

    elif main_selected == "Administración":
        with st.sidebar:
            # Determinar índice por defecto para submenú
            sub_default_idx = 0
            if 'sub_menu_override' in st.session_state:
                sub_options = ["Copia de Seguridad", "Restaurar Copia", "Exportar a Excel", "Borrar Datos de Prueba"]
                override_sub = st.session_state['sub_menu_override']
                if override_sub in sub_options:
                    sub_default_idx = sub_options.index(override_sub)
                del st.session_state['sub_menu_override']
            
            sub_selected = option_menu(
                menu_title="Administración",
                options=["Copia de Seguridad", "Restaurar Copia", "Exportar a Excel", "Borrar Datos de Prueba"],
                icons=["shield-check", "arrow-clockwise", "file-earmark-excel", "trash"],
                menu_icon="gear",
                default_index=sub_default_idx,
            )

        if sub_selected == "Copia de Seguridad":
            backup_database_form()
        elif sub_selected == "Restaurar Copia":
            restore_database_form()
        elif sub_selected == "Exportar a Excel":
            export_excel_form()
        elif sub_selected == "Borrar Datos de Prueba":
            delete_test_data_form()