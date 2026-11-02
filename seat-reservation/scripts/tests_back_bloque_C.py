#!/usr/bin/env python3
"""
Pruebas de caja negra - Bloque C (estados y flujo asincrónico)
Proyecto: Seat Reservation (back .NET, microservicios)

Pruebas: 14 (consulta inmediata), 15 (polling), 16 (reintentos / idempotencia), 17 (estados inconsistentes).

Solo usa la librería estándar de Python 3.8+ (no hace falta pip install). Necesita tests_back_comun.py
en la misma carpeta.

Uso (desde la carpeta seat-reservation):
    python scripts/tests_back_bloque_C.py
    python scripts/tests_back_bloque_C.py --pago-rechazado           # suma 17b (ver nota)


Nota 17b (--pago-rechazado): necesita Booking levantado con un precio por encima del máximo de Payment
(por ejemplo Booking__SeatPriceCents=20000000 con Payment__MaxAmount=100000), igual que la 13d del bloque B.
El estado "Vencida" no se prueba acá: una reserva solo vence si queda Retenida más de Booking__HoldSeconds
(120 s por defecto), y con Payment funcionando pasa a Confirmada/Rechazada en menos de un segundo.
"""

import sys
import time
import uuid

from tests_back_comun import *


def sec_txt(estados):
    return " -> ".join(comprimir(estados)) or "(vacío)"


def sondear(user, rid, extra_final=0.0, intervalo=0.15, limite=POLL_SECONDS):
    """Consulta GET /reservations/{id} sin pausas largas hasta ver un estado final (más 'extra_final' s).
    Devuelve (estados_vistos, codigos_http)."""
    estados, codigos = [], []
    fin = time.time() + limite
    t_final = None
    while time.time() < fin:
        s, obj = consultar(user, rid)
        codigos.append(s)
        if s == 200 and isinstance(obj, dict):
            est = obj.get("status")
            estados.append(est)
            if est in FINAL_STATES and t_final is None:
                t_final = time.time()
        if t_final is not None and time.time() - t_final >= extra_final:
            break
        time.sleep(intervalo)
    return estados, codigos


# ---------------------------------------------------------------------
# PRUEBA 14 - Consultar una reserva inmediatamente después de crearla
# ---------------------------------------------------------------------
def test_14(args):
    seat = asiento()
    status, rid, resp = reservar(USER_1, seat)
    record("14", "POST de la reserva", "202", status, status == 202, resp)
    if status != 202 or not rid:
        return

    # Primera consulta, pegada al 202 (sin ninguna espera)
    s, obj = consultar(USER_1, rid)
    est = estado_de(obj)
    record("14", "Primera consulta inmediata", "200 + estado válido", f"{s} {est}",
           s == 200 and est in VALID_STATES, obj)

    # Ráfaga de consultas sin pausa: recorre la zona de consistencia eventual
    vistos, codigos = [], []
    for _ in range(8):
        s, obj = consultar(USER_1, rid)
        codigos.append(s)
        vistos.append(estado_de(obj))
    malos = [c for c in codigos if c != 200]
    record("14", "Ráfaga de 8 consultas inmediatas", "todas 200 (nunca 404/500)",
           f"códigos {sorted(set(codigos))}", not malos, sec_txt(vistos))
    record("14", "Estados de la ráfaga coherentes", "sin retrocesos", sec_txt(vistos),
           secuencia_valida([e for e in vistos if e in STATE_RANK]))

    r = esperar_final(USER_1, rid)
    record("14", "Estado final", "Confirmada", estado_de(r), estado_de(r) == "Confirmada", r)


