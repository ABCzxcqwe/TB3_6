from servicios import EspacioService, UsuarioService, EventoService, ReporteService
from modelo_regresion import predecir_monto, cargar_modelo_guardado

esp_svc = EspacioService()
usr_svc = UsuarioService()
evt_svc = EventoService()


def _normalizar(texto: str) -> str:
    """Elimina tildes y diéresis para búsqueda sin distinguir acentos."""
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n",
        "Á": "a", "É": "e", "Í": "i", "Ó": "o", "Ú": "u",
        "Ü": "u", "Ñ": "n",
    }
    for a, b in replacements.items():
        texto = texto.replace(a, b)
    return texto


def _buscar_espacio_por_nombre(nombre: str) -> dict | None:
    nombre = _normalizar(nombre.strip().lower())
    for a in esp_svc.listar_todos():
        if nombre in _normalizar(a["nombre"].lower()):
            return a
    return None


def _buscar_usuario_por_nombre(nombre: str) -> dict | None:
    return usr_svc.buscar_por_nombre(nombre)


def listar_espacios() -> str:
    """Lista todos los espacios del centro de eventos."""
    espacios = esp_svc.listar_todos()
    if not espacios:
        return "No hay espacios registrados."
    return "Espacios:\n" + "\n".join(f"- {e['nombre']}" for e in espacios)


def verificar_disponibilidad(espacio: str, fecha: str) -> str:
    """Verifica si un espacio está disponible en una fecha específica."""
    esp = _buscar_espacio_por_nombre(espacio)
    if esp is None:
        return f"No encontré ningún espacio llamado '{espacio}'."
    libre = evt_svc.verificar_disponibilidad(esp["id"], fecha)
    estado = "SÍ está disponible" if libre else "NO está disponible (ya tiene un evento)"
    return f"El espacio {esp['nombre']} {estado} el {fecha}."


def cotizar_precio(tipo_evento: str, ambiente: str, servicio: str,
                    capacidad: int, horas: int) -> str:
    """Usa el modelo ML para cotizar un evento."""
    if cargar_modelo_guardado() is None:
        return ("El modelo de predicción de montos aún no ha sido entrenado. "
                 "Ejecuta ejecutar_regresion_completa() en modelo_regresion.py primero.")
    try:
        monto = predecir_monto({
            "tipo_evento": tipo_evento, "ambiente": ambiente,
            "servicio": servicio, "capacidad": capacidad, "horas": horas,
        })
    except Exception as e:
        return f"No pude calcular la cotización: {e}"
    return (f"Cotización estimada para {tipo_evento} en {ambiente}, "
            f"{capacidad} personas, {horas} horas, con {servicio}: "
            f"S/ {monto:.2f} (según el modelo de regresión entrenado con datos históricos).")


def listar_eventos_usuario(usuario: str) -> str:
    """Lista los eventos de un usuario por su nombre."""
    cli = _buscar_usuario_por_nombre(usuario)
    if cli is None:
        return f"No encontré ningún usuario llamado '{usuario}'."
    eventos = evt_svc.listar_por_usuario(cli["id"])
    if not eventos:
        return f"{cli['nombre']} no tiene eventos registrados."
    texto = f"Eventos de {cli['nombre']}:\n"
    for e in eventos:
        texto += f"- {e['fecha']} | Espacio ID: {e['espacio_id']} | S/ {e.get('costo', 0)}\n"
    return texto


def crear_evento(espacio: str, usuario: str, fecha: str,
                 costo: float = 0.0, descripcion: str = "") -> str:
    """Crea un nuevo evento para un usuario en un espacio en una fecha dada."""
    esp = _buscar_espacio_por_nombre(espacio)
    if esp is None:
        return f"No encontré ningún espacio llamado '{espacio}'."
    cli = _buscar_usuario_por_nombre(usuario)
    if cli is None:
        return f"No encontré ningún usuario llamado '{usuario}'."
    if not evt_svc.verificar_disponibilidad(esp["id"], fecha):
        return f"El espacio {esp['nombre']} ya tiene un evento el {fecha}."
    resultado = evt_svc.crear({
        "espacio_id": esp["id"], "usuario_id": cli["id"],
        "fecha": fecha, "costo": costo, "descripcion": descripcion,
    })
    if resultado is None:
        return "No se pudo crear el evento."
    return (f"Evento creado: {esp['nombre']} para {cli['nombre']} el {fecha}. "
            f"Costo: S/ {costo:.2f}" + (f" ({descripcion})" if descripcion else ""))


