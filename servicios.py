# ─────────────────────────────────────────────
#  SERVICIOS — Capa de lógica de negocio
#  Adaptado al diagrama UML (Grupo 6)
# ─────────────────────────────────────────────

from modelos import (Ambiente, Cliente, Reserva,
                     ServicioAdicional, EstadoReserva)
from repositorios import (AmbienteRepository, ClienteRepository,
                           ReservaRepository, ServicioRepository)


def _generar_id(lista: list, prefijo: str) -> str:
    """Genera un ID incremental con prefijo. Ej: AMB-001"""
    if not lista:
        return f"{prefijo}-001"
    ids = [int(item["id"].split("-")[1])
           for item in lista if "-" in item.get("id", "")]
    return f"{prefijo}-{(max(ids) + 1):03d}" if ids else f"{prefijo}-001"


# ==================== AMBIENTE SERVICE ====================

class AmbienteService:

    def __init__(self, ambiente_repo: AmbienteRepository = None):
        self.ambiente_repo = ambiente_repo or AmbienteRepository()

    def registrar_ambiente(self, datos: dict) -> Ambiente:
        ambiente = Ambiente(
            nombre          = datos["nombre"],
            tipo            = datos["tipo"],
            capacidad       = int(datos["capacidad"]),
            precio_por_hora = float(datos["precio_por_hora"]),
        )
        # Sobreescribir el id autogenerado con uno incremental
        todos    = self.ambiente_repo.obtener_todos()
        nuevo_id = _generar_id(todos, "AMB")
        d = ambiente.to_dict()
        d["id"] = nuevo_id
        self.ambiente_repo.guardar(d)
        print(f"  ✔ Ambiente registrado: [{nuevo_id}] {d['nombre']}")
        return ambiente

    def obtener_ambiente(self, id: str) -> dict:
        return self.ambiente_repo.buscar(id)

    def actualizar_ambiente(self, id: str, datos: dict) -> bool:
        return self.ambiente_repo.actualizar(id, datos)

    def eliminar_ambiente(self, id: str) -> bool:
        return self.ambiente_repo.eliminar(id)

    def listar_todos(self) -> list:
        return self.ambiente_repo.obtener_todos()

    def listar_disponibles(self) -> list:
        return self.ambiente_repo.obtener_disponibles()

    def buscar_por_tipo(self, tipo: str) -> list:
        return self.ambiente_repo.filtrar_por_tipo(tipo)

    def verificar_disponibilidad(self, id: str, fecha: str,
                                  hora_inicio: str, hora_fin: str) -> bool:
        """Devuelve True si el ambiente está libre en ese horario."""
        from repositorios import ReservaRepository
        repo_res = ReservaRepository()
        return not repo_res.verificar_conflictos(
            id, fecha, hora_inicio, hora_fin)


# ==================== CLIENTE SERVICE ====================

class ClienteService:

    def __init__(self, cliente_repo: ClienteRepository = None):
        self.cliente_repo = cliente_repo or ClienteRepository()

    def registrar_cliente(self, datos: dict) -> Cliente:
        if self.cliente_repo.buscar_por_documento(
                datos.get("documento", "")):
            print(f"  ✘ Ya existe un cliente con documento "
                  f"{datos.get('documento')}.")
            return None

        cliente = Cliente(
            nombre    = datos["nombre"],
            email     = datos["email"],
            telefono  = datos["telefono"],
            direccion = datos.get("direccion", ""),
            documento = datos.get("documento", ""),
        )
        if not cliente.validar_datos():
            print("  ✘ Datos del cliente incompletos.")
            return None

        todos    = self.cliente_repo.obtener_todos()
        nuevo_id = _generar_id(todos, "CLI")
        d = cliente.to_dict()
        d["id"] = nuevo_id
        self.cliente_repo.guardar(d)
        print(f"  ✔ Cliente registrado: [{nuevo_id}] {d['nombre']}")
        return cliente

    def obtener_cliente(self, id: str) -> dict:
        return self.cliente_repo.buscar(id)

    def actualizar_cliente(self, id: str, datos: dict) -> bool:
        return self.cliente_repo.actualizar(id, datos)

    def eliminar_cliente(self, id: str) -> bool:
        return self.cliente_repo.eliminar(id)

    def listar_todos(self) -> list:
        return self.cliente_repo.obtener_todos()

    def buscar_por_email(self, email: str) -> dict:
        return self.cliente_repo.buscar_por_email(email)


# ==================== SERVICIO ADICIONAL SERVICE ====================

