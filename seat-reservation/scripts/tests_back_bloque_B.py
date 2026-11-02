#!/usr/bin/env python3
"""
Pruebas de caja negra - Bloque B (reglas de negocio)
Proyecto: Seat Reservation (back .NET, microservicios)

Solo usa la librería estándar de Python 3.8+ (no hace falta pip install).

Uso:
    python tests_back_bloque_B.py
    python tests_back_bloque_B.py --pago-rechazado          # activa 13d (ver nota abajo)

Nota 13d: necesita que Booking esté levantado con un precio por encima del máximo de
Payment (por ejemplo Booking__SeatPriceCents=20000000 con Payment MaxAmount=100000).
"""

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

# =====================================================================
# CONFIG
# =====================================================================
AVAILABILITY_URL = "http://localhost:5001"
NOTIFICATIONS_URL = "http://localhost:5004"       # solo lectura (GET /notifications)
KEYCLOAK_TOKEN_URL = "http://localhost:8081/realms/seat-reservation/protocol/openid-connect/token"
USER_1 = "usuario1"                               # la contraseña es igual al usuario
USER_2 = "usuario2"
EVENT_ID = "11111111-1111-1111-1111-111111111111"        # evento 0 (20 asientos)
OTHER_EVENT_ID = "22222222-2222-2222-2222-222222222222"  # evento 1 (para la 13c)
NONEXISTENT_ID = "99999999-9999-9999-9999-999999999999"
TIMEOUT = 15
POLL_SECONDS = 25            # tiempo máximo esperando un estado final
FINAL_STATES = ("Confirmada", "Rechazada", "Vencida")
# =====================================================================

RESULTS = []
TOKENS = {}
SEAT_START = 1


# ---------------------------------------------------------------------
# Ayudas
# ---------------------------------------------------------------------
def seat_id(n, event=0):
    """Id del asiento número n del evento 'event' (formato fijo del sembrado de datos)."""
    return f"00000000-0000-0000-{event:04d}-{n:012d}"


