import streamlit as st
import pandas as pd
import altair as alt
from utils.database import get_dashboard_stats, get_pending_incidents_summary, get_recent_actions
from datetime import datetime

def dashboard_main():
    """Pantalla principal del dashboard con estadísticas y accesos directos"""
    st.title("📊 Dashboard - Gestión de Incidencias")
    st.markdown("---")
    
    # Obtener estadísticas
    try:
        stats = get_dashboard_stats()
        pending_incidents = get_pending_incidents_summary()
        recent_actions = get_recent_actions()
    except Exception as e:
        st.error(f"Error al cargar datos del dashboard: {e}")
        return
    
    # Sección de métricas principales
    st.subheader("📈 Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Incidencias",
            value=stats['total_incidents'],
            help="Número total de incidencias registradas"
        )
    
    with col2:
        st.metric(
            label="Pendientes",
            value=stats['pending_incidents'],
            delta=f"-{stats['resolved_incidents']} resueltas",
            delta_color="inverse",
            help="Incidencias que requieren atención"
        )
    
    with col3:
        st.metric(
            label="Resueltas",
            value=stats['resolved_incidents'],
            help="Incidencias completamente resueltas"
        )
    
    with col4:
        st.metric(
            label="Últimos 7 días",
            value=stats['recent_incidents'],
            help="Incidencias registradas en la última semana"
        )
    
    st.markdown("---")
    
    # Layout en dos columnas
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Sección de incidencias pendientes
        st.subheader("🚨 Incidencias Pendientes")
        
        if pending_incidents.empty:
            st.success("🎉 ¡Excelente! No hay incidencias pendientes.")
        else:
            st.info(f"Se muestran las {len(pending_incidents)} incidencias más recientes pendientes de resolución.")
            
            # Mostrar tabla de incidencias pendientes
            for idx, incident in pending_incidents.iterrows():
                with st.container():
                    # Crear un expander para cada incidencia
                    status_color = {
                        'Pendiente': '🔴',
                        'En Proceso': '🟡',
                        'Esperando Verificación': '🟠',
                        'Resuelto': '🟢'
                    }.get(incident['status'], '⚪')
                    
                    with st.expander(
                        f"{status_color} ID {incident['id']} - {incident['warehouse']} - {incident['incident_type']}",
                        expanded=False
                    ):
                        col_info, col_action = st.columns([3, 1])
                        
                        with col_info:
                            st.write(f"**📅 Fecha:** {incident['date']}")
                            st.write(f"**🏢 Bodega:** {incident['warehouse']} ({incident['warehouse_zone']})")
                            st.write(f"**👤 Verificador:** {incident['causing_verifier']}")
                            st.write(f"**👨‍💼 Coordinador Asignado:** {incident['assigned_coordinator']}")
                            st.write(f"**📋 Estado:** {incident['status']}")
                            st.write(f"**👥 Responsable:** {incident['responsible']}")
                        
                        with col_action:
                            # Botón de acceso directo a gestión de acciones
                            if st.button(
                                "⚡ Gestionar",
                                key=f"manage_{incident['id']}",
                                help="Ir a Gestión de Acciones para esta incidencia",
                                type="primary"
                            ):
                                # Guardar el ID de la incidencia en session_state para navegación
                                st.session_state['selected_incident_id'] = incident['id']
                                st.session_state['navigate_to_actions'] = True
                                st.rerun()
    
    with col_right:
        # Gráfico de distribución por estado
        st.subheader("📊 Distribución por Estado")
        
        if not stats['by_status'].empty:
            # Crear gráfico de barras
            chart = alt.Chart(stats['by_status']).mark_bar(color='steelblue').encode(
                x=alt.X('count:Q', title='Cantidad'),
                y=alt.Y('status:N', title='Estado', sort='-x'),
                tooltip=['status:N', 'count:Q']
            ).properties(
                width=300,
                height=200
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No hay datos para mostrar")
        
        # Acciones recientes
        st.subheader("🔄 Acciones Recientes")
        
        if recent_actions.empty:
            st.info("No hay acciones recientes")
        else:
            for idx, action in recent_actions.iterrows():
                with st.container():
                    st.markdown(f"""
                    **📅 {action['action_date']}**  
                    🏢 {action['warehouse']} (ID: {action['incident_id']})  
                    👤 {action['performed_by']}  
                    📝 {action['action_description'][:50]}{'...' if len(action['action_description']) > 50 else ''}  
                    {f"➡️ {action['new_status']}" if pd.notna(action['new_status']) else ""}
                    """)
                    st.markdown("---")
    
    # Sección de accesos rápidos
    st.markdown("---")
    st.subheader("🚀 Accesos Rápidos")
    
    col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)
    
    with col_quick1:
        if st.button("📝 Nueva Incidencia", use_container_width=True, type="secondary"):
            st.session_state['navigate_to'] = 'new_incident'
            st.rerun()
    
    with col_quick2:
        if st.button("⚡ Gestión de Acciones", use_container_width=True, type="secondary"):
            st.session_state['navigate_to'] = 'manage_actions'
            st.rerun()
    
    with col_quick3:
        if st.button("📊 Analítica Completa", use_container_width=True, type="secondary"):
            st.session_state['navigate_to'] = 'analytics'
            st.rerun()
    
    with col_quick4:
        if st.button("📋 Exportar Excel", use_container_width=True, type="secondary"):
            st.session_state['navigate_to'] = 'export'
            st.rerun()
    
    # Información adicional
    st.markdown("---")
    with st.expander("ℹ️ Información del Dashboard"):
        st.markdown("""
        **¿Qué puedes hacer desde aquí?**
        
        - **Ver estadísticas generales** de todas las incidencias
        - **Revisar incidencias pendientes** que requieren atención
        - **Acceder directamente** a la gestión de acciones de cualquier incidencia
        - **Monitorear acciones recientes** realizadas por el equipo
        - **Navegar rápidamente** a las funciones más utilizadas
        
        **Estados de incidencias:**
        - 🔴 **Pendiente**: Recién registrada, requiere asignación
        - 🟡 **En Proceso**: Se está trabajando en la resolución
        - 🟠 **Esperando Verificación**: Pendiente de confirmación
        - 🟢 **Resuelto**: Incidencia completamente resuelta
        """)

def handle_dashboard_navigation():
    """Maneja la navegación desde el dashboard"""
    # Verificar si hay navegación pendiente
    if 'navigate_to_actions' in st.session_state and st.session_state['navigate_to_actions']:
        st.session_state['navigate_to_actions'] = False
        return 'manage_actions'
    
    if 'navigate_to' in st.session_state:
        destination = st.session_state['navigate_to']
        del st.session_state['navigate_to']
        return destination
    
    return None