#!/usr/bin/env python3
"""
Pruebas de caja negra - Bloque E (microservicios y tolerancia a fallos)
Proyecto: Seat Reservation (back .NET, microservicios)

Solo usa la librería estándar de Python 3.8+ (no hace falta pip install). Necesita tests_back_comun.py
en la misma carpeta.

REQUIERE DOCKER: el script ejecuta `docker compose stop/start/pause/unpause/restart` sobre el sistema
que esté corriendo (el docker-compose.yml de la carpeta seat-reservation). Correrlo SIEMPRE desde esa
carpeta o con el python de cualquier lado (calcula la carpeta del proyecto a partir de su propia ruta).
Al terminar (o con Ctrl+C) intenta dejar todo levantado y sin pausar.

Uso (desde la carpeta seat-reservation):
    python scripts/tests_back_bloque_E.py
    python scripts/tests_back_bloque_E.py --caida-a-mitad              # suma 26e (ver nota)
    python scripts/tests_back_bloque_E.py --purgar-dead                # vacía booking.dead al terminar

IMPORTANTE:
  * Tarda varios minutos (esperas por arranques de contenedores y por timeouts de 5 s).
  * La 25a deja UN mensaje en la cola booking.dead (es lo que se verifica). Se puede vaciar con
    --purgar-dead.
  * La 25b necesita bajar la imagen fullstorydev/grpcurl (hace falta internet la primera vez) y ejecuta
    la llamada gRPC desde un contenedor dentro de la red de Docker, porque Payment no está publicado.

"""

import time

from tests_back_comun import *

RUN = datetime.now().strftime("%H%M%S")
SERVICIOS = ("payment", "notifications", "booking", "rabbitmq")


# ---------------------------------------------------------------------
# Ayudas del bloque
# ---------------------------------------------------------------------
def restaurar_servicios(args=None):
    for svc in SERVICIOS:
        compose("unpause", svc)            # falla (sin problema) si no estaba pausado
    compose("start", *SERVICIOS)
    print("   servicios iniciados; esperando que el sistema responda...")
    esperar_booking(120)


def accion(test_id, caso, *cmd):
    """Ejecuta un comando docker compose y lo registra como FAIL si falla."""
    rc, out = compose(*cmd)
    if rc != 0:
        record(test_id, caso, "comando OK", f"rc={rc}", False, out.strip()[-300:])
    return rc == 0


def esperar_booking(segundos=90):
    """Espera hasta que GET /events/{id}/seats responda 200 (Availability + Booking funcionando)."""
    fin = time.time() + segundos
    while time.time() < fin:
        if asientos_del_evento() is not None:
            return True
        time.sleep(2)
    return False


def esperar_consumidores(minimo=2, segundos=120):
    """Espera a que la cola booking tenga al menos 'minimo' consumidores. Devuelve el dict de la cola."""
    return esperar_cola(RABBIT_QUEUE, lambda q: q.get("consumers", 0) >= minimo, segundos)


def esperar_rabbit(segundos=120):
    fin = time.time() + segundos
    while time.time() < fin:
        if rabbit_cola(RABBIT_QUEUE) is not None:
            return True
        time.sleep(2)
    return False


def reservar_y_esperar(user, seat, correlation, timeout=POLL_SECONDS):
    """POST + espera del estado final. Devuelve (status_post, rid, final, segundos_desde_el_POST)."""
    s, rid, _ = reservar(user, seat, correlation=correlation)
    t0 = time.time()
    if s != 202 or not rid:
        return s, rid, None, 0.0
    final = esperar_final(user, rid, timeout)
    return s, rid, final, time.time() - t0


def reservar_con_reintento(user, seat, correlation, intentos=8, pausa=4):
    """Para después de reiniciar RabbitMQ: el primer POST puede fallar con 503 hasta que Availability
    vuelve a conectar. Devuelve (rid, [status de cada intento])."""
    estados = []
    for _ in range(intentos):
        s, rid, _ = reservar(user, seat, correlation=correlation)
        estados.append(s)
        if s == 202 and rid:
            return rid, estados
        time.sleep(pausa)
    return None, estados


def hay_aviso_notificacion(correlation):
    """¿Booking registró la advertencia 'No se pudo notificar' para esa reserva? None si no hay logs."""
    logs = logs_de("booking")
    if logs is None:
        return None
    for linea in logs.splitlines():
        if "No se pudo notificar la reserva confirmada" in linea and correlation in linea:
            return True
    return False


