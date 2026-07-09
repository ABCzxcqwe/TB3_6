from fastapi import APIRouter, HTTPException

from servicios import EventoService
from backend.schemas import EventoCrear, EventoActualizar

router = APIRouter(prefix="/api/v1/eventos", tags=["Eventos"])
svc = EventoService()


@router.post("", status_code=201)
def crear(datos: EventoCrear):
    resultado = svc.crear(datos.model_dump())
    if resultado is None:
        raise HTTPException(400, "No se pudo crear el evento: verifica que el usuario y espacio existan.")
    return resultado


@router.get("")
def listar(usuario_id: int | None = None, espacio_id: int | None = None, fecha: str | None = None):
    if usuario_id:
        return svc.listar_por_usuario(usuario_id)
    if espacio_id:
        return svc.listar_por_espacio(espacio_id)
    if fecha:
        return svc.listar_por_fecha(fecha)
    return svc.listar_todos()


@router.get("/{evento_id}")
def obtener(evento_id: int):
    item = svc.obtener(evento_id)
    if not item:
        raise HTTPException(404, f"Evento {evento_id} no encontrado.")
    return item


@router.put("/{evento_id}")
def actualizar(evento_id: int, datos: EventoActualizar):
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not cambios:
        raise HTTPException(400, "No se enviaron campos para actualizar.")
    ok = svc.actualizar(evento_id, cambios)
    if not ok:
        raise HTTPException(404, f"Evento {evento_id} no encontrado.")
    return svc.obtener(evento_id)


@router.delete("/{evento_id}", status_code=204)
def eliminar(evento_id: int):
    ok = svc.eliminar(evento_id)
    if not ok:
        raise HTTPException(404, f"Evento {evento_id} no encontrado.")
    return None


@router.get("/{espacio_id}/disponibilidad")
def verificar_disponibilidad(espacio_id: int, fecha: str):
    libre = svc.verificar_disponibilidad(espacio_id, fecha)
    return {"espacio_id": espacio_id, "fecha": fecha, "disponible": libre}
