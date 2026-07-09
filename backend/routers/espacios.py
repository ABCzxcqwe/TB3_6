from fastapi import APIRouter, HTTPException

from servicios import EspacioService
from backend.schemas import EspacioCrear, EspacioActualizar

router = APIRouter(prefix="/api/v1/espacios", tags=["Espacios"])
svc = EspacioService()


@router.post("", status_code=201)
def crear(datos: EspacioCrear):
    resultado = svc.registrar(datos.model_dump())
    if resultado is None:
        raise HTTPException(400, "No se pudo registrar el espacio.")
    return resultado


@router.get("")
def listar():
    return svc.listar_todos()


@router.get("/{espacio_id}")
def obtener(espacio_id: int):
    item = svc.obtener(espacio_id)
    if not item:
        raise HTTPException(404, f"Espacio {espacio_id} no encontrado.")
    return item


@router.put("/{espacio_id}")
def actualizar(espacio_id: int, datos: EspacioActualizar):
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not cambios:
        raise HTTPException(400, "No se enviaron campos para actualizar.")
    ok = svc.actualizar(espacio_id, cambios)
    if not ok:
        raise HTTPException(404, f"Espacio {espacio_id} no encontrado.")
    return svc.obtener(espacio_id)


@router.delete("/{espacio_id}", status_code=204)
def eliminar(espacio_id: int):
    ok = svc.eliminar(espacio_id)
    if not ok:
        raise HTTPException(404, f"Espacio {espacio_id} no encontrado.")
    return None
