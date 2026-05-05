

import sys
import os

# Esto le dice a Python que busque módulos en la raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))



import streamlit as st
from utils import verificar_usuario, registrar_log
import pandas as pd




st.set_page_config(page_title="Triaje IA", layout="wide")

# Inicializar estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Login
if not st.session_state.authenticated:
    st.title("Sistema de Triaje Asistido por IA")
    with st.form("login"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")
        if submitted:
            user = verificar_usuario(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                registrar_log(user['id_usuario'], "login", "Inicio de sesión exitoso")
                st.success("Acceso concedido")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

# ... después de la autenticación
st.sidebar.markdown("---")
st.sidebar.markdown("### Dashboards Avanzados")
st.sidebar.markdown("[Ver en React](http://localhost:3000)")  # Asumiendo que React corre en puerto 3000

# Sidebar con menú
st.sidebar.title(f"Bienvenido, {st.session_state.user['nombre_usuario']}")
menu = st.sidebar.selectbox("Navegación", ["Nuevo Triaje", "Dashboard Operacional", "Dashboard Gestión", "Reportes PDF"])
if st.sidebar.button("Cerrar sesión"):
    registrar_log(st.session_state.user['id_usuario'], "logout", "Cierre de sesión")
    st.session_state.authenticated = False
    st.session_state.user = None
    st.experimental_rerun()

# Navegación
if menu == "Nuevo Triaje":
    from pages import nuevo_triaje
    nuevo_triaje.show()
elif menu == "Dashboard Operacional":
    from pages.dashboard_operativo import show
    show()
elif menu == "Dashboard Gestión":
    from pages.dashboard_gestion import show
    show()
elif menu == "Reportes PDF":
    from pages.reportes import show
    show()