# ---------------------------------------------------------------------
# PRUEBA 22 - Fallo del servicio encargado de reservas (Booking)
# ---------------------------------------------------------------------
def test_22(args):
    seat = asiento()
    if not accion("22", "docker compose stop booking", "stop", "booking"):
        return
    time.sleep(3)

    # El POST se acepta igual: el mensaje queda encolado en RabbitMQ hasta que Booking vuelva
    s, rid, resp = reservar(USER_1, seat, correlation=f"t22-{RUN}")
    record("22", "POST /reservations con Booking caído", "202", s, s == 202 and bool(rid), resp)
    q = esperar_cola(RABBIT_QUEUE, lambda c: c.get("messages", 0) >= 1, 20)
    if q is None:
        revisar("22", "El mensaje queda encolado en RabbitMQ", "no se pudo leer la API de gestión de RabbitMQ")
    else:
        record("22", "El mensaje queda encolado en RabbitMQ", ">= 1 mensaje", f"{q.get('messages')} mensaje(s), "
               f"{q.get('consumers')} consumidores", q.get("messages", 0) >= 1)

    # Las consultas que dependen de Booking deben dar 503 de forma controlada (y rápido)
    st, tx, _, seg = http_completo("GET", f"{AVAILABILITY_URL}/events/{CFG.evento_id}/seats")
    record("22", "GET /events/{id}/seats", "503", f"{st} ({seg:.1f} s)", st == 503 and seg < 15, tx[:150])
    if rid:
        st, tx, _, seg = http_completo("GET", f"{AVAILABILITY_URL}/reservations/{rid}", user=USER_1)
        record("22", "GET /reservations/{requestId}", "503", f"{st} ({seg:.1f} s)", st == 503 and seg < 15, tx[:150])
    st, tx, _, seg = http_completo("GET", AVAILABILITY_URL + "/reservations/mine", user=USER_1)
    record("22", "GET /reservations/mine", "503", f"{st} ({seg:.1f} s)", st == 503 and seg < 15, tx[:150])
    st, tx, _, seg = http_completo("GET", AVAILABILITY_URL + "/events")
    record("22", "GET /events sigue funcionando", "200", f"{st} ({seg:.1f} s)", st == 200, tx[:100])

    # Vuelve Booking: la solicitud encolada se procesa
    if not accion("22", "docker compose start booking", "start", "booking"):
        return
    ok = esperar_booking(120)
    record("22", "Availability vuelve a responder al volver Booking", "200 en <= 120 s", "sí" if ok else "no", ok)
    if rid:
        r = esperar_final(USER_1, rid, 90)
        record("22", "La solicitud encolada se procesa al volver Booking", "Confirmada", estado_de(r),
               estado_de(r) == "Confirmada", r)


