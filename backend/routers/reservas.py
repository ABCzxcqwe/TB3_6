from fastapi import APIRouter, HTTPException

from servicios import ReservaService
from backend.schemas import ReservaCrear

router = APIRouter(prefix="/api/v1/reservas", tags=["Reservas"])
res_svc = ReservaService()


@router.post("", status_code=201)
def crear_reserva(datos: ReservaCrear):
    """Crea una reserva (valida disponibilidad y agrega servicios opcionales)."""
    datos_reserva = {
        "ambiente_id": datos.ambiente_id,
        "cliente_id":  datos.cliente_id,
        "fecha":       datos.fecha,
        "hora_inicio": datos.hora_inicio,
        "hora_fin":    datos.hora_fin,
    }
    servicios = ([s.model_dump() for s in datos.servicios]
                 if datos.servicios else None)
    reserva = res_svc.crear_reserva(datos_reserva, servicios)
    if reserva is None:
        raise HTTPException(
            400,
            "No se pudo crear la reserva: revisa que el ambiente/cliente "
            "existan y que el horario esté disponible."
        )
    return reserva.to_dict()


@router.get("")
def listar_reservas(ambiente_id: str | None = None,
                     cliente_id: str | None = None,
                     fecha: str | None = None):
    """Lista reservas, con filtros opcionales."""
    if ambiente_id:
        return res_svc.listar_reservas_por_ambiente(ambiente_id)
    if cliente_id:
        return res_svc.listar_reservas_por_cliente(cliente_id)
    if fecha:
        return res_svc.listar_reservas_por_fecha(fecha)
    return res_svc.listar_reservas()


@router.get("/{reserva_id}")
def obtener_reserva(reserva_id: str):
    reserva = res_svc.obtener_reserva(reserva_id)
    if not reserva:
        raise HTTPException(404, f"Reserva {reserva_id} no encontrada.")
    return reserva


@router.post("/{reserva_id}/confirmar")
def confirmar_reserva(reserva_id: str):
    ok = res_svc.confirmar_reserva(reserva_id)
    if not ok:
        raise HTTPException(404, f"Reserva {reserva_id} no encontrada.")
    return res_svc.obtener_reserva(reserva_id)


@router.post("/{reserva_id}/cancelar")
def cancelar_reserva(reserva_id: str):
    ok = res_svc.cancelar_reserva(reserva_id)
    if not ok:
        raise HTTPException(404, f"Reserva {reserva_id} no encontrada.")
    return res_svc.obtener_reserva(reserva_id)


@router.post("/{reserva_id}/servicios")
def agregar_servicio(reserva_id: str, servicio_id: str, cantidad: int):
    ok = res_svc.agregar_servicio_reserva(reserva_id, servicio_id, cantidad)
    if not ok:
        raise HTTPException(400, "No se pudo agregar el servicio (revisa los IDs).")
    return res_svc.obtener_reserva(reserva_id)