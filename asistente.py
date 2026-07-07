import json
import requests
from fastapi import APIRouter, HTTPException

from servicios import AmbienteService, ServicioService
from modelo_regresion import predecir_monto, cargar_modelo_guardado
from backend.config import OLLAMA_URL, OLLAMA_MODEL
from backend.schemas import PreguntaAsistente, RespuestaAsistente

router = APIRouter(prefix="/asistente", tags=["Asistente IA"])
amb_svc = AmbienteService()
srv_svc = ServicioService()


def _llamar_ollama(prompt: str, formato_json: bool = False) -> str:
    """Llama al servidor local de Ollama (ollama serve)."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if formato_json:
        payload["format"] = "json"
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            503,
            f"No se pudo conectar a Ollama en {OLLAMA_URL}. "
            "Verifica que esté corriendo con `ollama serve` y que el modelo "
            f"'{OLLAMA_MODEL}' esté descargado (`ollama pull {OLLAMA_MODEL}`)."
        )
    return resp.json()["response"]


def _extraer_parametros_evento(pregunta: str) -> dict | None:
    """
    Paso 1: le pide al modelo que EXTRAIGA parámetros estructurados
    de la pregunta, si esta pide una cotización/predicción de monto.
    Esto evita que el LLM "invente" el precio: solo extrae datos,
    el cálculo real lo hace nuestro modelo de regresión (predecir_monto).
    """
    prompt = f"""Analiza la siguiente pregunta de un usuario sobre un centro de eventos.
Si la pregunta pide calcular, cotizar o estimar el COSTO/MONTO de una reserva,
responde SOLO con un JSON con esta forma exacta (usa null si falta un dato):
{{"es_cotizacion": true, "tipo_evento": "...", "ambiente": "...", "servicio": "...", "capacidad": 0, "horas": 0}}

Si la pregunta NO pide una cotización (por ejemplo, pregunta por disponibilidad,
recomendaciones de ambiente, o info general), responde SOLO con:
{{"es_cotizacion": false}}

Pregunta: "{pregunta}"

Responde unicamente el JSON, sin texto adicional."""
    try:
        salida = _llamar_ollama(prompt, formato_json=True)
        datos = json.loads(salida)
    except (json.JSONDecodeError, KeyError):
        return None
    if not datos.get("es_cotizacion"):
        return None
    faltan = [c for c in ("tipo_evento", "ambiente", "servicio", "capacidad", "horas")
              if not datos.get(c)]
    if faltan:
        return None
    return datos


def _construir_contexto_negocio() -> dict:
    """Contexto real del sistema que se le da al LLM (no inventa datos)."""
    ambientes = amb_svc.listar_disponibles()
    servicios = srv_svc.listar_todos()
    return {
        "ambientes_disponibles": [
            {"id": a["id"], "nombre": a["nombre"], "tipo": a["tipo"],
             "capacidad": a["capacidad"], "precio_por_hora": a["precio_por_hora"]}
            for a in ambientes
        ],
        "servicios_catalogo": [
            {"id": s["id"], "nombre": s["nombre"], "tipo": s["tipo_servicio"],
             "costo_unitario": s["costo_unitario"]}
            for s in servicios
        ],
    }


@router.post("", response_model=RespuestaAsistente)
def preguntar_asistente(payload: PreguntaAsistente):
    pregunta = payload.pregunta.strip()
    if not pregunta:
        raise HTTPException(400, "La pregunta no puede estar vacía.")

    contexto = _construir_contexto_negocio()
    parametros_cotizacion = None
    prediccion = None

    # Si la pregunta pide un precio, usamos el modelo de regresión (no el LLM)
    if cargar_modelo_guardado() is not None:
        parametros_cotizacion = _extraer_parametros_evento(pregunta)
        if parametros_cotizacion:
            try:
                prediccion = predecir_monto({
                    "tipo_evento": parametros_cotizacion["tipo_evento"],
                    "ambiente":    parametros_cotizacion["ambiente"],
                    "servicio":    parametros_cotizacion["servicio"],
                    "capacidad":   parametros_cotizacion["capacidad"],
                    "horas":       parametros_cotizacion["horas"],
                })
            except Exception:
                prediccion = None

    prompt_final = f"""Eres el asistente virtual del Centro de Eventos (Caso 6).
Responde en español, de forma breve y clara, usando SOLO la información de contexto
que se te da a continuación. No inventes ambientes, precios ni servicios que no
aparezcan en el contexto.

Contexto del sistema (datos reales, actualizados):
{json.dumps(contexto, ensure_ascii=False, indent=2)}
"""
    if prediccion is not None:
        prompt_final += f"""
Predicción calculada por el modelo de Machine Learning (regresión lineal
entrenado con datos históricos de reservas) para el evento consultado:
Monto estimado: S/ {prediccion:.2f}
Usa este monto tal cual en tu respuesta; no lo recalcules ni lo cambies.
"""

    prompt_final += f'\nPregunta del usuario: "{pregunta}"\nRespuesta:'

    respuesta = _llamar_ollama(prompt_final)

    return RespuestaAsistente(
        respuesta=respuesta.strip(),
        contexto_usado={
            "prediccion_monto": prediccion,
            "parametros_detectados": parametros_cotizacion,
        },
    )