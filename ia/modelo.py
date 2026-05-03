import os
import json
import requests
from .prompts import PROMPT_TRIAGE

# Configuración de OpenAI (o simulación)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_MOCK = os.getenv('USE_MOCK_IA', 'true').lower() == 'true'

def obtener_recomendacion_ia(datos_triaje):
    """
    Llama a OpenAI API o retorna una respuesta mock si no hay clave.
    """
    if USE_MOCK or not OPENAI_API_KEY:
        # Respuesta simulada para pruebas
        return {
            "nivel_urgencia": "moderado",
            "conducta_sugerida": "Realizar evaluación médica en las próximas 2 horas.",
            "diagnosticos_diferenciales": "Infección respiratoria, deshidratación, ansiedad."
        }
    else:
        prompt = PROMPT_TRIAGE.format(
            presion_arterial_sist=datos_triaje['presion_arterial_sist'],
            presion_arterial_diast=datos_triaje['presion_arterial_diast'],
            frecuencia_cardiaca=datos_triaje['frecuencia_cardiaca'],
            temperatura=datos_triaje['temperatura'],
            saturacion_oxigeno=datos_triaje['saturacion_oxigeno'],
            sintomas=datos_triaje['sintomas']
        )
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            # Intentar parsear JSON
            return json.loads(content)
        except Exception as e:
            # Fallback mock
            return {
                "nivel_urgencia": "moderado",
                "conducta_sugerida": "Error en IA. Evaluar manualmente.",
                "diagnosticos_diferenciales": "No disponible por error de API."
            }