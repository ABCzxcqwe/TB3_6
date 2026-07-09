from fastapi import APIRouter, HTTPException

from servicios import UsuarioService
from backend.schemas import UsuarioCrear, UsuarioActualizar

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])
svc = UsuarioService()


@router.post("", status_code=201)
def crear(datos: UsuarioCrear):
    resultado = svc.registrar(datos.model_dump())
    if resultado is None:
        raise HTTPException(400, "No se pudo registrar el usuario.")
    return resultado


@router.get("")
def listar():
    return svc.listar_todos()


@router.get("/{usuario_id}")
def obtener(usuario_id: int):
    item = svc.obtener(usuario_id)
    if not item:
        raise HTTPException(404, f"Usuario {usuario_id} no encontrado.")
    return item


@router.put("/{usuario_id}")
def actualizar(usuario_id: int, datos: UsuarioActualizar):
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not cambios:
        raise HTTPException(400, "No se enviaron campos para actualizar.")
    ok = svc.actualizar(usuario_id, cambios)
    if not ok:
        raise HTTPException(404, f"Usuario {usuario_id} no encontrado.")
    return svc.obtener(usuario_id)


@router.delete("/{usuario_id}", status_code=204)
def eliminar(usuario_id: int):
    ok = svc.eliminar(usuario_id)
    if not ok:
        raise HTTPException(404, f"Usuario {usuario_id} no encontrado.")
    return None
