import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centroeventos.db")


def _get_conn():
    return sqlite3.connect(DB_PATH)


class EspacioRepository:
    def obtener_todos(self) -> list:
        with _get_conn() as conn:
            rows = conn.execute("SELECT id, nombre FROM espacios ORDER BY id").fetchall()
            return [{"id": r[0], "nombre": r[1]} for r in rows]

    def buscar(self, id: int) -> dict | None:
        with _get_conn() as conn:
            row = conn.execute("SELECT id, nombre FROM espacios WHERE id=?", (id,)).fetchone()
            if row:
                return {"id": row[0], "nombre": row[1]}
            return None

    def guardar(self, datos: dict) -> dict:
        with _get_conn() as conn:
            cur = conn.execute("INSERT INTO espacios (nombre) VALUES (?)", (datos["nombre"],))
            nuevo_id = cur.lastrowid
            conn.commit()
            return {"id": nuevo_id, "nombre": datos["nombre"]}

    def actualizar(self, id: int, datos: dict) -> bool:
        campos = ", ".join(f"{k}=?" for k in datos)
        valores = list(datos.values()) + [id]
        with _get_conn() as conn:
            cur = conn.execute(f"UPDATE espacios SET {campos} WHERE id=?", valores)
            conn.commit()
            return cur.rowcount > 0

    def eliminar(self, id: int) -> bool:
        with _get_conn() as conn:
            cur = conn.execute("DELETE FROM espacios WHERE id=?", (id,))
            conn.commit()
            return cur.rowcount > 0


class UsuarioRepository:
    def obtener_todos(self) -> list:
        with _get_conn() as conn:
            rows = conn.execute("SELECT id, nombre, correo, clave FROM usuarios ORDER BY id").fetchall()
            return [{"id": r[0], "nombre": r[1], "correo": r[2], "clave": r[3]} for r in rows]

    def buscar(self, id: int) -> dict | None:
        with _get_conn() as conn:
            row = conn.execute("SELECT id, nombre, correo, clave FROM usuarios WHERE id=?", (id,)).fetchone()
            if row:
                return {"id": row[0], "nombre": row[1], "correo": row[2], "clave": row[3]}
            return None

    def buscar_por_nombre(self, nombre: str) -> dict | None:
        with _get_conn() as conn:
            row = conn.execute("SELECT id, nombre, correo, clave FROM usuarios WHERE nombre LIKE ?",
                               (f"%{nombre}%",)).fetchone()
            if row:
                return {"id": row[0], "nombre": row[1], "correo": row[2], "clave": row[3]}
            return None

    def guardar(self, datos: dict) -> dict:
        with _get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO usuarios (nombre, correo, clave) VALUES (?, ?, ?)",
                (datos["nombre"], datos.get("correo", ""), datos.get("clave", "")))
            nuevo_id = cur.lastrowid
            conn.commit()
            return {"id": nuevo_id, "nombre": datos["nombre"],
                    "correo": datos.get("correo", ""), "clave": datos.get("clave", "")}

    def actualizar(self, id: int, datos: dict) -> bool:
        campos = ", ".join(f"{k}=?" for k in datos)
        valores = list(datos.values()) + [id]
        with _get_conn() as conn:
            cur = conn.execute(f"UPDATE usuarios SET {campos} WHERE id=?", valores)
            conn.commit()
            return cur.rowcount > 0

    def eliminar(self, id: int) -> bool:
        with _get_conn() as conn:
            cur = conn.execute("DELETE FROM usuarios WHERE id=?", (id,))
            conn.commit()
            return cur.rowcount > 0


class EventoRepository:
    def obtener_todos(self) -> list:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT id, usuario_id, espacio_id, fecha, costo, descripcion FROM eventos ORDER BY id"
            ).fetchall()
            return [{"id": r[0], "usuario_id": r[1], "espacio_id": r[2],
                     "fecha": r[3], "costo": r[4], "descripcion": r[5]} for r in rows]

    def buscar(self, id: int) -> dict | None:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT id, usuario_id, espacio_id, fecha, costo, descripcion FROM eventos WHERE id=?",
                (id,)).fetchone()
            if row:
                return {"id": row[0], "usuario_id": row[1], "espacio_id": row[2],
                        "fecha": row[3], "costo": row[4], "descripcion": row[5]}
            return None

    def guardar(self, datos: dict) -> dict:
        with _get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO eventos (usuario_id, espacio_id, fecha, costo, descripcion) VALUES (?, ?, ?, ?, ?)",
                (datos["usuario_id"], datos["espacio_id"], datos["fecha"],
                 datos.get("costo", 0.0), datos.get("descripcion", "")))
            nuevo_id = cur.lastrowid
            conn.commit()
            return {"id": nuevo_id, **{k: datos.get(k) for k in ("usuario_id", "espacio_id", "fecha", "costo", "descripcion")}}

    def actualizar(self, id: int, datos: dict) -> bool:
        campos = ", ".join(f"{k}=?" for k in datos)
        valores = list(datos.values()) + [id]
        with _get_conn() as conn:
            cur = conn.execute(f"UPDATE eventos SET {campos} WHERE id=?", valores)
            conn.commit()
            return cur.rowcount > 0

    def eliminar(self, id: int) -> bool:
        with _get_conn() as conn:
            cur = conn.execute("DELETE FROM eventos WHERE id=?", (id,))
            conn.commit()
            return cur.rowcount > 0

    def filtrar_por_usuario(self, usuario_id: int) -> list:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT id, usuario_id, espacio_id, fecha, costo, descripcion FROM eventos WHERE usuario_id=? ORDER BY id",
                (usuario_id,)).fetchall()
            return [{"id": r[0], "usuario_id": r[1], "espacio_id": r[2],
                     "fecha": r[3], "costo": r[4], "descripcion": r[5]} for r in rows]

    def filtrar_por_espacio(self, espacio_id: int) -> list:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT id, usuario_id, espacio_id, fecha, costo, descripcion FROM eventos WHERE espacio_id=? ORDER BY id",
                (espacio_id,)).fetchall()
            return [{"id": r[0], "usuario_id": r[1], "espacio_id": r[2],
                     "fecha": r[3], "costo": r[4], "descripcion": r[5]} for r in rows]

    def filtrar_por_fecha(self, fecha: str) -> list:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT id, usuario_id, espacio_id, fecha, costo, descripcion FROM eventos WHERE fecha=? ORDER BY id",
                (fecha,)).fetchall()
            return [{"id": r[0], "usuario_id": r[1], "espacio_id": r[2],
                     "fecha": r[3], "costo": r[4], "descripcion": r[5]} for r in rows]

    def filtrar_por_fecha_rango(self, fecha_ini: str, fecha_fin: str) -> list:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT id, usuario_id, espacio_id, fecha, costo, descripcion FROM eventos WHERE fecha BETWEEN ? AND ? ORDER BY id",
                (fecha_ini, fecha_fin)).fetchall()
            return [{"id": r[0], "usuario_id": r[1], "espacio_id": r[2],
                     "fecha": r[3], "costo": r[4], "descripcion": r[5]} for r in rows]

    def verificar_conflictos(self, espacio_id: int, fecha: str) -> bool:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM eventos WHERE espacio_id=? AND fecha=? LIMIT 1",
                (espacio_id, fecha)).fetchone()
            return row is not None
