import requests
from fastapi import APIRouter, HTTPException

from backend.config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_HEADERS
from backend.schemas import PreguntaAsistente, RespuestaAsistente
from backend.tools import TOOLS_MAP, TOOLS_SCHEMA

router = APIRouter(prefix="/api/v1", tags=["Asistente IA"])

# Instrucciones del asistente
SYSTEM_PROMPT = """
Eres el asistente virtual del Centro de Eventos.
Responde en español y de forma breve.
Usa las herramientas disponibles para responder preguntas.
"""


def _llamar_ollama(messages: list, incluir_tools: bool) -> dict:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    if incluir_tools:
        payload["tools"] = TOOLS_SCHEMA
    try:
        resp = requests.post(
            OLLAMA_URL + "/chat",
            headers=OLLAMA_HEADERS,
            json=payload,
            timeout=180,
        )
        resp.raise_for_status()
        return resp.json()["message"]
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            503,
            f"No se pudo conectar a Ollama en {OLLAMA_URL}. "
            "Revisa que OLLAMA_URL/OLLAMA_MODEL/OLLAMA_API_KEY en tu .env "
            "sean correctos y que el servicio esté disponible."
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(502, f"Ollama devolvió un error: {e}")


@router.post("/chat", response_model=RespuestaAsistente)
def chat(payload: PreguntaAsistente):
    """
    Endpoint del asistente conversacional (tool calling real):
    1. Se manda la pregunta + el catálogo de herramientas (TOOLS_SCHEMA) a Ollama.
    2. Si el modelo decide usar una herramienta (tool_calls), el backend
       ejecuta la función real de tools.py y le devuelve el resultado.
    3. Se le pide al modelo que redacte la respuesta final en español,
       ya con el dato real (nunca inventado) incorporado.
    """
    pregunta = payload.pregunta.strip()
    if not pregunta:
        raise HTTPException(400, "La pregunta no puede estar vacía.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": pregunta},
    ]

    msg = _llamar_ollama(messages, incluir_tools=True)

    if tool_calls := msg.get("tool_calls"):
        respuestas = []
        contexto = []
        for call in tool_calls:
            nombre_fn = call["function"]["name"]
            args = call["function"]["arguments"]
            fn = TOOLS_MAP.get(nombre_fn)
            if fn is None:
                resultado = f"Herramienta desconocida: {nombre_fn}"
            else:
                try:
                    resultado = fn(**args)
                except Exception as e:
                    resultado = f"Error ejecutando {nombre_fn}: {e}"
            respuestas.append(resultado)
            contexto.append({"nombre": nombre_fn, "argumentos": args})
        texto = "\n".join(respuestas)
        return RespuestaAsistente(respuesta=texto, contexto_usado={"herramientas_usadas": contexto})

    return RespuestaAsistente(
        respuesta=msg["content"],
    )