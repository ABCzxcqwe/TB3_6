from pydantic import BaseModel, Field
from typing import Optional, List


# ==================== AMBIENTES ====================

class AmbienteCrear(BaseModel):
    nombre: str
    tipo: str = Field(..., description="salon, auditorio, terraza, sala_de_reuniones, jardin")
    capacidad: int
    precio_por_hora: float


class AmbienteActualizar(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    capacidad: Optional[int] = None
    precio_por_hora: Optional[float] = None
    esta_disponible: Optional[bool] = None


# ==================== RESERVAS ====================

class ServicioEnReserva(BaseModel):
    servicio_id: str
    cantidad: int


class ReservaCrear(BaseModel):
    ambiente_id: str
    cliente_id: str
    fecha: str = Field(..., description="YYYY-MM-DD")
    hora_inicio: str = Field(..., description="HH:MM")
    hora_fin: str = Field(..., description="HH:MM")
    servicios: Optional[List[ServicioEnReserva]] = None


class DisponibilidadConsulta(BaseModel):
    fecha: str
    hora_inicio: str
    hora_fin: str


# ==================== ASISTENTE IA ====================

class PreguntaAsistente(BaseModel):
    pregunta: str


class RespuestaAsistente(BaseModel):
    respuesta: str
    contexto_usado: Optional[dict] = None