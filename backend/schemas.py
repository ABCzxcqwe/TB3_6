from pydantic import BaseModel, Field
from typing import Optional


class EspacioCrear(BaseModel):
    nombre: str


class EspacioActualizar(BaseModel):
    nombre: Optional[str] = None


class UsuarioCrear(BaseModel):
    nombre: str
    correo: str = ""
    clave: str = ""


class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    clave: Optional[str] = None


class EventoCrear(BaseModel):
    usuario_id: int
    espacio_id: int
    fecha: str = Field(..., description="YYYY-MM-DD")
    costo: float = 0.0
    descripcion: str = ""


class EventoActualizar(BaseModel):
    usuario_id: Optional[int] = None
    espacio_id: Optional[int] = None
    fecha: Optional[str] = None
    costo: Optional[float] = None
    descripcion: Optional[str] = None


class PreguntaAsistente(BaseModel):
    pregunta: str


class RespuestaAsistente(BaseModel):
    respuesta: str
    contexto_usado: Optional[dict] = None
