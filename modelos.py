class Espacio:
    def __init__(self, nombre: str):
        self.id = None
        self.nombre = nombre

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre}


class Usuario:
    def __init__(self, nombre: str, correo: str, clave: str):
        self.id = None
        self.nombre = nombre
        self.correo = correo
        self.clave = clave

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre,
                "correo": self.correo, "clave": self.clave}


class Evento:
    def __init__(self, usuario_id: int, espacio_id: int,
                 fecha: str, costo: float = 0.0, descripcion: str = ""):
        self.id = None
        self.usuario_id = usuario_id
        self.espacio_id = espacio_id
        self.fecha = fecha
        self.costo = costo
        self.descripcion = descripcion

    def to_dict(self):
        return {"id": self.id, "usuario_id": self.usuario_id,
                "espacio_id": self.espacio_id, "fecha": self.fecha,
                "costo": self.costo, "descripcion": self.descripcion}
