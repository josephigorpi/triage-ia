import os
import bcrypt
import psycopg2
import psycopg2.extras
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuración de la base de datos desde variables de entorno
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'triaje_ia'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    """Retorna una conexión a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)

def verificar_usuario(username, password):
    """Verifica credenciales contra la tabla usuarios."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT id_usuario, nombre_usuario, contrasena_hash, rol FROM usuarios WHERE nombre_usuario = %s", (username,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user['contrasena_hash'].encode('utf-8')):
                return dict(user)
    return None

def registrar_log(id_usuario, accion, detalles, ip_origen=''):
    """Registra una acción en logs_auditoria."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO logs_auditoria (id_usuario, accion, detalles, ip_origen)
                VALUES (%s, %s, %s, %s)
            """, (id_usuario, accion, detalles, ip_origen))
            conn.commit()

def obtener_pacientes():
    """Retorna lista de pacientes para selectores."""
    with get_db_connection() as conn:
        return pd.read_sql("SELECT id_paciente, nombre_completo FROM pacientes ORDER BY nombre_completo", conn)

def guardar_triaje(data):
    """Guarda un triaje y su resultado IA, retorna id_triaje."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Convertir valores numpy a tipos nativos de Python
            def to_native(val):
                if hasattr(val, 'item'):  # Detecta numpy types
                    return val.item()
                return val
            
            cur.execute("""
                INSERT INTO triajes (id_paciente, id_usuario, presion_arterial_sist, presion_arterial_diast,
                                     frecuencia_cardiaca, temperatura, saturacion_oxigeno, sintomas,
                                     nivel_urgencia, conducta_sugerida)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_triaje
            """, (
                to_native(data['id_paciente']),
                to_native(data['id_usuario']),
                to_native(data.get('presion_arterial_sist')),
                to_native(data.get('presion_arterial_diast')),
                to_native(data.get('frecuencia_cardiaca')),
                to_native(data.get('temperatura')),
                to_native(data.get('saturacion_oxigeno')),
                data.get('sintomas'),
                data.get('nivel_urgencia'),
                data.get('conducta_sugerida')
            ))
            id_triaje = cur.fetchone()[0]
            
            # Guardar resultado IA si existe
            if 'resultado_ia' in data:
                cur.execute("""
                    INSERT INTO resultados_ia (id_triaje, nivel_urgencia_ia, conducta_sugerida_ia, diagnosticos_diferenciales)
                    VALUES (%s, %s, %s, %s)
                """, (id_triaje, data['resultado_ia']['nivel_urgencia'],
                      data['resultado_ia']['conducta_sugerida'],
                      data['resultado_ia']['diagnosticos_diferenciales']))
            conn.commit()
            return id_triaje