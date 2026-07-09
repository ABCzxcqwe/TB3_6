from fastapi import APIRouter, HTTPException

from servicios import AmbienteService
from backend.schemas import AmbienteCrear, AmbienteActualizar

router = APIRouter(prefix="/api/v1/ambientes", tags=["Ambientes"])
amb_svc = AmbienteService()


@router.post("", status_code=201)
def crear_ambiente(datos: AmbienteCrear):
    """CREATE - Registra un nuevo ambiente."""
    ambiente = amb_svc.registrar_ambiente(datos.model_dump())
    if ambiente is None:
        raise HTTPException(400, "No se pudo registrar el ambiente. Revisa los datos enviados.")
    return ambiente.to_dict()


@router.get("")
def listar_ambientes(disponibles: bool = False, tipo: str | None = None,
                      capacidad_minima: int | None = None):
    """READ - Lista todos los ambientes, con filtros opcionales."""
    if capacidad_minima is not None:
        return amb_svc.buscar_por_capacidad_minima(capacidad_minima)
    if tipo:
        return amb_svc.buscar_por_tipo(tipo)
    if disponibles:
        return amb_svc.listar_disponibles()
    return amb_svc.listar_todos()


@router.get("/{ambiente_id}")
def obtener_ambiente(ambiente_id: str):
    """READ - Obtiene un ambiente por su ID (ej. AMB-001)."""
    ambiente = amb_svc.obtener_ambiente(ambiente_id)
    if not ambiente:
        raise HTTPException(404, f"Ambiente {ambiente_id} no encontrado.")
    return ambiente


@router.put("/{ambiente_id}")
def actualizar_ambiente(ambiente_id: str, datos: AmbienteActualizar):
    """UPDATE - Actualiza campos de un ambiente existente."""
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not cambios:
        raise HTTPException(400, "No se enviaron campos para actualizar.")
    ok = amb_svc.actualizar_ambiente(ambiente_id, cambios)
    if not ok:
        raise HTTPException(404, f"Ambiente {ambiente_id} no encontrado.")
    return amb_svc.obtener_ambiente(ambiente_id)


@router.delete("/{ambiente_id}", status_code=204)
def eliminar_ambiente(ambiente_id: str):
    """DELETE - Elimina un ambiente."""
    ok = amb_svc.eliminar_ambiente(ambiente_id)
    if not ok:
        raise HTTPException(404, f"Ambiente {ambiente_id} no encontrado.")
    return None


@router.get("/{ambiente_id}/disponibilidad")
def verificar_disponibilidad(ambiente_id: str, fecha: str,
                              hora_inicio: str, hora_fin: str):
    """Consulta si un ambiente está libre en un tramo horario."""
    libre = amb_svc.verificar_disponibilidad(ambiente_id, fecha, hora_inicio, hora_fin)
    return {"ambiente_id": ambiente_id, "fecha": fecha,
            "hora_inicio": hora_inicio, "hora_fin": hora_fin,
            "disponible": libre}