# ---------------------------------------------------------------------
# PRUEBA 23 - Fallo de un servicio dependiente (Payment, Notifications, RabbitMQ)
# ---------------------------------------------------------------------
def test_23(args):
    # ---- 23a: Payment caído ----
    seat = asiento()
    if accion("23a", "docker compose stop payment", "stop", "payment"):
        time.sleep(3)
        s, rid, final, seg = reservar_y_esperar(USER_1, seat, f"t23a-{RUN}", 45)
        record("23a", "POST con Payment caído", "202", s, s == 202, "")
        record("23a", "Estado final", "Rechazada", estado_de(final), estado_de(final) == "Rechazada",
               f"{final} ({seg:.1f} s)")
        record("23a", "Motivo del rechazo", "PagoNoDisponible", motivo_de(final), motivo_de(final) == "PagoNoDisponible")
        oc = asiento_ocupado(seat)
        record("23a", "El asiento queda libre", "occupied=false", oc, oc is False)
        accion("23a", "docker compose start payment", "start", "payment")
        time.sleep(8)

    # ---- 23b: Notifications caído ----
    seat = asiento()
    if accion("23b", "docker compose stop notifications", "stop", "notifications"):
        time.sleep(3)
        corr = f"t23b-{RUN}"
        s, rid, final, seg = reservar_y_esperar(USER_1, seat, corr, 45)
        record("23b", "POST con Notifications caído", "202", s, s == 202)
        record("23b", "La reserva queda igualmente Confirmada", "Confirmada", estado_de(final),
               estado_de(final) == "Confirmada", final)
        record("23b", "La confirmación no se demora", "<= 15 s", f"{seg:.1f} s", seg <= 15)
        oc = asiento_ocupado(seat)
        record("23b", "El asiento figura ocupado", "occupied=true", oc, oc is True)
        time.sleep(4)  # margen para que el log de Booking ya tenga la advertencia
        aviso = hay_aviso_notificacion(corr)
        if aviso is None:
            revisar("23b", "Booking registra una advertencia en el log", "no se pudieron leer los logs de Booking")
        else:
            record("23b", "Booking registra una advertencia en el log", "advertencia presente",
                   "presente" if aviso else "no encontrada", aviso)
        accion("23b", "docker compose start notifications", "start", "notifications")
        time.sleep(8)

    # ---- 23c: RabbitMQ caído ----
    seat = asiento()
    if accion("23c", "docker compose stop rabbitmq", "stop", "rabbitmq"):
        time.sleep(3)
        st, tx, _, seg = http_completo("POST", AVAILABILITY_URL + "/reservations",
                                       body={"eventId": CFG.evento_id, "seatId": seat}, user=USER_1,
                                       headers={"X-Correlation-Id": f"t23c-{RUN}"}, timeout=40)
        record("23c", "POST con RabbitMQ caído", "503 en <= 8 s", f"{st} ({seg:.1f} s)", st == 503 and seg <= 8, tx[:150])
        time.sleep(2)
        filas = booking_filas_asiento(seat)
        if filas is None:
            revisar("23c", "No quedó ninguna reserva en Booking", "no se pudo consultar Booking directo")
        else:
            record("23c", "No quedó ninguna reserva en Booking", "0 filas", len(filas), len(filas) == 0)
        oc = asiento_ocupado(seat)
        record("23c", "El asiento sigue libre", "occupied=false", oc, oc is False)
        accion("23c", "docker compose start rabbitmq", "start", "rabbitmq")
        ok = esperar_rabbit(120)
        q = esperar_consumidores(2, 120) if ok else None
        record("23c", "RabbitMQ vuelve y Booking se reconecta", "2 consumidores",
               f"{q.get('consumers') if q else 'sin respuesta'}", bool(q) and q.get("consumers", 0) >= 2)
        # La solicitud que falló nunca se publicó: no debe aparecer como reserva confirmada más tarde
        time.sleep(6)
        filas = booking_filas_asiento(seat)
        if filas is not None:
            record("23c", "Después de volver RabbitMQ sigue sin haber reserva", "0 filas", len(filas), len(filas) == 0)
        esperar_booking(60)


# ---------------------------------------------------------------------
# PRUEBA 24 - Timeout de un microservicio
# ---------------------------------------------------------------------
def test_24(args):
    # ---- 24a: Payment pausado (no responde) ----
    seat = asiento()
    if accion("24a", "docker compose pause payment", "pause", "payment"):
        s, rid, final, seg = reservar_y_esperar(USER_1, seat, f"t24a-{RUN}", 45)
        record("24a", "POST con Payment pausado", "202", s, s == 202)
        record("24a", "Estado final (deadline gRPC de 5 s)", "Rechazada / PagoNoDisponible",
               f"{estado_de(final)} / {motivo_de(final)}",
               estado_de(final) == "Rechazada" and motivo_de(final) == "PagoNoDisponible", final)
        record("24a", "No queda colgada: resuelve en poco más del plazo", "entre 4 y 20 s", f"{seg:.1f} s", 4 <= seg <= 20,
               "menos de 4 s sugiere que Booking no esperó el plazo de 5 s")
        oc = asiento_ocupado(seat)
        record("24a", "El asiento queda libre", "occupied=false", oc, oc is False)
        accion("24a", "docker compose unpause payment", "unpause", "payment")
        time.sleep(8)

    # ---- 24b: Notifications pausado ----
    seat = asiento()
    if accion("24b", "docker compose pause notifications", "pause", "notifications"):
        corr = f"t24b-{RUN}"
        s, rid, final, seg = reservar_y_esperar(USER_1, seat, corr, 45)
        record("24b", "POST con Notifications pausado", "202", s, s == 202)
        record("24b", "La reserva queda Confirmada", "Confirmada", estado_de(final), estado_de(final) == "Confirmada", final)
        record("24b", "No queda colgada", "<= 15 s", f"{seg:.1f} s", seg <= 15)
        time.sleep(5)  # que venza el timeout de 3 s de Notifications
        q = esperar_cola(RABBIT_QUEUE, lambda c: c.get("messages", 1) == 0, 20)
        if q is None:
            revisar("24b", "La cola booking no queda con mensajes sin confirmar", "no se pudo leer RabbitMQ")
        else:
            record("24b", "La cola booking no queda con mensajes sin confirmar", "0 mensajes",
                   f"{q.get('messages')} ({q.get('messages_unacknowledged')} sin ack)", q.get("messages", 1) == 0)
        r2 = resultado(USER_1, rid) if rid else None
        record("24b", "Sigue Confirmada tras vencer el timeout", "Confirmada", estado_de(r2), estado_de(r2) == "Confirmada")
        aviso = hay_aviso_notificacion(corr)
        if aviso is None:
            revisar("24b", "Booking registra una advertencia por el timeout", "no se pudieron leer los logs de Booking")
        else:
            record("24b", "Booking registra una advertencia por el timeout", "advertencia presente",
                   "presente" if aviso else "no encontrada", aviso)
        accion("24b", "docker compose unpause notifications", "unpause", "notifications")
        time.sleep(5)