class ServicioService:

    def __init__(self, servicio_repo: ServicioRepository = None):
        self.servicio_repo = servicio_repo or ServicioRepository()

    def registrar_servicio(self, datos: dict) -> ServicioAdicional:
        srv = ServicioAdicional(
            nombre         = datos["nombre"],
            costo_unitario = float(datos["costo_unitario"]),
            tipo_servicio  = datos["tipo_servicio"],
            descripcion    = datos.get("descripcion", ""),
        )
        todos    = self.servicio_repo.obtener_todos()
        nuevo_id = _generar_id(todos, "SRV")
        d = srv.to_dict()
        d["id"] = nuevo_id
        self.servicio_repo.guardar(d)
        print(f"  ✔ Servicio registrado: [{nuevo_id}] {d['nombre']}")
        return srv

    def obtener_servicio(self, id: str) -> dict:
        return self.servicio_repo.buscar(id)

    def actualizar_servicio(self, id: str, datos: dict) -> bool:
        return self.servicio_repo.actualizar(id, datos)

    def eliminar_servicio(self, id: str) -> bool:
        return self.servicio_repo.eliminar(id)

    def listar_todos(self) -> list:
        return self.servicio_repo.obtener_todos()

    def listar_por_tipo(self, tipo: str) -> list:
        return self.servicio_repo.filtrar_por_tipo(tipo)

    def calcular_costo_servicio(self, servicio_id: str,
                                 cantidad: int) -> float:
        srv = self.servicio_repo.buscar(servicio_id)
        if not srv:
            return 0.0
        return float(srv["costo_unitario"]) * cantidad


# ==================== RESERVA SERVICE ====================

