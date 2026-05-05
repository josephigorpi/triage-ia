import os
import json
import requests
from .prompts import PROMPT_TRIAGE

# Configuración de Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
USE_MOCK = os.getenv('USE_MOCK_IA', 'false').lower() == 'true'

def obtener_recomendacion_ia(datos_triaje):
    """
    Llama a Groq API o retorna una respuesta mock si está configurado.
    """
    if USE_MOCK or not GROQ_API_KEY:
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
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asistente médico especializado en triaje. Responde ÚNICAMENTE con un objeto JSON válido, sin texto adicional ni bloques de código."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "nivel_urgencia": "moderado",
                "conducta_sugerida": "Error al parsear respuesta de IA. Evaluar manualmente.",
                "diagnosticos_diferenciales": "No disponible por error de formato."
            }
        except requests.exceptions.Timeout:
            return {
                "nivel_urgencia": "moderado",
                "conducta_sugerida": "Timeout en IA. Evaluar manualmente.",
                "diagnosticos_diferenciales": "No disponible por timeout."
            }
        except Exception as e:
            return {
                "nivel_urgencia": "moderado",
                "conducta_sugerida": f"Error en IA. Evaluar manualmente.",
                "diagnosticos_diferenciales": "No disponible por error de API."
            }