# ---------------------------------------------------------------------
# PRUEBA 25 - Respuesta inválida de un servicio dependiente
# ---------------------------------------------------------------------
def test_25(args):
    # ---- 25a: mensaje ilegible en la cola booking ----
    antes = rabbit_cola(RABBIT_DEAD_QUEUE)
    if antes is None:
        revisar("25a", "Mensaje ilegible -> booking.dead", "no se pudo leer la API de gestión de RabbitMQ "
                f"({RABBIT_API}, usuario app/app)")
    else:
        n0 = antes.get("messages", 0)
        ok = rabbit_publicar("ESTE MENSAJE NO ES UN JSON VALIDO")
        record("25a", "Se publicó el mensaje ilegible en el exchange", "routed", "routed" if ok else "no ruteado", ok)
        q = esperar_cola(RABBIT_DEAD_QUEUE, lambda c: c.get("messages", 0) >= n0 + 1, 30)
        n1 = q.get("messages") if q else None
        record("25a", "El mensaje aparece en booking.dead", f"{n0 + 1} mensajes", n1, n1 is not None and n1 >= n0 + 1)
        qb = esperar_cola(RABBIT_QUEUE, lambda c: c.get("messages", 1) == 0, 20)
        record("25a", "No queda reencolado en booking (sin bucle)", "0 mensajes", qb.get("messages") if qb else "-",
               bool(qb) and qb.get("messages", 1) == 0)
        record("25a", "Los consumidores siguen conectados", "2 consumidores", qb.get("consumers") if qb else "-",
               bool(qb) and qb.get("consumers", 0) >= 2)
        seat = asiento()
        s, rid, final, seg = reservar_y_esperar(USER_1, seat, f"t25a-{RUN}")
        record("25a", "Una reserva normal posterior se procesa", "Confirmada", estado_de(final),
               s == 202 and estado_de(final) == "Confirmada", final)
        if getattr(args, "purgar_dead", False):
            st, _ = rabbit("DELETE", "/queues/%2F/booking.dead/contents")
            print(f"   (booking.dead purgada, HTTP {st})")

    # ---- 25b: Payment con reservation_id inválido ----
    tok = token_servicio("booking-service")
    for etiqueta, rid_inv in (("no es un GUID", "esto-no-es-un-guid"), ("vacío", "")):
        resp = grpc_cobrar({"reservation_id": rid_inv, "user_id": USER_1, "amount_cents": 1000,
                            "correlation_id": f"t25b-{RUN}"}, tok)
        if resp is None:
            revisar("25b", f"Payment con reservation_id {etiqueta}",
                    "no se pudo ejecutar grpcurl en Docker (¿hay internet para bajar fullstorydev/grpcurl? "
                    "¿está corriendo sr-postgres?). Alternativa: probarlo a mano con grpcurl contra payment:8080 "
                    "desde un contenedor de la red de Docker, con un token de booking-service")
            break
        codigo, salida = resp
        record("25b", f"Payment con reservation_id {etiqueta}", "InvalidArgument", codigo,
               codigo == "InvalidArgument", salida.strip().replace("\n", " ")[:200])
    else:
        # Payment no se cayó: una reserva normal sigue cobrándose
        seat = asiento()
        s, rid, final, seg = reservar_y_esperar(USER_1, seat, f"t25b-{RUN}")
        record("25b", "Payment sigue operativo después de recibir datos inválidos", "Confirmada",
               estado_de(final), s == 202 and estado_de(final) == "Confirmada", final)