def espacio_mas_utilizado(fecha_inicio: str, fecha_fin: str) -> str:
    """Indica cuál fue el espacio con más eventos en un rango de fechas."""
    rep = ReporteService()
    esp = rep.espacio_mas_utilizado(fecha_inicio, fecha_fin)
    if not esp:
        return f"No hay eventos entre {fecha_inicio} y {fecha_fin}."
    return (f"El espacio más utilizado entre {fecha_inicio} y {fecha_fin} fue "
            f"{esp.get('nombre')} con {esp.get('eventos')} evento(s).")


TOOLS_MAP = {
    "listar_espacios":             listar_espacios,
    "verificar_disponibilidad":    verificar_disponibilidad,
    "cotizar_precio":              cotizar_precio,
    "listar_eventos_usuario":     listar_eventos_usuario,
    "crear_evento":                crear_evento,
    "espacio_mas_utilizado":      espacio_mas_utilizado,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "listar_espacios",
            "description": "Lista todos los espacios del centro de eventos. USA esta herramienta cuando el usuario pregunte 'que espacios hay', 'listame los espacios' o similar.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_disponibilidad",
            "description": "Verifica si un espacio esta disponible en una fecha especifica (sin evento asignado). Cuando el usuario pregunte 'esta libre X espacio el Y date', USA esta herramienta. IMPORTANTE: pasa exactamente el nombre del espacio que dijo el usuario, ej. si dice 'Salon 12', pasa 'Salon 12' como valor de 'espacio'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "espacio": {"type": "string", "description": "Nombre exacto del espacio que el usuario pregunto, ej. 'Salon 12', 'Auditorio B'."},
                    "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                },
                "required": ["espacio", "fecha"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cotizar_precio",
            "description": "Calcula el monto estimado de un evento usando el modelo de Machine Learning entrenado con datos historicos. USA ESTA HERRAMIENTA SIEMPRE que el usuario pregunte por precio, costo, cotizacion, 'cuanto costaria', 'cuanto vale'. NUNCA inventes un monto, USA SIEMPRE esta herramienta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_evento": {"type": "string", "description": "Tipo de evento que el usuario menciona, ej: Boda, Cumpleanos, Corporativo, Graduacion, Concierto, Conferencia"},
                    "ambiente": {"type": "string", "description": "Nombre del espacio/ambiente del evento"},
                    "servicio": {"type": "string", "description": "Servicio adicional, ej: Catering, Audiovisual, Decoracion, Seguridad, Fotografia, Sonido, Ninguno"},
                    "capacidad": {"type": "number", "description": "Cantidad de personas para el evento"},
                    "horas": {"type": "number", "description": "Duracion del evento en horas"},
                },
                "required": ["tipo_evento", "ambiente", "servicio", "capacidad", "horas"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_eventos_usuario",
            "description": "Lista todos los eventos de un usuario, buscando por su nombre. USA cuando el usuario diga 'muestrame los eventos de Juan', 'que eventos tiene Maria'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "usuario": {"type": "string", "description": "Nombre del usuario que el usuario menciona"},
                },
                "required": ["usuario"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_evento",
            "description": "Crea un nuevo evento para un usuario en un espacio en una fecha dada. USA cuando el usuario diga 'reserva X espacio para Y usuario el Z date', 'crea un evento'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "espacio": {"type": "string", "description": "Nombre del espacio"},
                    "usuario": {"type": "string", "description": "Nombre del usuario"},
                    "fecha": {"type": "string", "description": "Fecha del evento en formato YYYY-MM-DD"},
                    "costo": {"type": "number", "description": "Costo del evento (opcional, default 0)"},
                    "descripcion": {"type": "string", "description": "Descripcion del evento (opcional)"},
                },
                "required": ["espacio", "usuario", "fecha"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "espacio_mas_utilizado",
            "description": "Indica cual fue el espacio con mas eventos en un rango de fechas. USA cuando el usuario pregunte 'cual fue el espacio mas utilizado', 'cual fue el ambiente mas reservado', 'que espacio tuvo mas eventos' en un periodo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string", "description": "Fecha de inicio del rango en formato YYYY-MM-DD"},
                    "fecha_fin": {"type": "string", "description": "Fecha de fin del rango en formato YYYY-MM-DD"},
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
]
