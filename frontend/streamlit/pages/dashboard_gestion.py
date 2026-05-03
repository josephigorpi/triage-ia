import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_db_connection

def show():
    st.title("Dashboard de Gestión")
    st.markdown("### Métricas agregadas y tendencias")

    with get_db_connection() as conn:
        # Triajes por mes
        df_mensual = pd.read_sql("""
            SELECT DATE_TRUNC('month', fecha_hora) AS mes, COUNT(*) AS total_triajes
            FROM triajes
            GROUP BY mes
            ORDER BY mes
        """, conn)
        if not df_mensual.empty:
            fig_mes = px.line(df_mensual, x='mes', y='total_triajes', title='Evolución mensual de triajes')
            st.plotly_chart(fig_mes, use_container_width=True)

        # Distribución por nivel de urgencia global
        df_global_nivel = pd.read_sql("""
            SELECT nivel_urgencia, COUNT(*) AS total
            FROM triajes
            GROUP BY nivel_urgencia
        """, conn)
        fig_pie = px.pie(df_global_nivel, values='total', names='nivel_urgencia', title='Distribución global de urgencias')
        st.plotly_chart(fig_pie, use_container_width=True)

        # Top pacientes con más triajes
        df_top_pacientes = pd.read_sql("""
            SELECT p.nombre_completo, COUNT(t.id_triaje) AS cantidad
            FROM pacientes p
            LEFT JOIN triajes t ON p.id_paciente = t.id_paciente
            GROUP BY p.id_paciente
            ORDER BY cantidad DESC
            LIMIT 10
        """, conn)
        st.subheader("Pacientes con más triajes")
        st.dataframe(df_top_pacientes, use_container_width=True)

        # Actividad por usuario
        df_usuarios = pd.read_sql("""
            SELECT u.nombre_usuario, COUNT(t.id_triaje) AS triajes_realizados
            FROM usuarios u
            LEFT JOIN triajes t ON u.id_usuario = t.id_usuario
            GROUP BY u.id_usuario
        """, conn)
        fig_bar = px.bar(df_usuarios, x='nombre_usuario', y='triajes_realizados', title='Triajes por usuario')
        st.plotly_chart(fig_bar, use_container_width=True)