# ---------------------------------------------------------------------
# PRUEBA 26 - Recuperación después de un fallo
# ---------------------------------------------------------------------
def test_26(args):
    # ---- 26a: Booking cae con solicitudes pendientes en la cola ----
    seats = [asiento(), asiento()]
    if accion("26a", "docker compose stop booking", "stop", "booking"):
        time.sleep(3)
        rids = []
        for i, seat in enumerate(seats):
            s, rid, _ = reservar(USER_1 if i == 0 else USER_2, seat, correlation=f"t26a-{RUN}-{i}")
            record("26a", f"POST {i + 1} con Booking caído", "202", s, s == 202 and bool(rid))
            rids.append((USER_1 if i == 0 else USER_2, rid, seat))
        q = esperar_cola(RABBIT_QUEUE, lambda c: c.get("messages", 0) >= 2, 20)
        if q is not None:
            record("26a", "Las 2 solicitudes quedan encoladas", ">= 2 mensajes", q.get("messages"), q.get("messages", 0) >= 2)
        accion("26a", "docker compose start booking", "start", "booking")
        q = esperar_consumidores(2, 120)
        record("26a", "Booking se reconecta al broker", "2 consumidores", q.get("consumers") if q else "-",
               bool(q) and q.get("consumers", 0) >= 2)
        esperar_booking(90)
        for user, rid, seat in rids:
            if not rid:
                continue
            r = esperar_final(user, rid, 90)
            record("26a", f"Solicitud pendiente del asiento {corto(seat)} se procesa", "Confirmada",
                   estado_de(r), estado_de(r) == "Confirmada", r)
            filas = booking_filas_asiento(seat)
            if filas is not None:
                record("26a", f"Sin duplicados en Booking (asiento {corto(seat)})", "1 fila", len(filas), len(filas) == 1)
        cobros = contar_cobros([reservation_id_de(rid) for _, rid, _ in rids])
        if cobros is None:
            revisar("26a", "Sin cobros duplicados", "sin Docker no se puede consultar la base payment")
        else:
            record("26a", "Un cobro por solicitud (sin duplicados)", 2, cobros, cobros == 2)

    # ---- 26b: reinicio de Payment ----
    if accion("26b", "docker compose restart payment", "restart", "payment"):
        time.sleep(10)
        _reserva_post_reinicio("26b", "Payment")

    # ---- 26c: reinicio de Notifications ----
    if accion("26c", "docker compose restart notifications", "restart", "notifications"):
        time.sleep(10)
        seat = asiento()
        s, rid, final, seg = reservar_y_esperar(USER_1, seat, f"t26c-{RUN}")
        record("26c", "Reserva después de reiniciar Notifications", "Confirmada", estado_de(final),
               s == 202 and estado_de(final) == "Confirmada", final)
        time.sleep(2)
        n = contar_notificaciones(seat, [reservation_id_de(rid)] if rid else [])
        if n is None:
            revisar("26c", "La notificación se registra", "no se pudo leer Notifications")
        else:
            record("26c", "La notificación se registra", "1", n, n == 1)

    # ---- 26d: reinicio de RabbitMQ ----
    if accion("26d", "docker compose restart rabbitmq", "restart", "rabbitmq"):
        ok = esperar_rabbit(150)
        q = esperar_consumidores(2, 150) if ok else None
        record("26d", "Booking se reconecta a RabbitMQ", "2 consumidores", q.get("consumers") if q else "sin respuesta",
               bool(q) and q.get("consumers", 0) >= 2)
        seat = asiento()
        rid, intentos = reservar_con_reintento(USER_1, seat, f"t26d-{RUN}")
        record("26d", "Availability vuelve a publicar", "202 en <= 8 intentos", f"intentos: {intentos}", rid is not None)
        if len(intentos) > 1 and rid:
            revisar("26d", "El primer POST tras volver RabbitMQ no fue 202",
                    f"intentos: {intentos} (Availability tardó en reconectar; no es grave pero se nota)")
        if rid:
            r = esperar_final(USER_1, rid, 60)
            record("26d", "La reserva posterior se procesa", "Confirmada", estado_de(r), estado_de(r) == "Confirmada", r)

    # ---- 26e: Booking cae a mitad de un procesamiento (opcional) ----
    if getattr(args, "caida_a_mitad", False):
        _caida_a_mitad()


