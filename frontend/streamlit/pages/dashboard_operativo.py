import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_db_connection

def show():
    st.title("Dashboard Operacional")
    st.markdown("### Triajes del día y métricas en tiempo real")

    with get_db_connection() as conn:
        # Triajes del día
        df_triajes_hoy = pd.read_sql("""
            SELECT t.id_triaje, p.nombre_completo AS paciente, t.nivel_urgencia, t.fecha_hora,
                   t.presion_arterial_sist, t.presion_arterial_diast, t.frecuencia_cardiaca,
                   t.temperatura, t.saturacion_oxigeno
            FROM triajes t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            WHERE t.fecha_hora::date = CURRENT_DATE
            ORDER BY t.fecha_hora DESC
        """, conn)

        # Distribución niveles de urgencia hoy
        df_niveles = df_triajes_hoy.groupby('nivel_urgencia').size().reset_index(name='count')
        fig = px.bar(df_niveles, x='nivel_urgencia', y='count', title='Distribución de niveles de urgencia hoy',
                     color='nivel_urgencia', color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

        # Lista de triajes recientes
        st.dataframe(df_triajes_hoy[['id_triaje', 'paciente', 'nivel_urgencia', 'fecha_hora']], use_container_width=True)

        # Tiempos de atención (ejemplo: tiempo entre triajes)
        # En un sistema real se podría calcular con logs.
        st.info("En esta versión se muestran datos básicos. Ampliable con métricas de tiempos.")