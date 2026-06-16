# ─────────────────────────────────────────────
#  MAIN — Menú principal del programa
#  Centro de Eventos y Reservas — Caso 6
#  Adaptado al diagrama UML (Grupo 6)
# ─────────────────────────────────────────────

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from repositorios import (AmbienteRepository, ClienteRepository,
                           ReservaRepository, ServicioRepository)
from servicios import (AmbienteService, ClienteService,
                       ReservaService, ServicioService, ReporteService)
from modelos import TipoAmbiente, TipoServicio, EstadoReserva

# ── Inyección de dependencias (según UML) ─────
_amb_repo = AmbienteRepository()
_cli_repo = ClienteRepository()
_res_repo = ReservaRepository()
_srv_repo = ServicioRepository()

amb_svc = AmbienteService(ambiente_repo=_amb_repo)
cli_svc = ClienteService(cliente_repo=_cli_repo)
srv_svc = ServicioService(servicio_repo=_srv_repo)
res_svc = ReservaService(reserva_repo=_res_repo,
                          ambiente_repo=_amb_repo,
                          cliente_repo=_cli_repo,
                          servicio_repo=_srv_repo)
rep_svc = ReporteService(reserva_repo=_res_repo,
                          ambiente_repo=_amb_repo,
                          cliente_repo=_cli_repo)


def limpiar(): os.system("cls" if os.name == "nt" else "clear")
def pausar():  input("\n  Presiona Enter para continuar...")

def separador(titulo=""):
    print("\n" + "═" * 55)
    if titulo:
        print(f"  {titulo}")
        print("═" * 55)


# ══════════════════════════════════════════════
#  MÓDULO 1 — AMBIENTES
# ══════════════════════════════════════════════

def menu_ambientes():
    while True:
        separador("GESTIÓN DE AMBIENTES")
        print("  1. Registrar nuevo ambiente")
        print("  2. Listar todos los ambientes")
        print("  3. Listar ambientes disponibles")
        print("  4. Filtrar por tipo")
        print("  5. Buscar por capacidad mínima")
        print("  6. Actualizar ambiente")
        print("  7. Eliminar ambiente")
        print("  0. Volver")
        op = input("\n  Opción: ").strip()

        if op == "1":
            separador("REGISTRAR AMBIENTE")
            tipos = [t.value for t in TipoAmbiente]
            print(f"  Tipos válidos: {tipos}")
            datos = {
                "nombre":          input("  Nombre del ambiente: ").strip(),
                "tipo":            input("  Tipo: ").strip(),
                "capacidad":       input("  Capacidad (personas): ").strip(),
                "precio_por_hora": input("  Precio por hora (S/.): ").strip(),
            }
            amb_svc.registrar_ambiente(datos)
            pausar()

        elif op == "2":
            separador("TODOS LOS AMBIENTES")
            ambientes = amb_svc.listar_todos()
            if not ambientes:
                print("  No hay ambientes registrados.")
            for a in ambientes:
                disp = ("✔ Disponible"
                        if str(a["esta_disponible"]).lower()
                        in ("true", "1") else "✘ No disponible")
                print(f"  [{a['id']}] {a['nombre']} | {a['tipo']} | "
                      f"Cap: {a['capacidad']} | "
                      f"S/.{a['precio_por_hora']}/h | {disp}")
            pausar()

        elif op == "3":
            separador("AMBIENTES DISPONIBLES")
            ambientes = amb_svc.listar_disponibles()
            if not ambientes:
                print("  No hay ambientes disponibles.")
            for a in ambientes:
                print(f"  [{a['id']}] {a['nombre']} | "
                      f"{a['tipo']} | Cap: {a['capacidad']}")
            pausar()

        elif op == "4":
            tipo = input("  Tipo a filtrar: ").strip()
            resultados = amb_svc.buscar_por_tipo(tipo)
            separador(f"AMBIENTES TIPO: {tipo.upper()}")
            if not resultados:
                print("  No se encontraron ambientes de ese tipo.")
            for a in resultados:
                print(f"  [{a['id']}] {a['nombre']} | Cap: {a['capacidad']}")
            pausar()

        elif op == "5":
            minima = int(input("  Capacidad mínima: "))
            resultados = [a for a in amb_svc.listar_todos()
                          if int(a["capacidad"]) >= minima]
            separador(f"AMBIENTES CON CAPACIDAD >= {minima}")
            for a in resultados:
                print(f"  [{a['id']}] {a['nombre']} | Cap: {a['capacidad']}")
            pausar()

        elif op == "6":
            amb_id = input("  ID del ambiente a actualizar: ").strip()
            print("  Ingresa los campos a modificar (Enter para omitir):")
            datos = {}
            for campo in ["nombre", "tipo", "capacidad",
                          "precio_por_hora", "esta_disponible"]:
                val = input(f"    {campo}: ").strip()
                if val:
                    datos[campo] = val
            if amb_svc.actualizar_ambiente(amb_id, datos):
                print(f"  ✔ Ambiente {amb_id} actualizado.")
            else:
                print(f"  ✘ No se encontró el ambiente {amb_id}.")
            pausar()

        elif op == "7":
            amb_id = input("  ID del ambiente a eliminar: ").strip()
            if amb_svc.eliminar_ambiente(amb_id):
                print(f"  ✔ Ambiente {amb_id} eliminado.")
            else:
                print(f"  ✘ No se pudo eliminar el ambiente {amb_id}.")
            pausar()

        elif op == "0":
            break


# ══════════════════════════════════════════════
#  MÓDULO 2 — CLIENTES
# ══════════════════════════════════════════════

def menu_clientes():
    while True:
        separador("GESTIÓN DE CLIENTES")
        print("  1. Registrar nuevo cliente")
        print("  2. Listar todos los clientes")
        print("  3. Buscar por documento")
        print("  4. Buscar por email")
        print("  5. Actualizar cliente")
        print("  6. Eliminar cliente")
        print("  0. Volver")
        op = input("\n  Opción: ").strip()

        if op == "1":
            separador("REGISTRAR CLIENTE")
            datos = {
                "nombre":    input("  Nombre completo: ").strip(),
                "email":     input("  Email: ").strip(),
                "telefono":  input("  Teléfono: ").strip(),
                "direccion": input("  Dirección: ").strip(),
                "documento": input("  N° Documento (DNI/RUC): ").strip(),
            }
            cli_svc.registrar_cliente(datos)
            pausar()

        elif op == "2":
            separador("TODOS LOS CLIENTES")
            clientes = cli_svc.listar_todos()
            if not clientes:
                print("  No hay clientes registrados.")
            for c in clientes:
                print(f"  [{c['id']}] {c['nombre']} | "
                      f"Doc: {c['documento']} | Tel: {c['telefono']}")
            pausar()

        elif op == "3":
            doc = input("  Número de documento: ").strip()
            c   = cli_svc.obtener_cliente.__func__  # usar repo directamente
            c   = _cli_repo.buscar_por_documento(doc)
            separador("RESULTADO DE BÚSQUEDA")
            if c:
                print(f"  [{c['id']}] {c['nombre']} | "
                      f"Email: {c['email']} | Tel: {c['telefono']}")
            else:
                print("  No se encontró cliente con ese documento.")
            pausar()

        elif op == "4":
            email = input("  Email: ").strip()
            c     = cli_svc.buscar_por_email(email)
            separador("RESULTADO DE BÚSQUEDA")
            if c:
                print(f"  [{c['id']}] {c['nombre']} | "
                      f"Tel: {c['telefono']}")
            else:
                print("  No se encontró cliente con ese email.")
            pausar()

        elif op == "5":
            cli_id = input("  ID del cliente a actualizar: ").strip()
            datos  = {}
            for campo in ["nombre", "email", "telefono",
                          "direccion", "documento"]:
                val = input(f"    {campo}: ").strip()
                if val:
                    datos[campo] = val
            if cli_svc.actualizar_cliente(cli_id, datos):
                print(f"  ✔ Cliente {cli_id} actualizado.")
            else:
                print(f"  ✘ No se encontró el cliente {cli_id}.")
            pausar()

        elif op == "6":
            cli_id = input("  ID del cliente a eliminar: ").strip()
            if cli_svc.eliminar_cliente(cli_id):
                print(f"  ✔ Cliente {cli_id} eliminado.")
            else:
                print(f"  ✘ No se pudo eliminar el cliente {cli_id}.")
            pausar()

        elif op == "0":
            break


# ══════════════════════════════════════════════
#  MÓDULO 3 — CATÁLOGO DE SERVICIOS ADICIONALES
# ══════════════════════════════════════════════

def menu_catalogo_servicios():
    while True:
        separador("CATÁLOGO DE SERVICIOS ADICIONALES")
        print("  1. Registrar nuevo servicio")
        print("  2. Listar todos los servicios")
        print("  3. Filtrar por tipo")
        print("  4. Calcular costo de servicio")
        print("  5. Actualizar servicio")
        print("  6. Eliminar servicio")
        print("  0. Volver")
        op = input("\n  Opción: ").strip()

        if op == "1":
            separador("REGISTRAR SERVICIO")
            tipos = [t.value for t in TipoServicio]
            print(f"  Tipos válidos: {tipos}")
            datos = {
                "nombre":         input("  Nombre del servicio: ").strip(),
                "descripcion":    input("  Descripción: ").strip(),
                "costo_unitario": input("  Costo unitario (S/.): ").strip(),
                "tipo_servicio":  input("  Tipo: ").strip(),
            }
            srv_svc.registrar_servicio(datos)
            pausar()

        elif op == "2":
            separador("TODOS LOS SERVICIOS")
            servicios = srv_svc.listar_todos()
            if not servicios:
                print("  No hay servicios registrados.")
            for s in servicios:
                print(f"  [{s['id']}] {s['nombre']} | "
                      f"Tipo: {s['tipo_servicio']} | "
                      f"S/. {s['costo_unitario']}/u")
            pausar()

        elif op == "3":
            tipo = input("  Tipo a filtrar: ").strip()
            resultados = srv_svc.listar_por_tipo(tipo)
            separador(f"SERVICIOS TIPO: {tipo.upper()}")
            for s in resultados:
                print(f"  [{s['id']}] {s['nombre']} | S/. {s['costo_unitario']}")
            pausar()

        elif op == "4":
            srv_id   = input("  ID del servicio: ").strip()
            cantidad = int(input("  Cantidad: "))
            costo    = srv_svc.calcular_costo_servicio(srv_id, cantidad)
            print(f"\n  Costo total: S/. {costo:.2f}")
            pausar()

        elif op == "5":
            srv_id = input("  ID del servicio a actualizar: ").strip()
            datos  = {}
            for campo in ["nombre", "descripcion",
                          "costo_unitario", "tipo_servicio"]:
                val = input(f"    {campo}: ").strip()
                if val:
                    datos[campo] = val
            if srv_svc.actualizar_servicio(srv_id, datos):
                print(f"  ✔ Servicio {srv_id} actualizado.")
            else:
                print(f"  ✘ No se encontró el servicio {srv_id}.")
            pausar()

        elif op == "6":
            srv_id = input("  ID del servicio a eliminar: ").strip()
            if srv_svc.eliminar_servicio(srv_id):
                print(f"  ✔ Servicio {srv_id} eliminado.")
            else:
                print(f"  ✘ No se pudo eliminar el servicio {srv_id}.")
            pausar()

        elif op == "0":
            break


# ══════════════════════════════════════════════
#  MÓDULO 4 — RESERVAS
# ══════════════════════════════════════════════

def menu_reservas():
    while True:
        separador("GESTIÓN DE RESERVAS")
        print("  1. Crear nueva reserva")
        print("  2. Verificar disponibilidad de ambiente")
        print("  3. Listar todas las reservas")
        print("  4. Listar reservas por fecha")
        print("  5. Listar reservas por ambiente")
        print("  6. Listar reservas por cliente")
        print("  7. Confirmar reserva")
        print("  8. Cancelar reserva")
        print("  9. Agregar servicio a reserva existente")
        print("  0. Volver")
        op = input("\n  Opción: ").strip()

        if op == "1":
            separador("CREAR RESERVA")
            datos_reserva = {
                "ambiente_id": input("  ID del ambiente (ej. AMB-001): ").strip(),
                "cliente_id":  input("  ID del cliente (ej. CLI-001): ").strip(),
                "fecha":       input("  Fecha (YYYY-MM-DD): ").strip(),
                "hora_inicio": input("  Hora inicio (HH:MM): ").strip(),
                "hora_fin":    input("  Hora fin   (HH:MM): ").strip(),
            }
            agregar_srvs = input("  ¿Agregar servicios? (s/n): ").strip().lower()
            servicios = []
            while agregar_srvs == "s":
                sid = input("    ID del servicio: ").strip()
                qty = int(input("    Cantidad: "))
                servicios.append({"servicio_id": sid, "cantidad": qty})
                agregar_srvs = input("  ¿Agregar otro servicio? (s/n): ").strip().lower()
            res_svc.crear_reserva(datos_reserva, servicios or None)
            pausar()

        elif op == "2":
            separador("VERIFICAR DISPONIBILIDAD")
            amb_id = input("  ID del ambiente: ").strip()
            fecha  = input("  Fecha (YYYY-MM-DD): ").strip()
            h_ini  = input("  Hora inicio (HH:MM): ").strip()
            h_fin  = input("  Hora fin   (HH:MM): ").strip()
            libre  = res_svc.verificar_disponibilidad(amb_id, fecha, h_ini, h_fin)
            if libre:
                print(f"\n  ✔ El ambiente {amb_id} está DISPONIBLE "
                      f"el {fecha} de {h_ini} a {h_fin}.")
            else:
                print(f"\n  ✘ El ambiente {amb_id} NO está disponible "
                      f"en ese horario.")
            pausar()

        elif op == "3":
            separador("TODAS LAS RESERVAS")
            reservas = res_svc.listar_reservas()
            if not reservas:
                print("  No hay reservas registradas.")
            for r in reservas:
                print(f"  [{r['id']}] Amb: {r['ambiente_id']} | "
                      f"Cli: {r['cliente_id']} | {r['fecha']} | "
                      f"{r['hora_inicio']}-{r['hora_fin']} | "
                      f"Estado: {r['estado']} | "
                      f"S/. {r.get('costo_total', '?')}")
            pausar()

        elif op == "4":
            fecha = input("  Fecha (YYYY-MM-DD): ").strip()
            reservas = res_svc.listar_reservas_por_fecha(fecha)
            separador(f"RESERVAS DEL {fecha}")
            if not reservas:
                print("  No hay reservas para esa fecha.")
            for r in reservas:
                print(f"  [{r['id']}] Amb: {r['ambiente_id']} | "
                      f"Cli: {r['cliente_id']} | "
                      f"{r['hora_inicio']}-{r['hora_fin']} | {r['estado']}")
            pausar()

        elif op == "5":
            amb_id = input("  ID del ambiente: ").strip()
            reservas = res_svc.listar_reservas_por_fecha.__doc__  # solo para evitar lint
            reservas = _res_repo.filtrar_por_ambiente(amb_id)
            separador(f"RESERVAS DE AMBIENTE {amb_id}")
            if not reservas:
                print("  No hay reservas confirmadas para ese ambiente.")
            for r in reservas:
                print(f"  [{r['id']}] {r['fecha']} | "
                      f"{r['hora_inicio']}-{r['hora_fin']} | {r['estado']}")
            pausar()

        elif op == "6":
            cli_id   = input("  ID del cliente: ").strip()
            reservas = res_svc.listar_reservas_por_cliente(cli_id)
            separador(f"RESERVAS DEL CLIENTE {cli_id}")
            if not reservas:
                print("  No hay reservas para ese cliente.")
            for r in reservas:
                print(f"  [{r['id']}] Amb: {r['ambiente_id']} | "
                      f"{r['fecha']} | {r['estado']}")
            pausar()

        elif op == "7":
            res_id = input("  ID de la reserva a confirmar: ").strip()
            res_svc.confirmar_reserva(res_id)
            pausar()

        elif op == "8":
            res_id = input("  ID de la reserva a cancelar: ").strip()
            res_svc.cancelar_reserva(res_id)
            pausar()

        elif op == "9":
            separador("AGREGAR SERVICIO A RESERVA")
            res_id = input("  ID de la reserva: ").strip()
            srv_id = input("  ID del servicio del catálogo: ").strip()
            qty    = int(input("  Cantidad: "))
            res_svc.agregar_servicio_reserva(res_id, srv_id, qty)
            pausar()

        elif op == "0":
            break


# ══════════════════════════════════════════════
#  MÓDULO 5 — REPORTES
# ══════════════════════════════════════════════

def menu_reportes():
    while True:
        separador("REPORTES")
        print("  1. Frecuencia de uso por ambiente")
        print("  2. Ambiente más reservado en un rango")
        print("  3. Servicios adicionales más solicitados")
        print("  4. Ingresos estimados por ambiente")
        print("  5. Clientes frecuentes")
        print("  6. Tasa de ocupación de un ambiente")
        print("  7. Horario pico")
        print("  0. Volver")
        op = input("\n  Opción: ").strip()

        if op == "1":
            separador("FRECUENCIA DE USO POR AMBIENTE")
            usar_rango = input("  ¿Filtrar por rango de fechas? (s/n): ").strip().lower()
            if usar_rango == "s":
                f_ini = input("  Fecha inicio (YYYY-MM-DD): ").strip()
                f_fin = input("  Fecha fin    (YYYY-MM-DD): ").strip()
                conteo = rep_svc.generar_reporte_frecuencia_uso(f_ini, f_fin)
            else:
                conteo = rep_svc.generar_reporte_frecuencia_uso()
            if not conteo:
                print("  No hay reservas confirmadas.")
            for amb_id, veces in sorted(conteo.items(),
                                         key=lambda x: x[1], reverse=True):
                amb    = amb_svc.obtener_ambiente(amb_id)
                nombre = amb["nombre"] if amb else amb_id
                print(f"  {nombre} ({amb_id}): {veces} reserva(s)")
            pausar()

        elif op == "2":
            separador("AMBIENTE MÁS RESERVADO")
            f_ini = input("  Fecha inicio (YYYY-MM-DD): ").strip()
            f_fin = input("  Fecha fin    (YYYY-MM-DD): ").strip()
            amb   = rep_svc.obtener_ambiente_mas_reservado(f_ini, f_fin)
            if amb:
                print(f"  [{amb.get('id')}] {amb.get('nombre')} — "
                      f"{amb.get('reservas')} reserva(s)")
            else:
                print("  Sin datos para ese rango.")
            pausar()

        elif op == "3":
            separador("SERVICIOS MÁS SOLICITADOS")
            servicios = rep_svc.generar_reporte_servicios_mas_solicitados()
            if not servicios:
                print("  No hay datos de servicios.")
            for item in servicios:
                print(f"  Servicio {item['servicio_id']}: "
                      f"{item['total']} unidad(es)")
            pausar()

        elif op == "4":
            separador("INGRESOS ESTIMADOS POR AMBIENTE")
            usar_rango = input("  ¿Filtrar por rango de fechas? (s/n): ").strip().lower()
            if usar_rango == "s":
                f_ini = input("  Fecha inicio (YYYY-MM-DD): ").strip()
                f_fin = input("  Fecha fin    (YYYY-MM-DD): ").strip()
                ingresos = rep_svc.generar_reporte_ingresos(f_ini, f_fin)
            else:
                ingresos = rep_svc.generar_reporte_ingresos()
            if not ingresos:
                print("  No hay datos suficientes.")
            for amb_id, total in sorted(ingresos.items(),
                                         key=lambda x: x[1], reverse=True):
                amb    = amb_svc.obtener_ambiente(amb_id)
                nombre = amb["nombre"] if amb else amb_id
                print(f"  {nombre}: S/. {total:.2f}")
            pausar()

        elif op == "5":
            separador("CLIENTES FRECUENTES")
            clientes = rep_svc.generar_reporte_clientes_frecuentes()
            for i, c in enumerate(clientes, 1):
                print(f"  {i}. {c['nombre']} ({c['cliente_id']}): "
                      f"{c['reservas']} reserva(s)")
            pausar()

        elif op == "6":
            separador("TASA DE OCUPACIÓN")
            amb_id = input("  ID del ambiente: ").strip()
            f_ini  = input("  Fecha inicio (YYYY-MM-DD): ").strip()
            f_fin  = input("  Fecha fin    (YYYY-MM-DD): ").strip()
            tasa   = rep_svc.calcular_tasa_ocupacion(amb_id, f_ini, f_fin)
            print(f"  Tasa de ocupación: {tasa}%")
            pausar()

        elif op == "7":
            separador("HORARIO PICO")
            horarios = rep_svc.obtener_horario_pico()
            if not horarios:
                print("  Sin datos de reservas.")
            for hora, total in horarios.items():
                print(f"  {hora} — {total} reserva(s)")
            pausar()

        elif op == "0":
            break


# ══════════════════════════════════════════════
#  MENÚ PRINCIPAL
# ══════════════════════════════════════════════

def main():
    while True:
        limpiar()
        separador()
        print("  SISTEMA DE GESTIÓN — CENTRO DE EVENTOS")
        print("  1ACC0271 | Grupo 6")
        separador()
        print("  1. Gestión de Ambientes")
        print("  2. Gestión de Clientes")
        print("  3. Catálogo de Servicios Adicionales")
        print("  4. Gestión de Reservas")
        print("  5. Reportes")
        print("  0. Salir")
        separador()
        op = input("  Opción: ").strip()

        if   op == "1": menu_ambientes()
        elif op == "2": menu_clientes()
        elif op == "3": menu_catalogo_servicios()
        elif op == "4": menu_reservas()
        elif op == "5": menu_reportes()
        elif op == "0":
            print("\n  Hasta luego.\n")
            break
        else:
            print("  Opción inválida.")
            pausar()


if __name__ == "__main__":
    main()