class ReservaService:

    def __init__(self,
                 reserva_repo:  ReservaRepository  = None,
                 ambiente_repo: AmbienteRepository = None,
                 cliente_repo:  ClienteRepository  = None,
                 servicio_repo: ServicioRepository = None):
        self.reserva_repo  = reserva_repo  or ReservaRepository()
        self.ambiente_repo = ambiente_repo or AmbienteRepository()
        self.cliente_repo  = cliente_repo  or ClienteRepository()
        self.servicio_repo = servicio_repo or ServicioRepository()

    def crear_reserva(self, datos_reserva: dict,
                      servicios: list = None) -> Reserva:
        """
        datos_reserva: {ambiente_id, cliente_id, fecha,
                        hora_inicio, hora_fin}
        servicios:     [{servicio_id, cantidad}, ...]  (opcional)
        """
        amb_dict = self.ambiente_repo.buscar(datos_reserva["ambiente_id"])
        if not amb_dict:
            print(f"  ✘ Ambiente {datos_reserva['ambiente_id']} no existe.")
            return None

        cli_dict = self.cliente_repo.buscar(datos_reserva["cliente_id"])
        if not cli_dict:
            print(f"  ✘ Cliente {datos_reserva['cliente_id']} no existe.")
            return None

        if self.reserva_repo.verificar_conflictos(
                datos_reserva["ambiente_id"],
                datos_reserva["fecha"],
                datos_reserva["hora_inicio"],
                datos_reserva["hora_fin"]):
            print("  ✘ El horario solicitado no está disponible.")
            return None

        # Construir objetos de dominio para la Reserva
        ambiente = Ambiente(amb_dict["nombre"], amb_dict["tipo"],
                            int(amb_dict["capacidad"]),
                            float(amb_dict["precio_por_hora"]))
        cliente  = Cliente(cli_dict["nombre"], cli_dict["email"],
                           cli_dict["telefono"],
                           cli_dict.get("direccion", ""),
                           cli_dict.get("documento", ""))

        reserva = Reserva(cliente, ambiente,
                          datos_reserva["fecha"],
                          datos_reserva["hora_inicio"],
                          datos_reserva["hora_fin"])

        if not reserva.validar_horario():
            print("  ✘ El horario es inválido (inicio >= fin).")
            return None

        # Agregar servicios adicionales si los hay
        filas_srv = []
        if servicios:
            for item in servicios:
                srv_dict = self.servicio_repo.buscar(item["servicio_id"])
                if srv_dict:
                    srv = ServicioAdicional(
                        srv_dict["nombre"],
                        float(srv_dict["costo_unitario"]),
                        srv_dict["tipo_servicio"],
                        srv_dict.get("descripcion", ""),
                    )
                    reserva.agregar_servicio(srv, int(item["cantidad"]))
                    filas_srv.append({
                        "reserva_id":  reserva.get_id(),
                        "servicio_id": srv_dict["id"],
                        "cantidad":    item["cantidad"],
                        "costo":       srv.calcular_costo(
                            int(item["cantidad"])),
                    })

        reserva.calcular_costo_total()
        reserva.cambiar_estado(EstadoReserva.CONFIRMADA.value)

        # Asignar ID incremental
        todos    = self.reserva_repo.obtener_todos()
        nuevo_id = _generar_id(todos, "RES")
        d = reserva.to_dict()
        d["id"] = nuevo_id

        self.reserva_repo.guardar(d, filas_srv)
        print(f"  ✔ Reserva creada: [{nuevo_id}] "
              f"{d['fecha']} {d['hora_inicio']}-{d['hora_fin']}")
        return reserva

    def cancelar_reserva(self, id: str) -> bool:
        reserva = self.reserva_repo.buscar(id)
        if not reserva:
            print(f"  ✘ Reserva {id} no encontrada.")
            return False
        self.reserva_repo.actualizar(
            id, {"estado": EstadoReserva.CANCELADA.value})
        print(f"  ✔ Reserva {id} cancelada.")
        return True

    def confirmar_reserva(self, id: str) -> bool:
        reserva = self.reserva_repo.buscar(id)
        if not reserva:
            print(f"  ✘ Reserva {id} no encontrada.")
            return False
        self.reserva_repo.actualizar(
            id, {"estado": EstadoReserva.CONFIRMADA.value})
        print(f"  ✔ Reserva {id} confirmada.")
        return True

    def agregar_servicio_reserva(self, reserva_id: str,
                                  servicio_id: str,
                                  cantidad: int) -> bool:
        if not self.reserva_repo.buscar(reserva_id):
            print(f"  ✘ Reserva {reserva_id} no encontrada.")
            return False
        srv = self.servicio_repo.buscar(servicio_id)
        if not srv:
            print(f"  ✘ Servicio {servicio_id} no encontrado.")
            return False
        costo = float(srv["costo_unitario"]) * cantidad
        fila = {
            "reserva_id":  reserva_id,
            "servicio_id": servicio_id,
            "cantidad":    cantidad,
            "costo":       costo,
        }
        from csv_helper import CSVHelper
        CSVHelper.escribir_csv(
            ReservaRepository.ARCHIVO_SERVICIOS,
            [fila],
            ReservaRepository.CAMPOS_SERVICIOS,
        )
        print(f"  ✔ Servicio {servicio_id} agregado a reserva {reserva_id}.")
        return True

    def quitar_servicio_reserva(self, reserva_id: str,
                                 servicio_id: str) -> bool:
        from csv_helper import CSVHelper
        todos = CSVHelper.leer_csv(
            ReservaRepository.ARCHIVO_SERVICIOS,
            ReservaRepository.CAMPOS_SERVICIOS)
        filtrados = [s for s in todos
                     if not (s["reserva_id"] == reserva_id
                             and s["servicio_id"] == servicio_id)]
        if len(filtrados) == len(todos):
            return False
        CSVHelper._reescribir(
            ReservaRepository.ARCHIVO_SERVICIOS, filtrados)
        return True

    def obtener_reserva(self, id: str) -> dict:
        return self.reserva_repo.buscar(id)

    def listar_reservas(self) -> list:
        return self.reserva_repo.obtener_todas()

    def listar_reservas_por_fecha(self, fecha: str) -> list:
        return self.reserva_repo.filtrar_por_fecha(fecha)

    def listar_reservas_por_cliente(self, cliente_id: str) -> list:
        return self.reserva_repo.filtrar_por_cliente(cliente_id)

    def verificar_disponibilidad(self, ambiente_id: str, fecha: str,
                                  hora_inicio: str, hora_fin: str) -> bool:
        return not self.reserva_repo.verificar_conflictos(
            ambiente_id, fecha, hora_inicio, hora_fin)


# ==================== REPORTE SERVICE ====================

