from modelos import Espacio, Usuario, Evento
from repositorios import EspacioRepository, UsuarioRepository, EventoRepository


class EspacioService:
    def __init__(self, repo: EspacioRepository = None):
        self.repo = repo or EspacioRepository()

    def listar_todos(self) -> list:
        return self.repo.obtener_todos()

    def registrar(self, datos: dict) -> dict | None:
        espacio = Espacio(datos["nombre"])
        result = self.repo.guardar({"nombre": espacio.nombre})
        return result

    def obtener(self, id: int) -> dict | None:
        return self.repo.buscar(id)

    def actualizar(self, id: int, datos: dict) -> bool:
        return self.repo.actualizar(id, datos)

    def eliminar(self, id: int) -> bool:
        return self.repo.eliminar(id)


class UsuarioService:
    def __init__(self, repo: UsuarioRepository = None):
        self.repo = repo or UsuarioRepository()

    def listar_todos(self) -> list:
        return self.repo.obtener_todos()

    def registrar(self, datos: dict) -> dict | None:
        usuario = Usuario(datos["nombre"], datos.get("correo", ""), datos.get("clave", ""))
        result = self.repo.guardar(usuario.to_dict())
        return result

    def obtener(self, id: int) -> dict | None:
        return self.repo.buscar(id)

    def actualizar(self, id: int, datos: dict) -> bool:
        return self.repo.actualizar(id, datos)

    def eliminar(self, id: int) -> bool:
        return self.repo.eliminar(id)

    def buscar_por_nombre(self, nombre: str) -> dict | None:
        return self.repo.buscar_por_nombre(nombre)


class EventoService:
    def __init__(self, repo: EventoRepository = None,
                 espacio_repo: EspacioRepository = None,
                 usuario_repo: UsuarioRepository = None):
        self.repo = repo or EventoRepository()
        self.espacio_repo = espacio_repo or EspacioRepository()
        self.usuario_repo = usuario_repo or UsuarioRepository()

    def listar_todos(self) -> list:
        return self.repo.obtener_todos()

    def crear(self, datos: dict) -> dict | None:
        if not self.espacio_repo.buscar(datos["espacio_id"]):
            return None
        if not self.usuario_repo.buscar(datos["usuario_id"]):
            return None
        evento = Evento(
            usuario_id=datos["usuario_id"],
            espacio_id=datos["espacio_id"],
            fecha=datos["fecha"],
            costo=datos.get("costo", 0.0),
            descripcion=datos.get("descripcion", ""),
        )
        result = self.repo.guardar(evento.to_dict())
        return result

    def obtener(self, id: int) -> dict | None:
        return self.repo.buscar(id)

    def actualizar(self, id: int, datos: dict) -> bool:
        return self.repo.actualizar(id, datos)

    def eliminar(self, id: int) -> bool:
        return self.repo.eliminar(id)

    def listar_por_usuario(self, usuario_id: int) -> list:
        return self.repo.filtrar_por_usuario(usuario_id)

    def listar_por_espacio(self, espacio_id: int) -> list:
        return self.repo.filtrar_por_espacio(espacio_id)

    def listar_por_fecha(self, fecha: str) -> list:
        return self.repo.filtrar_por_fecha(fecha)

    def verificar_disponibilidad(self, espacio_id: int, fecha: str) -> bool:
        return not self.repo.verificar_conflictos(espacio_id, fecha)


class ReporteService:
    def __init__(self, evento_repo: EventoRepository = None,
                 espacio_repo: EspacioRepository = None,
                 usuario_repo: UsuarioRepository = None):
        self.evento_repo = evento_repo or EventoRepository()
        self.espacio_repo = espacio_repo or EspacioRepository()
        self.usuario_repo = usuario_repo or UsuarioRepository()

    def espacio_mas_utilizado(self, fecha_inicio: str, fecha_fin: str) -> dict | None:
        eventos = self.evento_repo.filtrar_por_fecha_rango(fecha_inicio, fecha_fin)
        if not eventos:
            return None
        conteo = {}
        for e in eventos:
            eid = e["espacio_id"]
            conteo[eid] = conteo.get(eid, 0) + 1
        mejor_id = max(conteo, key=conteo.get)
        espacio = self.espacio_repo.buscar(mejor_id)
        if espacio:
            espacio["eventos"] = conteo[mejor_id]
        return espacio

    def clientes_frecuentes(self) -> list:
        eventos = self.evento_repo.obtener_todos()
        usuarios = {u["id"]: u for u in self.usuario_repo.obtener_todos()}
        conteo = {}
        for e in eventos:
            uid = e["usuario_id"]
            conteo[uid] = conteo.get(uid, 0) + 1
        resultado = [{"usuario_id": uid, "nombre": usuarios.get(uid, {}).get("nombre", "Desconocido"),
                       "eventos": total} for uid, total in conteo.items()]
        return sorted(resultado, key=lambda x: x["eventos"], reverse=True)
