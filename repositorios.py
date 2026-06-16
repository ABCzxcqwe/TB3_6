# ─────────────────────────────────────────────
#  REPOSITORIOS — Capa de acceso a datos
#  Adaptado al diagrama UML (Grupo 6)
# ─────────────────────────────────────────────

from abc import ABC, abstractmethod
from csv_helper import CSVHelper


# ==================== INTERFAZ BASE ====================

class IRepository(ABC):
    """Interfaz base — contrato que todos los repositorios deben cumplir."""

    @abstractmethod
    def obtener_todos(self) -> list: pass

    @abstractmethod
    def guardar(self, entidad: dict) -> None: pass

    @abstractmethod
    def buscar(self, id: str) -> dict: pass

    @abstractmethod
    def eliminar(self, id: str) -> bool: pass

    @abstractmethod
    def actualizar(self, id: str, datos: dict) -> bool: pass


# ==================== AMBIENTE ====================

class AmbienteRepository(IRepository):
    ARCHIVO = "ambientes.csv"
    CAMPOS  = ["id", "nombre", "tipo", "capacidad",
               "precio_por_hora", "esta_disponible"]

    def __init__(self):
        self.csv_helper = CSVHelper()

    def obtener_todos(self) -> list:
        return self.csv_helper.leer_csv(self.ARCHIVO, self.CAMPOS)

    def guardar(self, ambiente: dict) -> None:
        self.csv_helper.escribir_csv(self.ARCHIVO, [ambiente], self.CAMPOS)

    def buscar(self, id: str) -> dict:
        return next((a for a in self.obtener_todos()
                     if a["id"] == id), None)

    def eliminar(self, id: str) -> bool:
        return self.csv_helper.eliminar_csv(self.ARCHIVO, id)

    def actualizar(self, id: str, datos: dict) -> bool:
        return self.csv_helper.actualizar_csv(self.ARCHIVO, id, datos)

    # ── Filtros específicos (UML) ─────────────
    def filtrar_por_tipo(self, tipo: str) -> list:
        return [a for a in self.obtener_todos()
                if a["tipo"].lower() == tipo.lower()]

    def filtrar_por_capacidad_minima(self, capacidad: int) -> list:
        return [a for a in self.obtener_todos()
                if int(a["capacidad"]) >= capacidad]

    def obtener_disponibles(self) -> list:
        return [a for a in self.obtener_todos()
                if str(a["esta_disponible"]).lower()
                in ("true", "1", "sí", "si")]


# ==================== CLIENTE ====================

class ClienteRepository(IRepository):
    ARCHIVO = "clientes.csv"
    CAMPOS  = ["id", "nombre", "email",
               "telefono", "direccion", "documento"]

    def __init__(self):
        self.csv_helper = CSVHelper()

    def obtener_todos(self) -> list:
        return self.csv_helper.leer_csv(self.ARCHIVO, self.CAMPOS)

    def guardar(self, cliente: dict) -> None:
        self.csv_helper.escribir_csv(self.ARCHIVO, [cliente], self.CAMPOS)

    def buscar(self, id: str) -> dict:
        return next((c for c in self.obtener_todos()
                     if c["id"] == id), None)

    def eliminar(self, id: str) -> bool:
        return self.csv_helper.eliminar_csv(self.ARCHIVO, id)

    def actualizar(self, id: str, datos: dict) -> bool:
        return self.csv_helper.actualizar_csv(self.ARCHIVO, id, datos)

    # ── Búsquedas específicas (UML) ───────────
    def buscar_por_email(self, email: str) -> dict:
        return next((c for c in self.obtener_todos()
                     if c["email"].lower() == email.lower()), None)

    def buscar_por_documento(self, documento: str) -> dict:
        return next((c for c in self.obtener_todos()
                     if c["documento"] == documento), None)


# ==================== SERVICIO ADICIONAL ====================

class ServicioRepository(IRepository):
    ARCHIVO = "servicios.csv"
    CAMPOS  = ["id", "nombre", "descripcion",
               "costo_unitario", "tipo_servicio"]

    def __init__(self):
        self.csv_helper = CSVHelper()

    def obtener_todos(self) -> list:
        return self.csv_helper.leer_csv(self.ARCHIVO, self.CAMPOS)

    def guardar(self, servicio: dict) -> None:
        self.csv_helper.escribir_csv(self.ARCHIVO, [servicio], self.CAMPOS)

    def buscar(self, id: str) -> dict:
        return next((s for s in self.obtener_todos()
                     if s["id"] == id), None)

    def eliminar(self, id: str) -> bool:
        return self.csv_helper.eliminar_csv(self.ARCHIVO, id)

    def actualizar(self, id: str, datos: dict) -> bool:
        return self.csv_helper.actualizar_csv(self.ARCHIVO, id, datos)

    # ── Filtro específico (UML) ───────────────
    def filtrar_por_tipo(self, tipo: str) -> list:
        return [s for s in self.obtener_todos()
                if s["tipo_servicio"].lower() == tipo.lower()]


