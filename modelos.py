# ─────────────────────────────────────────────
#  MODELOS — Capa de dominio
#  Adaptado al diagrama UML (Grupo 6)
# ─────────────────────────────────────────────

from enum import Enum
import uuid


# ==================== ENUMERACIONES ====================

class TipoAmbiente(Enum):
    SALON            = "salon"
    AUDITORIO        = "auditorio"
    TERRAZA          = "terraza"
    SALA_DE_REUNIONES = "sala_de_reuniones"
    JARDIN           = "jardin"


class TipoServicio(Enum):
    CATERING         = "catering"
    AUDIOVISUAL      = "audiovisual"
    PERSONAL_APOYO   = "personal_apoyo"
    DECORACION       = "decoracion"
    SEGURIDAD        = "seguridad"


class EstadoReserva(Enum):
    PENDIENTE   = "pendiente"
    CONFIRMADA  = "confirmada"
    CANCELADA   = "cancelada"
    COMPLETADA  = "completada"


# ==================== MODELOS ====================

class Ambiente:
    """Un salón, auditorio o terraza del centro de eventos."""

    def __init__(self, nombre: str, tipo: str,
                 capacidad: int, precio_por_hora: float):
        self.__id              = str(uuid.uuid4())[:8].upper()
        self.__nombre          = nombre
        self.__tipo            = tipo
        self.__capacidad       = capacidad
        self.__precio_por_hora = precio_por_hora
        self.__esta_disponible = True

    # ── Getters ──────────────────────────────
    def get_id(self):              return self.__id
    def get_nombre(self):          return self.__nombre
    def get_tipo(self):            return self.__tipo
    def get_capacidad(self):       return self.__capacidad
    def get_precio_por_hora(self): return self.__precio_por_hora
    def is_disponible(self):       return self.__esta_disponible

    def set_disponible(self, estado: bool):
        self.__esta_disponible = estado

    # ── Métodos UML ───────────────────────────
    def validar_disponibilidad(self, fecha: str,
                               hora_inicio: str, hora_fin: str) -> bool:
        if not self.__esta_disponible:
            return False
        if hora_inicio >= hora_fin:
            return False
        return True

    def calcular_costo(self, horas: int) -> float:
        return horas * self.__precio_por_hora

    def to_dict(self) -> dict:
        return {
            "id":              self.__id,
            "nombre":          self.__nombre,
            "tipo":            self.__tipo,
            "capacidad":       self.__capacidad,
            "precio_por_hora": self.__precio_por_hora,
            "esta_disponible": self.__esta_disponible,
        }

    def mostrar_info(self) -> str:
        estado = "Disponible" if self.__esta_disponible else "No disponible"
        return (f"[{self.__id}] {self.__nombre} | Tipo: {self.__tipo} | "
                f"Cap: {self.__capacidad} | "
                f"S/. {self.__precio_por_hora}/h | {estado}")


class Cliente:
    """Persona que realiza una reserva en el centro."""

    def __init__(self, nombre: str, email: str, telefono: str,
                 direccion: str = "", documento: str = ""):
        self.__id        = str(uuid.uuid4())[:8].upper()
        self.__nombre    = nombre
        self.__email     = email
        self.__telefono  = telefono
        self.__direccion = direccion
        self.__documento = documento

    # ── Getters ──────────────────────────────
    def get_id(self):        return self.__id
    def get_nombre(self):    return self.__nombre
    def get_email(self):     return self.__email
    def get_telefono(self):  return self.__telefono
    def get_direccion(self): return self.__direccion
    def get_documento(self): return self.__documento

    # ── Métodos UML ───────────────────────────
    def validar_datos(self) -> bool:
        """Valida que los campos obligatorios no estén vacíos."""
        return bool(self.__nombre and self.__email and self.__telefono)

    def to_dict(self) -> dict:
        return {
            "id":        self.__id,
            "nombre":    self.__nombre,
            "email":     self.__email,
            "telefono":  self.__telefono,
            "direccion": self.__direccion,
            "documento": self.__documento,
        }

    def mostrar_info(self) -> str:
        return (f"[{self.__id}] {self.__nombre} | "
                f"Doc: {self.__documento} | "
                f"Email: {self.__email} | Tel: {self.__telefono}")


