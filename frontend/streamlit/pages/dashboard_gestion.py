import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_db_connection
import datetime  # <--- Cambia 'from datetime import datetime' por esto


def show():
    st.title("📈 Dashboard de Gestión")
    
    # Filtros de fecha para análisis histórico
    col_f1, col_f2 = st.columns(2)
    f_inicio = col_f1.date_input("Fecha Inicio", hoy.replace(day=1)) 
    f_fin = col_f2.date_input("Fecha Fin", hoy)

    with get_db_connection() as conn:
        df_base = pd.read_sql("""
            SELECT t.fecha_hora, t.nivel_urgencia, u.nombre_usuario, p.nombre_completo
            FROM triajes t
            JOIN usuarios u ON t.id_usuario = u.id_usuario
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            WHERE t.fecha_hora::date BETWEEN %s AND %s
        """, conn, params=(f_inicio, f_fin))

        if not df_base.empty:
            # Gráfico 1: Evolución Temporal (Área)
            df_base['fecha'] = df_base['fecha_hora'].dt.date
            df_diario = df_base.groupby('fecha').size().reset_index(name='total')
            fig_area = px.area(df_diario, x='fecha', y='total', title='Tendencia de triajes realizados')
            st.plotly_chart(fig_area, use_container_width=True)

            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de Torta (Distribución porcentual)
                df_pie = df_base.groupby('nivel_urgencia').size().reset_index(name='total')
                fig_pie = px.pie(df_pie, values='total', names='nivel_urgencia', title='Mix de Urgencias %')
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                # Top Usuarios (Rendimiento)
                df_user = df_base.groupby('nombre_usuario').size().reset_index(name='triajes')
                fig_user = px.bar(df_user, x='triajes', y='nombre_usuario', orientation='h', 
                                  title='Productividad por Usuario')
                st.plotly_chart(fig_user, use_container_width=True)

            # Análisis de Recurrencia
            st.subheader("Pacientes recurrentes en el periodo")
            df_rec = df_base.groupby('nombre_completo').size().reset_index(name='visitas')
            df_rec = df_rec[df_rec['visitas'] > 1].sort_values(by='visitas', ascending=False)
            st.table(df_rec.head(5))
        else:
            st.info("No hay datos agregados en este periodo.")
