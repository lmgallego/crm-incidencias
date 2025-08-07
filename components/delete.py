import streamlit as st
from utils.database import reset_database

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