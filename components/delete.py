import streamlit as st
import os
from utils.database import reset_database, create_backup, export_incidents_to_excel
from utils.backup_restore import restore_db

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

def restore_database_form():
    st.subheader("Restaurar Copia de Seguridad")
    st.warning("Esta acción reemplazará completamente la base de datos actual. Asegúrate de hacer una copia de seguridad antes de proceder.")
    
    uploaded_file = st.file_uploader(
        "Selecciona el archivo de copia de seguridad (.db)",
        type=['db'],
        help="Sube un archivo de copia de seguridad generado previamente"
    )
    
    if uploaded_file is not None:
        st.info(f"Archivo seleccionado: {uploaded_file.name}")
        
        # Código de confirmación
        access_code = st.text_input("Código de Acceso para Restauración", type="password")
        confirm_restore = st.checkbox("Confirmo que deseo restaurar la base de datos y reemplazar todos los datos actuales")
        
        if st.button("Restaurar Base de Datos", disabled=not confirm_restore):
            if access_code == "197569":
                try:
                    # Guardar el archivo temporalmente
                    temp_path = f"temp_restore_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Restaurar la base de datos
                    restore_db(temp_path)
                    
                    # Limpiar archivo temporal
                    os.remove(temp_path)
                    
                    st.success("Base de datos restaurada exitosamente.")
                    st.info("La aplicación se reiniciará automáticamente para aplicar los cambios.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error al restaurar la base de datos: {str(e)}")
                    # Limpiar archivo temporal en caso de error
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                st.error("Código de acceso incorrecto.")
    else:
        st.info("Por favor, selecciona un archivo de copia de seguridad para continuar.")