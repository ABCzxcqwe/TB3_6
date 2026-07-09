import requests
from fastapi import APIRouter, HTTPException

from backend.config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_HEADERS
from backend.schemas import PreguntaAsistente, RespuestaAsistente
from backend.tools import TOOLS_MAP, TOOLS_SCHEMA

router = APIRouter(prefix="/api/v1", tags=["Asistente IA"])

# Instrucciones del asistente (rol del sistema, igual que SYSTEM_PROMPT de PagoYa)
SYSTEM_PROMPT = """
Eres el asistente virtual del Centro de Eventos (Caso 6).
Usa las herramientas disponibles para consultar ambientes, verificar
disponibilidad, cotizar eventos, consultar reservas de clientes y crear
reservas reales en el sistema.
Identifica ambientes y clientes por su NOMBRE (nunca pidas ni uses ids
como AMB-001 o CLI-001); las herramientas los buscan internamente.
Para calcular cualquier precio o costo, SIEMPRE usa la herramienta
cotizar_evento; nunca inventes un monto tu mismo.
Responde en español y de forma breve.
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
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            503,
            f"No se pudo conectar a Ollama en {OLLAMA_URL}. "
            "Revisa que OLLAMA_URL/OLLAMA_MODEL/OLLAMA_API_KEY en tu .env "
            "sean correctos y que el servicio esté disponible."
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(502, f"Ollama devolvió un error: {e}")
    return resp.json()["message"]


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

    herramientas_usadas = []
    if tool_calls := msg.get("tool_calls"):
        messages.append(msg)
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
            herramientas_usadas.append({"nombre": nombre_fn, "argumentos": args})
            messages.append({"role": "tool", "content": resultado})

        # segunda llamada: el modelo redacta la respuesta final con los datos reales
        msg = _llamar_ollama(messages, incluir_tools=False)

    return RespuestaAsistente(
        respuesta=msg["content"],
        contexto_usado={"herramientas_usadas": herramientas_usadas} if herramientas_usadas else None,
    )