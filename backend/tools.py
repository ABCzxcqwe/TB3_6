"""
Herramientas del asistente de IA generativa - Caso 6 (Centro de Eventos)

Sigue el mismo patrón que el ejemplo del profesor (PagoYa):
- Cada función traduce una intención del usuario en una operación real
  sobre los datos del sistema (aquí, vía servicios.py en vez de SQL
  directo, porque el Caso 6 persiste en CSV, no en SQLite).
- TOOLS_MAP conecta el nombre de la herramienta con la función Python.
- TOOLS_SCHEMA describe cada herramienta en el formato que Ollama
  espera para decidir cuándo y con qué argumentos llamarla
  (tool calling / function calling).
"""

from servicios import AmbienteService, ClienteService, ReservaService
from modelo_regresion import predecir_monto, cargar_modelo_guardado

amb_svc = AmbienteService()
cli_svc = ClienteService()
res_svc = ReservaService()


# ───────────────────── Búsquedas internas por nombre ─────────────────────
# El asistente trabaja con NOMBRES (no con ids AMB-001/CLI-001, difíciles
# de recordar para un usuario). Estas funciones resuelven el nombre a id.

def _buscar_ambiente_por_nombre(nombre: str) -> dict | None:
    nombre = nombre.lower().strip()
    for a in amb_svc.listar_todos():
        if nombre in a["nombre"].lower():
            return a
    return None


def _buscar_cliente_por_nombre(nombre: str) -> dict | None:
    nombre = nombre.lower().strip()
    for c in cli_svc.listar_todos():
        if nombre in c["nombre"].lower():
            return c
    return None


# ───────────────────────── Herramientas (tools) ──────────────────────────

def listar_ambientes_disponibles(tipo: str = "") -> str:
    """1) «¿Qué ambientes tienen disponibles?» -> lista ambientes libres."""
    ambientes = amb_svc.listar_disponibles()
    if tipo:
        ambientes = [a for a in ambientes if a["tipo"].lower() == tipo.lower()]
    if not ambientes:
        return "No hay ambientes disponibles" + (f" del tipo {tipo}" if tipo else "") + "."
    texto = "Ambientes disponibles:\n"
    for a in ambientes:
        texto += (f"- {a['nombre']} ({a['tipo']}), capacidad {a['capacidad']} "
                  f"personas, S/ {a['precio_por_hora']}/hora\n")
    return texto


def verificar_disponibilidad(ambiente: str, fecha: str,
                              hora_inicio: str, hora_fin: str) -> str:
    """2) «¿Está libre el Salón 12 el 20 de agosto de 3pm a 6pm?»"""
    amb = _buscar_ambiente_por_nombre(ambiente)
    if amb is None:
        return f"No encontré ningún ambiente llamado '{ambiente}'."
    libre = amb_svc.verificar_disponibilidad(amb["id"], fecha, hora_inicio, hora_fin)
    estado = "SÍ está disponible" if libre else "NO está disponible (ya reservado)"
    return f"El ambiente {amb['nombre']} {estado} el {fecha} de {hora_inicio} a {hora_fin}."


def cotizar_evento(tipo_evento: str, ambiente: str, servicio: str,
                    capacidad: int, horas: int) -> str:
    """3) «¿Cuánto costaría una boda para 300 personas en el Salón 12,
    6 horas, con catering?» -> usa el modelo de Machine Learning ya
    entrenado (modelo_regresion.py), NO inventa el precio."""
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


def listar_reservas_cliente(cliente: str) -> str:
    """4) «Muéstrame las reservas de Juan Pérez»"""
    cli = _buscar_cliente_por_nombre(cliente)
    if cli is None:
        return f"No encontré ningún cliente llamado '{cliente}'."
    reservas = res_svc.listar_reservas_por_cliente(cli["id"])
    if not reservas:
        return f"{cli['nombre']} no tiene reservas registradas."
    texto = f"Reservas de {cli['nombre']}:\n"
    for r in reservas:
        texto += (f"- {r['fecha']} {r['hora_inicio']}-{r['hora_fin']} "
                  f"| Estado: {r['estado']} | S/ {r.get('costo_total', '?')}\n")
    return texto


