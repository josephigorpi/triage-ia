# Sistema de Triaje Clínico Asistido por IA

## Prerrequisitos
- Docker y Docker Compose
- Python 3.10+ (solo si se ejecuta fuera de Docker)
- Cuenta de OpenAI (opcional, para IA real)

## Configuración inicial
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/triage-ia.git
   cd triage-ia
    2. Copiar .env.example a .env y editar las variables necesarias (especialmente OPENAI_API_KEY si se desea usar IA real).
    3. Levantar los servicios con Docker Compose:
bash
docker-compose up -d
    4. La base de datos se inicializa automáticamente con schema.sql.
    5. Importar los workflows de n8n:
        ◦ Acceder a http://localhost:5678 (usuario: admin, contraseña: admin123).
        ◦ En la interfaz de n8n, ir a "Workflows" → "Import" y subir los archivos JSON de backend/n8n-workflows/.
        ◦ Activar los workflows.
    6. La aplicación Streamlit estará disponible en http://localhost:8501.
        ◦ Usuario por defecto: admin, contraseña: admin123 (definida en el script SQL, cambiar en producción).
    7. El mock HCE estará en http://localhost:5001.