# ---------------------------------------------------------------------
# PRUEBA 15 - Consultar una reserva mientras se procesa (polling)
# ---------------------------------------------------------------------
def test_15(args):
    seat = asiento()
    status, rid1, resp = reservar(USER_1, seat)
    record("15", "POST de la reserva (usuario1)", "202", status, status == 202, resp)
    if status != 202 or not rid1:
        return

    estados, codigos = sondear(USER_1, rid1, extra_final=3.0)
    malos = [c for c in codigos if c != 200]
    record("15", "Todas las consultas del polling responden 200", "200", f"{len(codigos)} consultas, "
           f"{len(malos)} distintas de 200", not malos, codigos[:20])
    record("15", "La secuencia respeta el orden y no retrocede", "EnProceso -> Retenida -> Confirmada",
           sec_txt(estados), secuencia_valida(estados) and bool(estados))
    record("15", "Termina en un estado final y se mantiene", "Confirmada", estados[-1] if estados else "-",
           bool(estados) and estados[-1] == "Confirmada")

    # Segundo usuario sobre el mismo asiento: debe terminar Rechazada sin pasar nunca por Confirmada
    s2, rid2, resp2 = reservar(USER_2, seat)
    record("15", "POST del mismo asiento (usuario2)", "202", s2, s2 == 202, resp2)
    if s2 == 202 and rid2:
        est2, cod2 = sondear(USER_2, rid2, extra_final=2.0)
        r2 = resultado(USER_2, rid2)
        record("15", "Secuencia de la solicitud rechazada", "... -> Rechazada (sin Confirmada)", sec_txt(est2),
               secuencia_valida(est2) and "Confirmada" not in est2 and bool(est2) and est2[-1] == "Rechazada")
        record("15", "Motivo de la rechazada", "AsientoOcupado", motivo_de(r2), motivo_de(r2) == "AsientoOcupado", r2)

    # Información ajena / inexistente / id inválido -> 404 (sin filtrar si existe)
    s, obj = consultar(USER_2, rid1)
    record("15", "Solicitud de OTRO usuario", "404", s, s == 404, obj)
    s, obj = consultar(USER_1, str(uuid.uuid4()))
    record("15", "Solicitud inexistente", "404", s, s == 404, obj)
    s, obj = consultar(USER_1, "no-es-un-guid")
    record("15", "Id con formato inválido", "404", s, s == 404, obj)


# ---------------------------------------------------------------------
# PRUEBA 16 - Reintentar una operación asincrónica
# ---------------------------------------------------------------------
def test_16(args):
    seat = asiento()

    # (a) Reintento: segundo POST del mismo usuario y mismo asiento, pegado al primero
    sa, rid_a, _ = reservar(USER_1, seat, correlation="t16-original")
    sb, rid_b, _ = reservar(USER_1, seat, correlation="t16-reintento")
    record("16", "Original y reintento responden", "202 y 202", f"{sa} y {sb}", sa == 202 and sb == 202)
    if not rid_a or not rid_b:
        return
    record("16", "Cada POST genera un requestId distinto", "distintos", "distintos" if rid_a != rid_b else "iguales",
           rid_a != rid_b)
    ra = esperar_final(USER_1, rid_a)
    rb = esperar_final(USER_1, rid_b)
    estados = sorted([estado_de(ra), estado_de(rb)])
    record("16", "Una Confirmada y una Rechazada", "Confirmada + Rechazada", " + ".join(estados),
           estados == ["Confirmada", "Rechazada"], f"{ra} | {rb}")
    ganadora, perdedora = (rid_a, rid_b) if estado_de(ra) == "Confirmada" else (rid_b, rid_a)

    filas = booking_filas_asiento(seat)
    if filas is None:
        revisar("16", "Filas en Booking para el asiento", "no se pudo consultar Booking directo "
                "(puertos 5002/5003, token de availability-service)")
    else:
        record("16", "Booking: una fila por solicitud (2) y una sola activa", "2 filas, 1 activa",
               f"{len(filas)} filas, {len(activas(filas))} activas", len(filas) == 2 and len(activas(filas)) == 1)

    ids_res = [reservation_id_de(ganadora), reservation_id_de(perdedora)]
    cobros = contar_cobros(ids_res)
    if cobros is None:
        revisar("16", "Payment: un único cobro", "sin Docker no se puede consultar la base payment")
    else:
        record("16", "Payment: un único cobro para el asiento", "1", cobros, cobros == 1)
    notifs = contar_notificaciones(seat, ids_res)
    if notifs is None:
        revisar("16", "Notifications: una única notificación", "no se pudo leer Notifications")
    else:
        record("16", "Notifications: una única notificación", "1", notifs, notifs == 1)

    # (b) Reentrega del mismo mensaje (mismo RequestId) directamente en el broker
    pub = [
        rabbit_publicar(mensaje_reserva(ganadora, seat, USER_1, "t16-reentrega"), ganadora),
        rabbit_publicar(mensaje_reserva(ganadora, seat, USER_1, "t16-reentrega"), ganadora),
        rabbit_publicar(mensaje_reserva(perdedora, seat, USER_1, "t16-reentrega"), perdedora),
    ]
    if not all(pub):
        revisar("16", "Reentrega de mensajes por RabbitMQ", "no se pudo publicar en el exchange "
                f"{RABBIT_EXCHANGE} (API de gestión {RABBIT_API}, usuario app/app)", obtenido=pub)
        return
    record("16", "3 mensajes duplicados publicados en el broker", "routed", "routed", True)
    # Se espera a que la cola quede vacía (todos consumidos) y un margen
    esperar_cola(RABBIT_QUEUE, lambda q: q.get("messages", 1) == 0, 20)
    time.sleep(4)

    filas2 = booking_filas_asiento(seat)
    if filas2 is not None:
        mismas = [f for f in filas2 if f.get("requestId") in (ganadora, perdedora)]
        record("16", "Booking: sigue habiendo 2 filas y una activa", "2 filas, 1 activa",
               f"{len(filas2)} filas, {len(activas(filas2))} activas", len(filas2) == 2 and len(activas(filas2)) == 1)
        por_req = {r: sum(1 for f in mismas if f.get("requestId") == r) for r in (ganadora, perdedora)}
        record("16", "Booking: una sola reserva por RequestId", "1 y 1", f"{list(por_req.values())}",
               all(v == 1 for v in por_req.values()))
    rg = resultado(USER_1, ganadora)
    record("16", "La reserva original sigue Confirmada", "Confirmada", estado_de(rg), estado_de(rg) == "Confirmada", rg)
    cobros2 = contar_cobros(ids_res)
    if cobros2 is not None:
        record("16", "Payment: sigue habiendo un único cobro", "1", cobros2, cobros2 == 1)
    notifs2 = contar_notificaciones(seat, ids_res)
    if notifs2 is not None:
        record("16", "Notifications: sigue habiendo una única notificación", "1", notifs2, notifs2 == 1)