class ReporteService:

    def __init__(self,
                 reserva_repo:  ReservaRepository  = None,
                 ambiente_repo: AmbienteRepository = None,
                 cliente_repo:  ClienteRepository  = None):
        self.reserva_repo  = reserva_repo  or ReservaRepository()
        self.ambiente_repo = ambiente_repo or AmbienteRepository()
        self.cliente_repo  = cliente_repo  or ClienteRepository()

    def generar_reporte_frecuencia_uso(self, fecha_inicio: str = "",
                                        fecha_fin: str = "") -> dict:
        """Cuántas reservas confirmadas tiene cada ambiente."""
        if fecha_inicio and fecha_fin:
            reservas = self.reserva_repo.filtrar_por_fecha_rango(
                fecha_inicio, fecha_fin)
        else:
            reservas = self.reserva_repo.obtener_todas()

        conteo = {}
        for r in reservas:
            if r["estado"] == "confirmada":
                aid = r["ambiente_id"]
                conteo[aid] = conteo.get(aid, 0) + 1
        return conteo

    def generar_reporte_ingresos(self, fecha_inicio: str = "",
                                  fecha_fin: str = "") -> dict:
        """Ingresos estimados por ambiente (precio/hora × horas)."""
        if fecha_inicio and fecha_fin:
            reservas = self.reserva_repo.filtrar_por_fecha_rango(
                fecha_inicio, fecha_fin)
        else:
            reservas = self.reserva_repo.obtener_todas()

        amb_dict = {a["id"]: a for a in self.ambiente_repo.obtener_todos()}
        ingresos = {}
        for r in reservas:
            if r["estado"] != "confirmada":
                continue
            aid = r["ambiente_id"]
            if aid in amb_dict:
                h_ini = int(r["hora_inicio"].replace(":", ""))
                h_fin = int(r["hora_fin"].replace(":", ""))
                horas = (h_fin - h_ini) / 100
                precio = float(amb_dict[aid]["precio_por_hora"])
                ingresos[aid] = ingresos.get(aid, 0) + horas * precio

        return {aid: round(val, 2) for aid, val in ingresos.items()}

    def generar_reporte_clientes_frecuentes(self) -> list:
        """Clientes ordenados por número de reservas."""
        reservas = self.reserva_repo.obtener_todas()
        clientes = {c["id"]: c for c in self.cliente_repo.obtener_todos()}
        conteo = {}
        for r in reservas:
            cid = r["cliente_id"]
            conteo[cid] = conteo.get(cid, 0) + 1

        resultado = []
        for cid, total in conteo.items():
            info = clientes.get(cid, {})
            resultado.append({
                "cliente_id": cid,
                "nombre":     info.get("nombre", "Desconocido"),
                "reservas":   total,
            })
        return sorted(resultado, key=lambda x: x["reservas"], reverse=True)

    def generar_reporte_servicios_mas_solicitados(
            self, fecha_inicio: str = "", fecha_fin: str = "") -> list:
        from csv_helper import CSVHelper
        from repositorios import ReservaRepository as RR
        todos = CSVHelper.leer_csv(
            RR.ARCHIVO_SERVICIOS, RR.CAMPOS_SERVICIOS)
        conteo: dict = {}
        for s in todos:
            sid = s["servicio_id"]
            conteo[sid] = conteo.get(sid, 0) + int(s.get("cantidad", 1))
        resultado = [{"servicio_id": k, "total": v}
                     for k, v in conteo.items()]
        return sorted(resultado, key=lambda x: x["total"], reverse=True)

    def exportar_reporte_csv(self, reporte: dict,
                              nombre_reporte: str) -> None:
        from csv_helper import CSVHelper
        filas = [{"clave": k, "valor": v} for k, v in reporte.items()]
        CSVHelper.escribir_csv(nombre_reporte, filas)
        print(f"  ✔ Reporte exportado a {nombre_reporte}")

    def calcular_tasa_ocupacion(self, ambiente_id: str,
                                 fecha_inicio: str,
                                 fecha_fin: str) -> float:
        """Porcentaje de días en el rango que tienen al menos una reserva."""
        reservas = self.reserva_repo.filtrar_por_fecha_rango(
            fecha_inicio, fecha_fin)
        dias_reservados = {r["fecha"] for r in reservas
                           if r["ambiente_id"] == ambiente_id
                           and r["estado"] == "confirmada"}
        from datetime import datetime, timedelta
        fmt = "%Y-%m-%d"
        delta = (datetime.strptime(fecha_fin, fmt)
                 - datetime.strptime(fecha_inicio, fmt)).days + 1
        return round(len(dias_reservados) / delta * 100, 2) if delta else 0.0

    def obtener_ambiente_mas_reservado(self, fecha_inicio: str,
                                        fecha_fin: str) -> dict:
        frecuencia = self.generar_reporte_frecuencia_uso(
            fecha_inicio, fecha_fin)
        if not frecuencia:
            return {}
        mejor_id = max(frecuencia, key=frecuencia.get)
        amb = self.ambiente_repo.buscar(mejor_id)
        if amb:
            amb["reservas"] = frecuencia[mejor_id]
        return amb or {}

    def obtener_horario_pico(self) -> dict:
        """Hora de inicio con más reservas confirmadas."""
        reservas = self.reserva_repo.obtener_todas()
        conteo = {}
        for r in reservas:
            if r["estado"] == "confirmada":
                hora = r["hora_inicio"]
                conteo[hora] = conteo.get(hora, 0) + 1
        return dict(sorted(conteo.items(),
                            key=lambda x: x[1], reverse=True))
