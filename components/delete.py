import streamlit as st
import os
from utils.database import reset_database, create_backup, export_incidents_to_excel

def delete_test_data_form():
    st.subheader("Borrar Datos de Prueba")
    st.warning("Esta acción borrará todos los datos de la base de datos. Úsala solo para pruebas.")
    access_code = st.text_input("Código de Acceso", type="password")
    confirm = st.checkbox("Confirmo que deseo borrar todos los datos")
    if st.button("Borrar Datos", disabled=not confirm):
        if access_code == "197569":
            reset_database()
            st.success("Datos de prueba borrados exitosamente.")
        else:
            st.error("Código de acceso incorrecto.")

def backup_database_form():
    st.subheader("Copia de Seguridad de la Base de Datos")
    st.info("Crea una copia de seguridad de toda la base de datos.")
    
    if st.button("Crear Copia de Seguridad"):
        try:
            backup_path = create_backup()
            st.success(f"Copia de seguridad creada exitosamente: {backup_path}")
            
            # Ofrecer descarga del archivo
            if os.path.exists(backup_path):
                with open(backup_path, 'rb') as f:
                    st.download_button(
                        label="Descargar Copia de Seguridad",
                        data=f.read(),
                        file_name=os.path.basename(backup_path),
                        mime="application/octet-stream"
                    )
        except Exception as e:
            st.error(f"Error al crear la copia de seguridad: {str(e)}")

def export_excel_form():
    st.subheader("Exportar Historial a Excel")
    st.info("Exporta el historial completo de incidencias y acciones a un archivo Excel.")
    
    if st.button("Exportar a Excel"):
        try:
            filename = export_incidents_to_excel()
            st.success(f"Archivo Excel creado exitosamente: {filename}")
            
            # Ofrecer descarga del archivo
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="Descargar Archivo Excel",
                        data=f.read(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"Error al exportar a Excel: {str(e)}")
            st.info("Nota: Asegúrate de que openpyxl esté instalado: pip install openpyxl")