# ---------------------------------------------------------------------
# PRUEBA 17 - Verificar estados inconsistentes
# ---------------------------------------------------------------------
def _en_mis_reservas(user, rid):
    mine = mis_reservas(user)
    if mine is None:
        return None, 0
    coinc = [m for m in mine if m.get("requestId") == rid]
    return (coinc[0] if coinc else None), len(coinc)


def test_17(args):
    seat = asiento()
    s1, rid1, _ = reservar(USER_1, seat, correlation="t17-confirmada")
    r1 = esperar_final(USER_1, rid1) if rid1 else None
    record("17", "Reserva (usuario1) Confirmada", "Confirmada", estado_de(r1), estado_de(r1) == "Confirmada", r1)

    # --- Reserva Confirmada ---
    ocupado = asiento_ocupado(seat)
    record("17", "Confirmada: el asiento figura ocupado", "occupied=true", ocupado, ocupado is True)
    fila, veces = _en_mis_reservas(USER_1, rid1)
    if fila is None and veces == 0:
        record("17", "Confirmada: aparece en /reservations/mine", "1 vez, Confirmada", "no aparece", False)
    else:
        record("17", "Confirmada: aparece en /reservations/mine con el mismo estado", "1 vez, Confirmada",
               f"{veces} vez/veces, {fila.get('status')}", veces == 1 and fila.get("status") == "Confirmada", fila)
    be = booking_estado(rid1)
    if be is not None:
        record("17", "Confirmada: Booking coincide con Availability", "Confirmada", be.get("status"),
               be.get("status") == estado_de(r1))
    res_id1 = be.get("reservationId") if be else None
    n = contar_notificaciones(seat, [res_id1])
    if n is None:
        revisar("17", "Confirmada: exactamente una notificación", "no se pudo leer Notifications")
    else:
        record("17", "Confirmada: exactamente una notificación", "1", n, n == 1)

    # --- Reserva Rechazada (otro usuario, mismo asiento) ---
    s2, rid2, _ = reservar(USER_2, seat, correlation="t17-rechazada")
    r2 = esperar_final(USER_2, rid2) if rid2 else None
    record("17", "Reserva (usuario2) Rechazada por asiento ocupado", "Rechazada / AsientoOcupado",
           f"{estado_de(r2)} / {motivo_de(r2)}", estado_de(r2) == "Rechazada" and motivo_de(r2) == "AsientoOcupado", r2)
    fila2, veces2 = _en_mis_reservas(USER_2, rid2)
    record("17", "Rechazada: aparece en /reservations/mine de usuario2", "1 vez, Rechazada",
           f"{veces2} vez/veces, {fila2.get('status') if fila2 else '-'}",
           veces2 == 1 and fila2 is not None and fila2.get("status") == "Rechazada", fila2)
    en_u1, _ = _en_mis_reservas(USER_1, rid2)
    record("17", "Rechazada: NO aparece en el historial de usuario1", "no aparece", "aparece" if en_u1 else "no aparece",
           en_u1 is None)
    res_id2 = reservation_id_de(rid2)
    n2 = contar_notificaciones(seat, [res_id2]) if res_id2 else None
    if n2 is None:
        revisar("17", "Rechazada: no existe notificación", "no se pudo consultar (sin Docker o sin Booking directo)")
    else:
        record("17", "Rechazada: no existe notificación", "0", n2, n2 == 0)
    ocupado2 = asiento_ocupado(seat)
    record("17", "El asiento sigue ocupado solo por la reserva Confirmada", "occupied=true", ocupado2, ocupado2 is True)
    r1b = resultado(USER_1, rid1)
    record("17", "La reserva Confirmada no fue modificada", "Confirmada", estado_de(r1b), estado_de(r1b) == "Confirmada")
    # Cada requestId aparece una sola vez en el historial (sin duplicados)
    mine = mis_reservas(USER_1) or []
    ids_mine = [m.get("requestId") for m in mine]
    record("17", "Historial de usuario1 sin requestId repetidos", "sin repetidos",
           f"{len(ids_mine)} filas, {len(set(ids_mine))} distintas", len(ids_mine) == len(set(ids_mine)))

    # --- 17b: Rechazada por pago fallido (necesita configuración especial) ---
    if getattr(args, "pago_rechazado", False):
        seat_p = asiento()
        s, rid_p, resp = reservar(USER_1, seat_p, correlation="t17-pago-fallido")
        r = esperar_final(USER_1, rid_p) if rid_p else None
        record("17b", "Rechazada por pago fallido", "Rechazada / PagoFallido",
               f"{estado_de(r)} / {motivo_de(r)}", estado_de(r) == "Rechazada" and motivo_de(r) == "PagoFallido", r)
        oc = asiento_ocupado(seat_p)
        record("17b", "El asiento queda libre", "occupied=false", oc, oc is False)
        f_p, v_p = _en_mis_reservas(USER_1, rid_p)
        record("17b", "Aparece en /reservations/mine como Rechazada", "1 vez, Rechazada",
               f"{v_p} vez/veces, {f_p.get('status') if f_p else '-'}",
               v_p == 1 and f_p is not None and f_p.get("status") == "Rechazada")
        rid_res = reservation_id_de(rid_p)
        n = contar_notificaciones(seat_p, [rid_res]) if rid_res else None
        if n is None:
            revisar("17b", "No existe notificación", "no se pudo consultar")
        else:
            record("17b", "No existe notificación", "0", n, n == 0)


def extra(p):
    p.add_argument("--pago-rechazado", action="store_true",
                   help="ejecuta también 17b (requiere Booking con precio alto, ver la ayuda del archivo)")


if __name__ == "__main__":
    correr_bloque(
        "C", "Estados y flujo asincrónico",
        tests=[("14", test_14), ("15", test_15), ("16", test_16), ("17", test_17)],
        evento=0, seat_inicial=9,
        necesarios=lambda a: sum(1 for t in ("14", "15", "16", "17") if t in a.seleccion)
        + (1 if a.pago_rechazado and "17" in a.seleccion else 0),
        extra_args=extra)
