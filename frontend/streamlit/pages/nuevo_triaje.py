import sys
import os
# Primero el path, luego tus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

import streamlit as st
import pandas as pd
import requests
import json
from utils import get_db_connection, registrar_log, guardar_triaje, obtener_pacientes
from ia.modelo import obtener_recomendacion_ia
from datetime import datetime
from datetime import date

def show():
    # Limpiar estado al cambiar de opción
    if "previous_opcion" not in st.session_state:
        st.session_state.previous_opcion = None

    st.title("Nuevo Triaje")
    st.markdown("---")

    # Seleccionar paciente existente o crear nuevo
    opcion = st.radio("Seleccionar paciente", ["Paciente existente", "Nuevo paciente"])
    
    # Resetear estado si cambió la opción
    if st.session_state.previous_opcion != opcion:
        st.session_state.paciente_creado = False
        st.session_state.nuevo_id_paciente = None
        st.session_state.form_submitted = False
        st.session_state.previous_opcion = opcion

    id_paciente = None

    if opcion == "Paciente existente":
        pacientes_df = obtener_pacientes()
        if pacientes_df.empty:
            st.warning("No hay pacientes registrados. Crea un nuevo paciente primero.")
            id_paciente = None
        else:
            paciente_seleccionado = st.selectbox("Paciente", pacientes_df['nombre_completo'].tolist())
            id_paciente = pacientes_df[pacientes_df['nombre_completo'] == paciente_seleccionado]['id_paciente'].iloc[0]
        # Opcional: cargar antecedentes desde HCE simulada
        with st.expander("Antecedentes (desde HCE)"):
            try:
                resp = requests.get(f"http://localhost:5001/pacientes/{id_paciente}/antecedentes")
                if resp.status_code == 200:
                    st.json(resp.json())
                else:
                    st.info("No se encontraron antecedentes en HCE.")
            except:
                st.warning("No se pudo conectar con la HCE simulada.")

    else:
        with st.form("nuevo_paciente"):
            nombre = st.text_input("Nombre completo")
            fecha_nac = st.date_input("Fecha de nacimiento")
            genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
            contacto = st.text_input("Contacto")
            direccion = st.text_area("Dirección")
            submitted = st.form_submit_button("Registrar paciente")
        
            if submitted and nombre:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO pacientes (nombre_completo, fecha_nacimiento, genero, contacto, direccion)
                            VALUES (%s, %s, %s, %s, %s) RETURNING id_paciente
                        """, (nombre, fecha_nac, genero, contacto, direccion))
                        nuevo_id = cur.fetchone()[0]
                        conn.commit()
                
                # Guardar en session_state en lugar de query_params
                st.session_state.nuevo_id_paciente = nuevo_id
                st.success(f"✅ Paciente {nombre} registrado con ID {nuevo_id}")
                st.info("👉 Cambia manualmente a **'Paciente existente'** y selecciona el paciente recién creado")
                
                # NO hay st.rerun() aquí - el usuario debe cambiar manualmente
































    




    if id_paciente:

        if not id_paciente:
            id_paciente = int(st.query_params.get("pid")) if st.query_params.get("pid") else None

        st.subheader("Datos de Triaje")
        with st.form("triaje"):
            col1, col2 = st.columns(2)
            with col1:
                presion_sist = st.number_input("Presión arterial sistólica", min_value=0, max_value=300)
                presion_diast = st.number_input("Presión arterial diastólica", min_value=0, max_value=200)
                frecuencia = st.number_input("Frecuencia cardíaca (lpm)", min_value=0, max_value=300)
            with col2:
                temperatura = st.number_input("Temperatura (°C)", min_value=30.0, max_value=42.0, step=0.1)
                saturacion = st.number_input("Saturación O₂ (%)", min_value=0, max_value=100)
            sintomas = st.text_area("Síntomas principales", height=100)

            submitted = st.form_submit_button("Evaluar con IA y Guardar")
            if submitted:
                # Construir datos para IA
                datos_triaje = {
                    'presion_arterial_sist': presion_sist,
                    'presion_arterial_diast': presion_diast,
                    'frecuencia_cardiaca': frecuencia,
                    'temperatura': temperatura,
                    'saturacion_oxigeno': saturacion,
                    'sintomas': sintomas
                }
                with st.spinner("Consultando IA..."):
                    recomendacion = obtener_recomendacion_ia(datos_triaje)
                st.success("Recomendación IA obtenida")
                st.info(f"**Nivel de urgencia sugerido:** {recomendacion['nivel_urgencia']}")
                st.info(f"**Conducta sugerida:** {recomendacion['conducta_sugerida']}")
                st.write(f"**Diagnósticos diferenciales:** {recomendacion['diagnosticos_diferenciales']}")

                # Función para convertir numpy types a Python nativos
                def to_python(val):
                    if hasattr(val, 'item'):
                        return val.item()
                    return val

                # Guardar en BD
                data_guardado = {
                    'id_paciente': to_python(id_paciente),
                    'id_usuario': to_python(st.session_state.user['id_usuario']),
                    'presion_arterial_sist': to_python(presion_sist),
                    'presion_arterial_diast': to_python(presion_diast),
                    'frecuencia_cardiaca': to_python(frecuencia),
                    'temperatura': to_python(temperatura),
                    'saturacion_oxigeno': to_python(saturacion),
                    'sintomas': sintomas,
                    'nivel_urgencia': recomendacion['nivel_urgencia'],
                    'conducta_sugerida': recomendacion['conducta_sugerida'],
                    'resultado_ia': recomendacion
                }
                id_triaje = guardar_triaje(data_guardado)
                registrar_log(st.session_state.user['id_usuario'], "crear_triaje", f"Triaje ID {id_triaje} creado")

                # Llamar a webhook de n8n para activar flujos
                try:
                    webhook_url = "http://localhost:5678/webhook/triaje-creado"
                    payload = {
                        "id_triaje": id_triaje,
                        "nivel_urgencia": recomendacion['nivel_urgencia']
                    }
                    requests.post(webhook_url, json=payload, timeout=2)
                except:
                    pass  # No detener el flujo si n8n no responde

                st.success("Triaje guardado correctamente")
                st.balloons()