class ServicioAdicional:
    """Servicio extra ofrecido de forma independiente (catering, audio, etc.)."""

    def __init__(self, nombre: str, costo_unitario: float,
                 tipo_servicio: str, descripcion: str = ""):
        self.__id             = str(uuid.uuid4())[:8].upper()
        self.__nombre         = nombre
        self.__descripcion    = descripcion
        self.__costo_unitario = costo_unitario
        self.__tipo_servicio  = tipo_servicio

    # ── Getters ──────────────────────────────
    def get_id(self):             return self.__id
    def get_nombre(self):         return self.__nombre
    def get_descripcion(self):    return self.__descripcion
    def get_costo_unitario(self): return self.__costo_unitario
    def get_tipo_servicio(self):  return self.__tipo_servicio

    # ── Métodos UML ───────────────────────────
    def calcular_costo(self, cantidad: int) -> float:
        return cantidad * self.__costo_unitario

    def to_dict(self) -> dict:
        return {
            "id":             self.__id,
            "nombre":         self.__nombre,
            "descripcion":    self.__descripcion,
            "costo_unitario": self.__costo_unitario,
            "tipo_servicio":  self.__tipo_servicio,
        }

    def mostrar_info(self) -> str:
        return (f"[{self.__id}] {self.__nombre} | "
                f"Tipo: {self.__tipo_servicio} | "
                f"Costo unit.: S/. {self.__costo_unitario:.2f}")


class Reserva:
    """Reserva de un ambiente por un cliente en fecha y horario específicos."""

    def __init__(self, cliente: Cliente, ambiente: Ambiente,
                 fecha: str, hora_inicio: str, hora_fin: str):
        self.__id                   = str(uuid.uuid4())[:8].upper()
        self.__cliente              = cliente
        self.__ambiente             = ambiente
        self.__fecha                = fecha
        self.__hora_inicio          = hora_inicio
        self.__hora_fin             = hora_fin
        # list[tuple[ServicioAdicional, int]]
        self.__servicios_adicionales: list = []
        self.__estado               = EstadoReserva.PENDIENTE
        self.__costo_total          = 0.0

    # ── Getters ──────────────────────────────
    def get_id(self):          return self.__id
    def get_cliente(self):     return self.__cliente
    def get_ambiente(self):    return self.__ambiente
    def get_fecha(self):       return self.__fecha
    def get_hora_inicio(self): return self.__hora_inicio
    def get_hora_fin(self):    return self.__hora_fin
    def get_estado(self):      return self.__estado
    def get_costo_total(self): return self.__costo_total
    def get_servicios(self):   return self.__servicios_adicionales

    # ── Métodos UML ───────────────────────────
    def agregar_servicio(self, servicio: ServicioAdicional,
                         cantidad: int) -> None:
        self.__servicios_adicionales.append((servicio, cantidad))
        self.__costo_total = self.calcular_costo_total()

    def quitar_servicio(self, servicio_id: str) -> bool:
        original = len(self.__servicios_adicionales)
        self.__servicios_adicionales = [
            (s, c) for s, c in self.__servicios_adicionales
            if s.get_id() != servicio_id
        ]
        if len(self.__servicios_adicionales) < original:
            self.__costo_total = self.calcular_costo_total()
            return True
        return False

    def calcular_costo_total(self) -> float:
        h_ini = int(self.__hora_inicio.replace(":", ""))
        h_fin = int(self.__hora_fin.replace(":", ""))
        horas = (h_fin - h_ini) / 100
        costo_ambiente = self.__ambiente.calcular_costo(horas)
        costo_servicios = sum(
            s.calcular_costo(c) for s, c in self.__servicios_adicionales
        )
        self.__costo_total = round(costo_ambiente + costo_servicios, 2)
        return self.__costo_total

    def validar_horario(self) -> bool:
        """Valida que hora_inicio sea anterior a hora_fin."""
        return self.__hora_inicio < self.__hora_fin

    def cambiar_estado(self, nuevo_estado: str) -> None:
        self.__estado = EstadoReserva(nuevo_estado)

    def to_dict(self) -> dict:
        return {
            "id":          self.__id,
            "cliente_id":  self.__cliente.get_id(),
            "ambiente_id": self.__ambiente.get_id(),
            "fecha":       self.__fecha,
            "hora_inicio": self.__hora_inicio,
            "hora_fin":    self.__hora_fin,
            "estado":      self.__estado.value,
            "costo_total": self.__costo_total,
        }

    def mostrar_info(self) -> str:
        return (f"[{self.__id}] "
                f"Amb: {self.__ambiente.get_id()} | "
                f"Cliente: {self.__cliente.get_id()} | "
                f"Fecha: {self.__fecha} | "
                f"{self.__hora_inicio}-{self.__hora_fin} | "
                f"Estado: {self.__estado.value} | "
                f"Total: S/. {self.__costo_total:.2f}")