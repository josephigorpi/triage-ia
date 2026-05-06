import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from utils import get_db_connection
from datetime import datetime

def show():
    st.title("Generar Reportes PDF")
    tipo = st.radio("Tipo de reporte", ["Operacional", "Gestión"])
    todo_el_historico = st.checkbox("Incluir todos los registros (ignorar rango de fechas)")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", datetime.today(), disabled=todo_el_historico)
    with col2:
        fecha_fin = st.date_input("Fecha fin", datetime.today(), disabled=todo_el_historico)

    if st.button("Generar PDF"):
        with get_db_connection() as conn:
            # 1. LÓGICA DE FILTRO
            if todo_el_historico:
                condicion = "TRUE"
                params = []
                rango_texto = "Historial Completo"
            else:
                condicion = "t.fecha_hora BETWEEN %s AND %s"
                params = [f"{fecha_inicio} 00:00:00", f"{fecha_fin} 23:59:59"]
                rango_texto = f"del día {fecha_inicio}" if fecha_inicio == fecha_fin else f"del {fecha_inicio} al {fecha_fin}"
            
            # 2. EJECUCIÓN DE QUERY
            if tipo == "Operacional":
                query = f"""
                    SELECT t.id_triaje as ID, p.nombre_completo as Paciente, t.nivel_urgencia as Urgencia, 
                           TO_CHAR(t.fecha_hora, 'DD/MM/YY HH24:MI') as Fecha,
                           t.presion_arterial_sist as Sist, t.presion_arterial_diast as Diast, 
                           t.frecuencia_cardiaca as Frec, t.temperatura as Temp, 
                           t.saturacion_oxigeno as Sat, t.conducta_sugerida as Conducta
                    FROM triajes t
                    JOIN pacientes p ON t.id_paciente = p.id_paciente
                    WHERE {condicion} ORDER BY t.fecha_hora
                """
                df = pd.read_sql(query, conn, params=params)
                titulo = f"Reporte Operacional ({rango_texto})"
            else:
                query = f"""
                    SELECT DATE(t.fecha_hora) AS Fecha, COUNT(*) AS Total,
                           SUM(CASE WHEN nivel_urgencia = 'crítico' THEN 1 ELSE 0 END) AS Críticos,
                           SUM(CASE WHEN nivel_urgencia = 'alto' THEN 1 ELSE 0 END) AS Altos,
                           SUM(CASE WHEN nivel_urgencia = 'moderado' THEN 1 ELSE 0 END) AS Moderados,
                           SUM(CASE WHEN nivel_urgencia = 'bajo' THEN 1 ELSE 0 END) AS Bajos
                    FROM triajes t
                    WHERE {condicion} GROUP BY Fecha ORDER BY Fecha
                """
                df = pd.read_sql(query, conn, params=params)
                titulo = f"Reporte de Gestión ({rango_texto})"

        # 3. LLAMADA A LA FUNCIÓN DE GENERACIÓN
        pdf_buffer = generar_pdf(df, titulo, tipo)
        
        st.success("¡PDF generado con éxito!")
        st.download_button(
            label="⬇️ Descargar Reporte PDF",
            data=pdf_buffer,
            file_name=f"reporte_{tipo.lower()}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

def generar_pdf(df, titulo, tipo):
    buffer = BytesIO()
    # Orientación horizontal para que quepan las columnas
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), 
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    style_cell = styles["Normal"]
    style_cell.fontSize = 8 
    style_cell.alignment = 1 

    story = []
    story.append(Paragraph(f"<b>{titulo}</b>", styles['Title']))
    story.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    if not df.empty:
        data = []
        # Cabeceras con estilo negrita
        header = [Paragraph(f"<b>{col}</b>", style_cell) for col in df.columns]
        data.append(header)
        
        # Filas convertidas a Paragraph para ajuste automático
        for row in df.values.tolist():
            data.append([Paragraph(str(item) if item is not None else "-", style_cell) for item in row])

        # Configuración de anchos según el tipo de reporte
        if tipo == "Operacional":
            # Reparto de puntos (Total ~730 en landscape)
            column_widths = [25, 130, 60, 80, 35, 35, 35, 35, 35, 230]
        else:
            column_widths = None 

        table = Table(data, colWidths=column_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.beige]) # Efecto cebra
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No se encontraron registros para los criterios seleccionados.", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer
