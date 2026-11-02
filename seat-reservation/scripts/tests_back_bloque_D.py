#!/usr/bin/env python3
"""
Pruebas de caja negra - Bloque D (concurrencia)
Proyecto: Seat Reservation (back .NET, microservicios)

Solo usa la librería estándar de Python 3.8+ (no hace falta pip install). Necesita tests_back_comun.py
en la misma carpeta.

Uso (desde la carpeta seat-reservation):
    python scripts/tests_back_bloque_D.py

Cómo se hace la simultaneidad: todos los POST salen en hilos distintos y arrancan juntos (threading.Barrier);
los tokens se piden antes para que no demoren el disparo. RabbitMQ reparte los mensajes entre las dos
réplicas de Booking (consumidores competidores).

Limitación: Keycloak solo tiene usuario1 y usuario2, así que "distintos usuarios" se resuelve alternando
entre los dos (para la reserva de un asiento el usuario no cambia nada; lo que compite es el asiento).

"""

import time

from tests_back_comun import *

RUN = datetime.now().strftime("%H%M%S")


def esperar_todas(intentos, timeout=40):
    """Espera el estado final de cada intento. Completa intento['final'] con el dict final (o None)."""
    for it in intentos:
        if it.get("rid"):
            it["final"] = esperar_final(it["user"], it["rid"], timeout)
        else:
            it["final"] = None


def verificar_carrera(test_id, seat, intentos, esperadas_rechazadas=None):
    """Chequeos comunes de las pruebas 18, 19 y 21 sobre UN asiento disputado."""
    n = len(intentos)
    codigos = [it["status"] for it in intentos]
    record(test_id, f"{n} POST sin errores 5xx", "todos 202", f"{sorted(set(codigos))}",
           all(c == 202 for c in codigos), [it["resp"] for it in intentos if it["status"] != 202][:2])

    esperar_todas(intentos)
    conf = [it for it in intentos if estado_de(it["final"]) == "Confirmada"]
    rech = [it for it in intentos if estado_de(it["final"]) == "Rechazada"]
    otros = [it for it in intentos if estado_de(it["final"]) not in ("Confirmada", "Rechazada")]
    record(test_id, "Exactamente una Confirmada", "1", len(conf), len(conf) == 1)
    esperado_rech = (n - 1) if esperadas_rechazadas is None else esperadas_rechazadas
    record(test_id, "Las demás Rechazadas", esperado_rech, len(rech), len(rech) == esperado_rech and not otros,
           [estado_de(it["final"]) for it in otros])
    motivos = sorted(set(str(motivo_de(it["final"])) for it in rech))
    record(test_id, "Motivo de todas las rechazadas", "AsientoOcupado", motivos if motivos else "-",
           bool(rech) and motivos == ["AsientoOcupado"])

    filas = booking_filas_asiento(seat)
    if filas is None:
        revisar(test_id, "Booking: una sola reserva activa por asiento",
                "no se pudo consultar Booking directo (puertos 5002/5003, token de availability-service)")
    else:
        record(test_id, "Booking: una sola reserva activa por asiento", "1 activa",
               f"{len(activas(filas))} activas de {len(filas)} filas", len(activas(filas)) == 1)
        record(test_id, "Booking: una fila por solicitud (sin duplicados)", f"{n} filas", len(filas), len(filas) == n)

    ids_res = [reservation_id_de(it["rid"]) for it in intentos if it.get("rid")]
    cobros = contar_cobros(ids_res)
    if cobros is None:
        revisar(test_id, "Payment: un solo cobro", "sin Docker no se puede consultar la base payment")
    else:
        record(test_id, "Payment: un solo cobro", "1", cobros, cobros == 1)
    notifs = contar_notificaciones(seat, ids_res)
    if notifs is None:
        revisar(test_id, "Notifications: una sola notificación", "no se pudo leer Notifications")
    else:
        record(test_id, "Notifications: una sola notificación", "1", notifs, notifs == 1)
    oc = asiento_ocupado(seat)
    record(test_id, "El asiento figura ocupado", "occupied=true", oc, oc is True)


def lanzar(users, seat, tag):
    """Dispara len(users) POST al mismo asiento, todos a la vez. Devuelve la lista de intentos."""
    for u in set(users):
        get_token(u)  # se pide antes para no demorar el disparo

    def mk(i, u):
        def f():
            s, rid, resp = reservar(u, seat, correlation=f"{tag}-{RUN}-{i}")
            return {"user": u, "status": s, "rid": rid, "resp": resp}
        return f

    return disparar_simultaneo([mk(i, u) for i, u in enumerate(users)])


# ---------------------------------------------------------------------
# PRUEBA 18 - Dos usuarios reservando el mismo asiento simultáneamente
# ---------------------------------------------------------------------
def test_18(args):
    for ronda in range(1, args.rondas + 1):
        seat = asiento()
        tid = "18" if args.rondas == 1 else f"18.{ronda}"
        intentos = lanzar([USER_1, USER_2], seat, "t18")
        print(f"   (ronda {ronda}/{args.rondas}, asiento {corto(seat)})")
        verificar_carrera(tid, seat, intentos)


# ---------------------------------------------------------------------
# PRUEBA 19 - Múltiples solicitudes simultáneas sobre un mismo asiento
# ---------------------------------------------------------------------
def test_19(args):
    seat = asiento()
    n = args.solicitudes
    users = [USER_1 if i % 2 == 0 else USER_2 for i in range(n)]
    t0 = time.time()
    intentos = lanzar(users, seat, "t19")
    print(f"   ({n} solicitudes disparadas en {time.time() - t0:.1f} s, asiento {corto(seat)})")
    verificar_carrera("19", seat, intentos)


# ---------------------------------------------------------------------
# PRUEBA 20 - Reservas simultáneas para diferentes asientos
# ---------------------------------------------------------------------
def test_20(args):
    m = args.asientos_simultaneos
    seats = [asiento() for _ in range(m)]
    users = [USER_1 if i % 2 == 0 else USER_2 for i in range(m)]
    for u in set(users):
        get_token(u)

    def mk(i):
        def f():
            s, rid, resp = reservar(users[i], seats[i], correlation=f"t20-{RUN}-{i}")
            return {"user": users[i], "status": s, "rid": rid, "resp": resp, "seat": seats[i]}
        return f

    t0 = time.time()
    intentos = disparar_simultaneo([mk(i) for i in range(m)])
    codigos = [it["status"] for it in intentos]
    record("20", f"{m} POST simultáneos (asientos distintos)", "todos 202", f"{sorted(set(codigos))}",
           all(c == 202 for c in codigos))
    esperar_todas(intentos)
    total = time.time() - t0
    estados = [estado_de(it["final"]) for it in intentos]
    conf = estados.count("Confirmada")
    record("20", "Todas Confirmadas", f"{m} Confirmadas", f"{conf} Confirmadas ({total:.1f} s en total)",
           conf == m, [f"{corto(it['seat'])}:{estado_de(it['final'])}/{motivo_de(it['final'])}"
                       for it in intentos if estado_de(it["final"]) != "Confirmada"])
    ocup = [it for it in intentos if motivo_de(it["final"]) == "AsientoOcupado"]
    record("20", "Ningún rechazo por AsientoOcupado", "0", len(ocup), not ocup)

    # Cada asiento figura ocupado y tiene exactamente una reserva
    seats_api = asientos_del_evento() or []
    por_id = {s["id"]: s for s in seats_api}
    libres = [corto(s) for s in seats if not por_id.get(s, {}).get("occupied")]
    record("20", "Todos los asientos figuran ocupados", "0 libres", f"{len(libres)} libres", not libres, libres)
    dup = []
    for s in seats:
        filas = booking_filas_asiento(s)
        if filas is not None and len(filas) != 1:
            dup.append(f"{corto(s)}:{len(filas)}")
    record("20", "Una sola reserva por asiento en Booking", "sin duplicados", dup or "ok", not dup)

    ids_res = [reservation_id_de(it["rid"]) for it in intentos if it.get("rid")]
    cobros = contar_cobros(ids_res)
    if cobros is None:
        revisar("20", "Payment: un cobro por reserva", "sin Docker no se puede consultar la base payment")
    else:
        record("20", "Payment: un cobro por reserva", m, cobros, cobros == m)
    notifs = contar_notificaciones("", ids_res)
    if notifs is None:
        revisar("20", "Notifications: una notificación por reserva", "no se pudo leer Notifications")
    else:
        record("20", "Notifications: una notificación por reserva", m, notifs, notifs == m)

    # Reparto entre las dos réplicas de Booking (consumidores competidores)
    logs = logs_de("booking")
    if logs is None:
        revisar("20", "Reparto entre las dos réplicas de Booking", "sin Docker no se pueden leer los logs de Booking")
        return
    cuentas = {}
    for linea in logs.splitlines():
        if "AUDITORIA inicio reserva" in linea and f"t20-{RUN}-" in linea:
            m_ = re.match(r"^(\S+)\s*\|", linea)
            if m_:
                cuentas[m_.group(1)] = cuentas.get(m_.group(1), 0) + 1
    if len(cuentas) >= 2:
        record("20", "Los mensajes se reparten entre las 2 réplicas", "ambas procesan", cuentas, True)
    elif len(cuentas) == 1:
        # Con pocos mensajes o una réplica reiniciando puede pasar; no es una falla del código por sí sola.
        revisar("20", "Los mensajes se reparten entre las 2 réplicas",
                f"solo procesó una réplica: {cuentas}. Ver `docker compose ps` (¿hay 2 réplicas de booking?) y repetir",
                esperado="ambas", obtenido=cuentas)
    else:
        revisar("20", "Los mensajes se reparten entre las 2 réplicas",
                "no se encontraron líneas AUDITORIA de esta corrida en `docker compose logs booking`")


# ---------------------------------------------------------------------
# PRUEBA 21 - Repetir solicitudes concurrentes del mismo usuario
# ---------------------------------------------------------------------
def test_21(args):
    seat = asiento()
    n = args.clics
    intentos = lanzar([USER_1] * n, seat, "t21")
    print(f"   ({n} clics simultáneos del mismo usuario, asiento {corto(seat)})")
    verificar_carrera("21", seat, intentos)
    mine = mis_reservas(USER_1)
    if mine is not None:
        ids = {it["rid"] for it in intentos if it.get("rid")}
        en_hist = [m for m in mine if m.get("requestId") in ids]
        conf = [m for m in en_hist if m.get("status") == "Confirmada"]
        record("21", "Historial: una sola Confirmada para el asiento", "1", len(conf), len(conf) == 1)


def extra(p):
    p.add_argument("--rondas", type=int, default=3, help="repeticiones de la prueba 18 (un asiento por ronda). Por defecto 3")
    p.add_argument("--solicitudes", type=int, default=20, help="cantidad de solicitudes de la prueba 19. Por defecto 20")
    p.add_argument("--asientos-simultaneos", type=int, default=10, help="asientos distintos de la prueba 20. Por defecto 10")
    p.add_argument("--clics", type=int, default=10, help="solicitudes iguales de la prueba 21. Por defecto 10")


if __name__ == "__main__":
    correr_bloque(
        "D", "Concurrencia",
        tests=[("18", test_18), ("19", test_19), ("20", test_20), ("21", test_21)],
        evento=1, seat_inicial=1,
        necesarios=lambda a: ((a.rondas if "18" in a.seleccion else 0) + (1 if "19" in a.seleccion else 0)
                              + (a.asientos_simultaneos if "20" in a.seleccion else 0) + (1 if "21" in a.seleccion else 0)),
        extra_args=extra)