# ==================== RESERVA ====================

class ReservaRepository(IRepository):
    ARCHIVO          = "reservas.csv"
    ARCHIVO_SERVICIOS = "reservas_servicios.csv"
    CAMPOS_RESERVA   = ["id", "cliente_id", "ambiente_id", "fecha",
                        "hora_inicio", "hora_fin", "estado", "costo_total"]
    CAMPOS_SERVICIOS = ["reserva_id", "servicio_id", "cantidad", "costo"]

    def __init__(self):
        self.csv_helper = CSVHelper()

    # ── IRepository ──────────────────────────
    def obtener_todos(self) -> list:
        return self.csv_helper.leer_csv(self.ARCHIVO, self.CAMPOS_RESERVA)

    # Alias semántico usado por los servicios
    def obtener_todas(self) -> list:
        return self.obtener_todos()

    def guardar(self, reserva: dict,
                servicios: list = None) -> None:
        self.csv_helper.escribir_csv(
            self.ARCHIVO, [reserva], self.CAMPOS_RESERVA)
        if servicios:
            self.csv_helper.escribir_csv(
                self.ARCHIVO_SERVICIOS, servicios, self.CAMPOS_SERVICIOS)

    def buscar(self, id: str) -> dict:
        return next((r for r in self.obtener_todos()
                     if r["id"] == id), None)

    def eliminar(self, id: str) -> bool:
        ok = self.csv_helper.eliminar_csv(self.ARCHIVO, id)
        # También elimina los servicios asociados
        servicios = self.obtener_servicios_reserva(id)
        for s in servicios:
            self.csv_helper.eliminar_csv(
                self.ARCHIVO_SERVICIOS, s["reserva_id"])
        return ok

    def actualizar(self, id: str, datos: dict) -> bool:
        return self.csv_helper.actualizar_csv(self.ARCHIVO, id, datos)

    # ── Métodos adicionales (UML) ─────────────
    def obtener_servicios_reserva(self, reserva_id: str) -> list:
        todos = self.csv_helper.leer_csv(
            self.ARCHIVO_SERVICIOS, self.CAMPOS_SERVICIOS)
        return [s for s in todos if s["reserva_id"] == reserva_id]

    def filtrar_por_fecha(self, fecha: str) -> list:
        return [r for r in self.obtener_todos()
                if r["fecha"] == fecha]

    def filtrar_por_ambiente(self, ambiente_id: str) -> list:
        return [r for r in self.obtener_todos()
                if r["ambiente_id"] == ambiente_id
                and r["estado"] == "confirmada"]

    def filtrar_por_cliente(self, cliente_id: str) -> list:
        return [r for r in self.obtener_todos()
                if r["cliente_id"] == cliente_id]

    def filtrar_por_estado(self, estado: str) -> list:
        return [r for r in self.obtener_todos()
                if r["estado"].lower() == estado.lower()]

    def filtrar_por_fecha_rango(self, fecha_ini: str,
                                 fecha_fin: str) -> list:
        return [r for r in self.obtener_todos()
                if fecha_ini <= r["fecha"] <= fecha_fin]

    def agregar_servicio(self, fila: dict) -> None:
        """Agrega una fila a reservas_servicios.csv."""
        self.csv_helper.escribir_csv(
            self.ARCHIVO_SERVICIOS, [fila], self.CAMPOS_SERVICIOS)

    def quitar_servicio(self, reserva_id: str,
                        servicio_id: str) -> bool:
        """Elimina la fila de un servicio en reservas_servicios.csv.
        Retorna True si existía y fue eliminada."""
        todos = self.csv_helper.leer_csv(
            self.ARCHIVO_SERVICIOS, self.CAMPOS_SERVICIOS)
        filtrados = [s for s in todos
                     if not (s["reserva_id"] == reserva_id
                             and s["servicio_id"] == servicio_id)]
        if len(filtrados) == len(todos):
            return False
        self.csv_helper._reescribir(self.ARCHIVO_SERVICIOS, filtrados)
        return True

    def verificar_conflictos(self, ambiente_id: str, fecha: str,
                              hora_inicio: str, hora_fin: str) -> bool:
        """Retorna True si HAY conflicto (el horario está ocupado)."""
        for r in self.filtrar_por_ambiente(ambiente_id):
            if r["fecha"] == fecha:
                if not (hora_fin <= r["hora_inicio"]
                        or hora_inicio >= r["hora_fin"]):
                    return True
        return False