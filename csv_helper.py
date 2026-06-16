import csv
import os


class CSVHelper:
    """Utilidad para manejo de archivos CSV."""

    @staticmethod
    def leer_csv(ruta: str, campos: list) -> list:
        try:
            if not os.path.exists(ruta):
                return []
            with open(ruta, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                return [dict(row) for row in reader]
        except (IOError, csv.Error) as e:
            print(f"  ✘ Error al leer {ruta}: {e}")
            return []

    @staticmethod
    def escribir_csv(ruta: str, datos: list, campos: list = None) -> None:
        """Agrega filas al CSV; crea cabecera si el archivo es nuevo."""
        try:
            archivo_nuevo = not os.path.exists(ruta)
            fieldnames = campos or (list(datos[0].keys()) if datos else [])
            with open(ruta, "a", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if archivo_nuevo:
                    writer.writeheader()
                writer.writerows(datos)
        except (IOError, csv.Error) as e:
            print(f"  ✘ Error al escribir en {ruta}: {e}")

    @staticmethod
    def actualizar_csv(ruta: str, id: str, datos: dict) -> bool:
        """Actualiza el registro con el id indicado. Retorna True si lo encontró."""
        try:
            todos = CSVHelper.leer_csv(ruta, [])
            encontrado = False
            for i, row in enumerate(todos):
                if row.get("id") == id:
                    todos[i].update(datos)
                    encontrado = True
                    break
            if encontrado:
                CSVHelper._reescribir(ruta, todos)
            return encontrado
        except Exception as e:
            print(f"  ✘ Error al actualizar {ruta}: {e}")
            return False

    @staticmethod
    def eliminar_csv(ruta: str, id: str) -> bool:
        """Elimina el registro con el id indicado. Retorna True si lo encontró."""
        try:
            todos = CSVHelper.leer_csv(ruta, [])
            filtrados = [r for r in todos if r.get("id") != id]
            if len(filtrados) == len(todos):
                return False
            CSVHelper._reescribir(ruta, filtrados)
            return True
        except Exception as e:
            print(f"  ✘ Error al eliminar en {ruta}: {e}")
            return False

    # ── Interno ──────────────────────────────
    @staticmethod
    def _validar_ruta(ruta: str) -> bool:
        return os.path.exists(ruta)

    @staticmethod
    def _reescribir(ruta: str, datos: list) -> None:
        """Sobreescribe el CSV completo (usado internamente)."""
        try:
            if not datos:
                if os.path.exists(ruta):
                    with open(ruta, "r", encoding="utf-8") as f:
                        header = f.readline()
                    with open(ruta, "w", encoding="utf-8") as f:
                        f.write(header)
                return
            campos = list(datos[0].keys())
            with open(ruta, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(datos)
        except (IOError, csv.Error) as e:
            print(f"  ✘ Error al reescribir {ruta}: {e}")