def _reserva_post_reinicio(tid, nombre):
    """Reserva después de reiniciar un servicio. Si el primer intento falla pero el segundo anda, es REVISAR."""
    seat = asiento()
    s, rid, final, seg = reservar_y_esperar(USER_1, seat, f"t{tid}-{RUN}")
    if s == 202 and estado_de(final) == "Confirmada":
        record(tid, f"Reserva después de reiniciar {nombre}", "Confirmada", estado_de(final), True, final)
        return
    seat2 = asiento()
    s2, rid2, final2, _ = reservar_y_esperar(USER_1, seat2, f"t{tid}b-{RUN}")
    if s2 == 202 and estado_de(final2) == "Confirmada":
        revisar(tid, f"Reserva después de reiniciar {nombre}",
                f"el 1er intento terminó {estado_de(final)}/{motivo_de(final)} y el 2do Confirmada: "
                f"se recupera, pero no al instante", esperado="Confirmada", obtenido=estado_de(final))
    else:
        record(tid, f"Reserva después de reiniciar {nombre}", "Confirmada",
               f"{estado_de(final)} / {estado_de(final2)}", False, f"{final} | {final2}")


def _caida_a_mitad():
    seat = asiento()
    if not accion("26e", "docker compose pause payment", "pause", "payment"):
        return
    s, rid, _ = reservar(USER_1, seat, correlation=f"t26e-{RUN}")
    record("26e", "POST con Payment pausado", "202", s, s == 202 and bool(rid))
    if not rid:
        accion("26e", "unpause payment", "unpause", "payment")
        return
    # Esperar a que Booking deje la reserva Retenida (ya insertó la fila y está esperando el cobro)
    retenida = False
    fin = time.time() + 12
    while time.time() < fin:
        r = resultado(USER_1, rid)
        if estado_de(r) == "Retenida":
            retenida = True
            break
        time.sleep(0.2)
    record("26e", "Booking dejó la reserva Retenida (esperando a Payment)", "Retenida", "Retenida" if retenida else "no se vio", retenida)
    compose("kill", "booking")           # SIGKILL a las dos réplicas: el mensaje queda sin confirmar
    compose("unpause", "payment")
    time.sleep(2)
    accion("26e", "docker compose start booking", "start", "booking")
    esperar_consumidores(2, 120)
    esperar_booking(90)
    t0 = time.time()
    r = None
    while time.time() - t0 < 150:      # más que Booking__HoldSeconds (120 s por defecto)
        r = resultado(USER_1, rid)
        if estado_de(r) in FINAL_STATES:
            break
        time.sleep(2)
    record("26e", "Reserva interrumpida a mitad de procesamiento", "Confirmada", f"{estado_de(r)} (tras {time.time() - t0:.0f} s)",
           estado_de(r) == "Confirmada",
           "Si queda Retenida y luego Vencida: el reproceso se ignoró por idempotencia con la fila a medias. " + str(r))
    filas = booking_filas_asiento(seat)
    if filas is not None:
        record("26e", "Sin filas duplicadas en Booking", "1 fila", len(filas), len(filas) == 1)
    cobros = contar_cobros([reservation_id_de(rid)])
    if cobros is not None:
        record("26e", "Sin cobros duplicados", "<= 1", cobros, cobros <= 1)


def extra(p):
    p.add_argument("--caida-a-mitad", action="store_true",
                   help="ejecuta también 26e (kill de Booking a mitad de un cobro; tarda hasta ~3 min)")
    p.add_argument("--purgar-dead", action="store_true",
                   help="vacía la cola booking.dead después de la 25a")


if __name__ == "__main__":
    correr_bloque(
        "E", "Microservicios y tolerancia a fallos",
        tests=[("22", test_22), ("23", test_23), ("24", test_24), ("25", test_25), ("26", test_26)],
        evento=2, seat_inicial=1,
        necesarios=lambda a: 14 + (1 if a.caida_a_mitad else 0),
        extra_args=extra, requiere_docker=True, despues=restaurar_servicios,
        notas="ATENCIÓN: este bloque baja, pausa y reinicia servicios del docker compose.")
