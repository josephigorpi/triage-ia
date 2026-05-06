import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_db_connection
from datetime import datetime

def show():
    st.title("📊 Dashboard Operacional")
    
    # Filtros de fecha
    col_f1, col_f2 = st.columns(2)
    fecha_i = col_f1.date_input("Desde", datetime.today())
    fecha_f = col_f2.date_input("Hasta", datetime.today())

    with get_db_connection() as conn:
        # Query con rango de fechas
        df = pd.read_sql("""
            SELECT t.id_triaje, p.nombre_completo AS paciente, t.nivel_urgencia, t.fecha_hora,
                   EXTRACT(HOUR FROM t.fecha_hora) as hora
            FROM triajes t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            WHERE t.fecha_hora::date BETWEEN %s AND %s
            ORDER BY t.fecha_hora DESC
        """, conn, params=(fecha_i, fecha_f))

        if not df.empty:
            # KPIs Rápidos
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Triajes", len(df))
            c2.metric("Nivel Crítico/Alto", len(df[df['nivel_urgencia'].isin(['crítico', 'alto'])]))
            hora_pico = df['hora'].mode()[0]
            c3.metric("Hora de mayor flujo", f"{int(hora_pico)}:00h")

            # Gráfico de Barras: Distribución de Urgencias
            df_niveles = df.groupby('nivel_urgencia').size().reset_index(name='cantidad')
            fig_bar = px.bar(df_niveles, x='nivel_urgencia', y='cantidad', 
                             title='Carga por Nivel de Urgencia',
                             color='nivel_urgencia',
                             color_discrete_map={'crítico':'red', 'alto':'orange', 'moderado':'yellow', 'bajo':'green'})
            st.plotly_chart(fig_bar, use_container_width=True)

            # NUEVO: Mapa de calor de actividad por hora (Lineal)
            df_horas = df.groupby('hora').size().reset_index(name='cantidad')
            fig_line = px.line(df_horas, x='hora', y='cantidad', title='Flujo de pacientes por hora',
                               markers=True, labels={'hora': 'Hora del día', 'cantidad': 'Pacientes'})
            st.plotly_chart(fig_line, use_container_width=True)

            st.markdown("### Detalle de ingresos recientes")
            st.dataframe(df[['id_triaje', 'paciente', 'nivel_urgencia', 'fecha_hora']], use_container_width=True)
        else:
            st.warning("No hay datos para el rango seleccionado.")