def crear_reserva_rapida(ambiente: str, cliente: str, fecha: str,
                          hora_inicio: str, hora_fin: str) -> str:
    """5) «Reserva el Auditorio A para María López el 2026-08-20 de 10:00 a 14:00»"""
    amb = _buscar_ambiente_por_nombre(ambiente)
    if amb is None:
        return f"No encontré ningún ambiente llamado '{ambiente}'."
    cli = _buscar_cliente_por_nombre(cliente)
    if cli is None:
        return f"No encontré ningún cliente llamado '{cliente}'."
    reserva = res_svc.crear_reserva({
        "ambiente_id": amb["id"], "cliente_id": cli["id"],
        "fecha": fecha, "hora_inicio": hora_inicio, "hora_fin": hora_fin,
    })
    if reserva is None:
        return (f"No se pudo crear la reserva. Verifica que {amb['nombre']} "
                f"esté libre en ese horario.")
    return (f"Reserva creada: {amb['nombre']} para {cli['nombre']} el {fecha} "
            f"de {hora_inicio} a {hora_fin}. Costo total: S/ {reserva.get_costo_total():.2f}")


def ambiente_mas_reservado(fecha_inicio: str, fecha_fin: str) -> str:
    """6) «¿Cuál fue el ambiente más reservado en julio?»"""
    from servicios import ReporteService
    rep_svc = ReporteService()
    amb = rep_svc.obtener_ambiente_mas_reservado(fecha_inicio, fecha_fin)
    if not amb:
        return f"No hay reservas confirmadas entre {fecha_inicio} y {fecha_fin}."
    return (f"El ambiente más reservado entre {fecha_inicio} y {fecha_fin} fue "
            f"{amb.get('nombre')} con {amb.get('reservas')} reserva(s).")


# ─────────────────── TOOLS_MAP y TOOLS_SCHEMA (Ollama) ───────────────────

TOOLS_MAP = {
    "listar_ambientes_disponibles": listar_ambientes_disponibles,
    "verificar_disponibilidad":     verificar_disponibilidad,
    "cotizar_evento":                cotizar_evento,
    "listar_reservas_cliente":      listar_reservas_cliente,
    "crear_reserva_rapida":         crear_reserva_rapida,
    "ambiente_mas_reservado":       ambiente_mas_reservado,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "listar_ambientes_disponibles",
            "description": "Lista los ambientes disponibles del centro de eventos, opcionalmente filtrando por tipo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string",
                             "description": "Tipo de ambiente: salon, auditorio, terraza, sala_de_reuniones, jardin. Opcional."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_disponibilidad",
            "description": "Verifica si un ambiente está libre en una fecha y tramo horario específicos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ambiente": {"type": "string", "description": "Nombre del ambiente, ej. 'Salon 12'"},
                    "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                    "hora_inicio": {"type": "string", "description": "Hora de inicio HH:MM"},
                    "hora_fin": {"type": "string", "description": "Hora de fin HH:MM"},
                },
                "required": ["ambiente", "fecha", "hora_inicio", "hora_fin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cotizar_evento",
            "description": "Calcula el monto estimado de una reserva usando el modelo de Machine Learning entrenado con datos historicos. Usar SIEMPRE que el usuario pida un precio, costo o cotizacion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo_evento": {"type": "string", "description": "Ej: Boda, Cumpleanos, Corporativo, Graduacion, Concierto, Conferencia"},
                    "ambiente": {"type": "string", "description": "Nombre del ambiente, ej. 'Salon 12'"},
                    "servicio": {"type": "string", "description": "Servicio adicional, ej: Catering, Audiovisual, Ninguno"},
                    "capacidad": {"type": "number", "description": "Cantidad de personas"},
                    "horas": {"type": "number", "description": "Duracion del evento en horas"},
                },
                "required": ["tipo_evento", "ambiente", "servicio", "capacidad", "horas"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_reservas_cliente",
            "description": "Lista todas las reservas de un cliente, buscando por su nombre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente": {"type": "string", "description": "Nombre completo o parcial del cliente"},
                },
                "required": ["cliente"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_reserva_rapida",
            "description": "Crea una nueva reserva para un cliente en un ambiente, en una fecha y horario dados.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ambiente": {"type": "string", "description": "Nombre del ambiente"},
                    "cliente": {"type": "string", "description": "Nombre del cliente"},
                    "fecha": {"type": "string", "description": "Fecha YYYY-MM-DD"},
                    "hora_inicio": {"type": "string", "description": "HH:MM"},
                    "hora_fin": {"type": "string", "description": "HH:MM"},
                },
                "required": ["ambiente", "cliente", "fecha", "hora_inicio", "hora_fin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ambiente_mas_reservado",
            "description": "Indica cual fue el ambiente con mas reservas confirmadas en un rango de fechas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {"type": "string", "description": "YYYY-MM-DD"},
                    "fecha_fin": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["fecha_inicio", "fecha_fin"],
            },
        },
    },
]