def get_token(user):
    if user in TOKENS:
        return TOKENS[user]
    form = urllib.parse.urlencode({
        "grant_type": "password", "client_id": "seat-web",
        "username": user, "password": user,
    }).encode("utf-8")
    req = urllib.request.Request(KEYCLOAK_TOKEN_URL, data=form, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        TOKENS[user] = json.loads(resp.read())["access_token"]
    return TOKENS[user]


def http(method, url, body=None, user=None):
    """Devuelve (status, objeto_json_o_texto)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if user:
        req.add_header("Authorization", "Bearer " + get_token(user))
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        status = e.code
    except Exception as e:
        return 0, f"ERROR DE CONEXION: {e}"
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, raw


def reservar(user, seat, event=EVENT_ID):
    """POST /reservations. Devuelve (status, requestId_o_None, respuesta)."""
    status, resp = http("POST", AVAILABILITY_URL + "/reservations",
                        {"eventId": event, "seatId": seat}, user=user)
    request_id = resp.get("requestId") if isinstance(resp, dict) else None
    return status, request_id, resp


def resultado(user, request_id):
    """GET /reservations/{id}. Devuelve el dict (status, reason) o None."""
    status, resp = http("GET", f"{AVAILABILITY_URL}/reservations/{request_id}", user=user)
    return resp if status == 200 and isinstance(resp, dict) else None


def esperar_final(user, request_id):
    """Consulta cada 0,5 s hasta ver un estado final. Devuelve el último dict visto."""
    ultimo = None
    fin = time.time() + POLL_SECONDS
    while time.time() < fin:
        r = resultado(user, request_id)
        if r:
            ultimo = r
            if r.get("status") in FINAL_STATES:
                return r
        time.sleep(0.5)
    return ultimo


def asiento_ocupado(seat, event=EVENT_ID):
    """True/False según GET /events/{id}/seats; None si no se pudo consultar."""
    status, resp = http("GET", f"{AVAILABILITY_URL}/events/{event}/seats")
    if status != 200 or not isinstance(resp, list):
        return None
    for s in resp:
        if s.get("id") == seat:
            return bool(s.get("occupied"))
    return None


def notificaciones_del_asiento(seat):
    """Cantidad de notificaciones cuyo mensaje menciona el asiento; None si no se puede leer."""
    status, resp = http("GET", NOTIFICATIONS_URL + "/notifications", user=USER_1)
    if status != 200 or not isinstance(resp, list):
        return None
    return sum(1 for n in resp if seat in str(n.get("message", "")))


def record(test_id, caso, esperado, obtenido, ok, detalle=""):
    verdict = "PASS" if ok else "FAIL"
    RESULTS.append({
        "prueba": test_id, "caso": caso, "esperado": esperado,
        "obtenido": obtenido, "veredicto": verdict, "detalle": str(detalle)[:300],
    })
    icon = "[ OK ]" if ok else "[FAIL]"
    print(f"{icon} {test_id} | {caso:<46} esperado={esperado} | obtenido={obtenido}")


def revisar(test_id, caso, motivo):
    """Para chequeos que no se pudieron hacer (por ejemplo, Notifications no accesible)."""
    RESULTS.append({
        "prueba": test_id, "caso": caso, "esperado": "-", "obtenido": "-",
        "veredicto": "REVISAR", "detalle": motivo,
    })
    print(f"[ ?? ] {test_id} | {caso:<46} {motivo}")


def chequear_notif(test_id, caso, seat, esperadas):
    n = notificaciones_del_asiento(seat)
    if n is None:
        revisar(test_id, caso, "no se pudo leer GET /notifications (revisar puerto/token)")
    else:
        record(test_id, caso, f"{esperadas} notificación(es)", f"{n}", n == esperadas)


# ---------------------------------------------------------------------
# PRUEBA 9 - Reservar un asiento libre
# ---------------------------------------------------------------------
def test_9():
    seat = seat_id(SEAT_START)
    status, rid, resp = reservar(USER_1, seat)
    record("9", "POST de un asiento libre", "202", status, status == 202, resp)
    if status != 202 or not rid:
        return
    r = esperar_final(USER_1, rid)
    estado = r.get("status") if r else "sin respuesta"
    record("9", "Estado final de la reserva", "Confirmada", estado, estado == "Confirmada", r)
    ocupado = asiento_ocupado(seat)
    record("9", "Asiento queda ocupado", "occupied=true", ocupado, ocupado is True)
    chequear_notif("9", "Notificación de confirmación", seat, 1)


# ---------------------------------------------------------------------
# PRUEBA 10 - Reservar un asiento ya reservado (otro usuario)
# ---------------------------------------------------------------------
def test_10():
    seat = seat_id(SEAT_START + 1)
    s1, rid1, _ = reservar(USER_1, seat)
    r1 = esperar_final(USER_1, rid1) if rid1 else None
    e1 = r1.get("status") if r1 else "sin respuesta"
    record("10", "Primera reserva (usuario1)", "Confirmada", e1, e1 == "Confirmada", r1)

    s2, rid2, resp2 = reservar(USER_2, seat)
    record("10", "POST de la segunda reserva (usuario2)", "202", s2, s2 == 202, resp2)
    if s2 != 202 or not rid2:
        return
    r2 = esperar_final(USER_2, rid2)
    e2 = r2.get("status") if r2 else "sin respuesta"
    motivo = r2.get("reason") if r2 else None
    record("10", "Segunda reserva rechazada", "Rechazada", e2, e2 == "Rechazada", r2)
    record("10", "Motivo del rechazo", "AsientoOcupado", motivo, motivo == "AsientoOcupado")

    r1b = resultado(USER_1, rid1)
    e1b = r1b.get("status") if r1b else "sin respuesta"
    record("10", "Primera reserva sigue Confirmada", "Confirmada", e1b, e1b == "Confirmada", r1b)
    chequear_notif("10", "Una sola notificación para el asiento", seat, 1)


# ---------------------------------------------------------------------
# PRUEBA 11 - Varios asientos en solicitudes consecutivas
# ---------------------------------------------------------------------
def test_11():
    asientos = [seat_id(SEAT_START + 2 + i) for i in range(3)]
    ids = []
    for i, seat in enumerate(asientos, 1):
        status, rid, resp = reservar(USER_1, seat)
        record("11", f"POST asiento {i} de 3", "202", status, status == 202, resp)
        if rid:
            ids.append((rid, seat))
    for rid, seat in ids:
        r = esperar_final(USER_1, rid)
        estado = r.get("status") if r else "sin respuesta"
        record("11", f"Estado final {seat[-3:]}", "Confirmada", estado, estado == "Confirmada", r)
        ocupado = asiento_ocupado(seat)
        record("11", f"Asiento {seat[-3:]} ocupado", "occupied=true", ocupado, ocupado is True)

    status, mine = http("GET", AVAILABILITY_URL + "/reservations/mine", user=USER_1)
    if status == 200 and isinstance(mine, list):
        presentes = {m.get("requestId") for m in mine if m.get("status") == "Confirmada"}
        faltan = [rid for rid, _ in ids if rid not in presentes]
        record("11", "Las 3 figuran en /reservations/mine", "3 Confirmadas",
               f"faltan {len(faltan)}", len(ids) == 3 and not faltan)
    else:
        record("11", "GET /reservations/mine", "200", status, False, mine)


# ---------------------------------------------------------------------
# PRUEBA 12 - Mismo asiento dos veces, mismo usuario
# ---------------------------------------------------------------------
def test_12():
    seat = seat_id(SEAT_START + 5)
    sa, rid_a, _ = reservar(USER_1, seat)
    sb, rid_b, _ = reservar(USER_1, seat)
    record("12", "Ambos POST responden", "202 y 202", f"{sa} y {sb}", sa == 202 and sb == 202)
    if not rid_a or not rid_b:
        return
    ra = esperar_final(USER_1, rid_a)
    rb = esperar_final(USER_1, rid_b)
    estados = sorted([(ra or {}).get("status", "?"), (rb or {}).get("status", "?")])
    record("12", "Una Confirmada y una Rechazada", "Confirmada + Rechazada",
           " + ".join(estados), estados == ["Confirmada", "Rechazada"], f"{ra} | {rb}")
    rechazada = ra if (ra or {}).get("status") == "Rechazada" else rb
    motivo = (rechazada or {}).get("reason")
    record("12", "Motivo del rechazo", "AsientoOcupado", motivo, motivo == "AsientoOcupado")
    chequear_notif("12", "Una sola notificación para el asiento", seat, 1)


# ---------------------------------------------------------------------
# PRUEBA 13 - Eventos/asientos inválidos (13a-c) y pago rechazado (13d)
# ---------------------------------------------------------------------
def test_13():
    # 13a: evento inexistente (asiento válido)
    status, _, resp = reservar(USER_1, seat_id(SEAT_START + 6), event=NONEXISTENT_ID)
    record("13a", "Evento inexistente", "404", status, status == 404, resp)

    # 13b: asiento inexistente (evento válido)
    status, _, resp = reservar(USER_1, NONEXISTENT_ID)
    record("13b", "Asiento inexistente", "404", status, status == 404, resp)

    # 13c: asiento que pertenece a OTRO evento (asiento del evento 1, con el id del evento 0)
    status, _, resp = reservar(USER_1, seat_id(1, event=1))
    record("13c", "Asiento de otro evento", "404", status, status == 404, resp)

    # Ninguna de las tres debe dejar el asiento ocupado
    ocupado = asiento_ocupado(seat_id(SEAT_START + 6))
    record("13a-c", "El asiento válido sigue libre", "occupied=false", ocupado, ocupado is False)


def test_13d():
    seat = seat_id(SEAT_START + 7)
    status, rid, resp = reservar(USER_1, seat)
    record("13d", "POST con pago que será rechazado", "202", status, status == 202, resp)
    if status != 202 or not rid:
        return
    r = esperar_final(USER_1, rid)
    estado = r.get("status") if r else "sin respuesta"
    motivo = r.get("reason") if r else None
    record("13d", "Estado final", "Rechazada", estado, estado == "Rechazada", r)
    record("13d", "Motivo del rechazo", "PagoFallido", motivo, motivo == "PagoFallido")
    ocupado = asiento_ocupado(seat)
    record("13d", "El asiento queda libre", "occupied=false", ocupado, ocupado is False)
    chequear_notif("13d", "No hay notificación", seat, 0)


def main():
    global SEAT_START
    parser = argparse.ArgumentParser(description="Pruebas bloque B - Seat Reservation")
    parser.add_argument("--seat-inicial", type=int, default=1,
                        help="número del primer asiento libre del evento 0 (se usan 8 seguidos)")
    parser.add_argument("--only", help="pruebas separadas por coma, ej: 9,10,13")
    parser.add_argument("--pago-rechazado", action="store_true",
                        help="ejecuta también 13d (requiere Booking con precio alto)")
    parser.add_argument("--csv", default="resultados_bloque_B.csv")
    args = parser.parse_args()
    SEAT_START = args.seat_inicial

    tests = {"9": test_9, "10": test_10, "11": test_11, "12": test_12, "13": test_13}
    seleccion = args.only.split(",") if args.only else list(tests)

    print(f"Inicio: {datetime.now():%Y-%m-%d %H:%M:%S} | Base: {AVAILABILITY_URL} | "
          f"Asientos desde el {SEAT_START}\n")
    for n in seleccion:
        print(f"--- Prueba {n} ---")
        tests[n]()
        print()
    if args.pago_rechazado:
        print("--- Prueba 13d ---")
        test_13d()
        print()

    if not RESULTS:
        print("No se ejecutó ninguna prueba.")
        sys.exit(1)

    with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(RESULTS[0].keys()))
        w.writeheader()
        w.writerows(RESULTS)

    total = len(RESULTS)
    por = {v: sum(1 for r in RESULTS if r["veredicto"] == v) for v in ("PASS", "FAIL", "REVISAR")}
    print("=" * 60)
    print(f"Total: {total} | PASS: {por['PASS']} | FAIL: {por['FAIL']} | REVISAR: {por['REVISAR']}")
    print(f"Evidencia guardada en {args.csv}")
    sys.exit(1 if por["FAIL"] else 0)


if __name__ == "__main__":
    main()
