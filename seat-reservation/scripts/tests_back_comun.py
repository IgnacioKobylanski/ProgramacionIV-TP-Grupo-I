#!/usr/bin/env python3
"""
Utilidades compartidas por los scripts de los bloques C, D, E y F.
Proyecto: Seat Reservation (back .NET, microservicios)

No se ejecuta solo: lo importan tests_back_bloque_C.py, _D.py, _E.py y _F.py
(tienen que estar en la misma carpeta, scripts/).

Solo usa la librería estándar de Python 3.8+ (no hace falta pip install).

Qué necesita del entorno (todo sale del docker-compose.yml del repo):
  - Availability  http://localhost:5001      (API pública del sistema)
  - Booking       http://localhost:5002/5003 (las dos réplicas; se les pega directo con token de servicio)
  - Notifications http://localhost:5004
  - Keycloak      http://localhost:8081      (tokens de usuario y de servicio, secretos de DESARROLLO)
  - RabbitMQ API  http://localhost:15672     (app / app)
  - Docker        para `docker exec sr-postgres psql`, `docker compose stop/pause/logs` y grpcurl.
    Si Docker no está, los chequeos que lo necesitan se marcan REVISAR en vez de FAIL.
"""

import argparse
import base64
import csv
import hashlib
import hmac
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import types
import urllib.error
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

# =====================================================================
# CONFIG
# =====================================================================
AVAILABILITY_URL = "http://localhost:5001"
BOOKING_URLS = ["http://localhost:5002", "http://localhost:5003"]   # réplica 1 y 2
NOTIFICATIONS_URL = "http://localhost:5004"
KEYCLOAK_TOKEN_URL = "http://localhost:8081/realms/seat-reservation/protocol/openid-connect/token"
RABBIT_API = "http://localhost:15672/api"
RABBIT_AUTH = ("app", "app")
RABBIT_EXCHANGE = "grupo1-booking"
RABBIT_QUEUE = "booking"
RABBIT_DEAD_QUEUE = "booking.dead"

USER_1 = "usuario1"                                  # la contraseña es igual al usuario
USER_2 = "usuario2"
# Secretos de DESARROLLO (están en docker-compose.yml y en el realm importado).
SERVICE_CLIENTS = {
    "availability-service": "availability-service-dev-secret",
    "booking-service": "booking-service-dev-secret",
}
EVENT_IDS = {
    0: "11111111-1111-1111-1111-111111111111",       # Recital (20 asientos)
    1: "22222222-2222-2222-2222-222222222222",       # TecWeek (24 asientos)
    2: "33333333-3333-3333-3333-333333333333",       # Teatro (24 asientos)
}
NONEXISTENT_ID = "99999999-9999-9999-9999-999999999999"

POSTGRES_CONTAINER = "sr-postgres"                   # container_name del docker-compose.yml
GRPCURL_IMAGE = "fullstorydev/grpcurl:latest"
TIMEOUT = 15                                         # segundos por request HTTP
POLL_SECONDS = 25                                    # máximo esperando un estado final
FINAL_STATES = ("Confirmada", "Rechazada", "Vencida")
VALID_STATES = ("EnProceso", "Retenida", "Confirmada", "Rechazada", "Vencida")
STATE_RANK = {"EnProceso": 0, "Retenida": 1, "Confirmada": 2, "Rechazada": 2, "Vencida": 3}
# =====================================================================

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPTS_DIR.parent                     # carpeta seat-reservation (donde está el docker-compose.yml)
PROTO_DIR = PROJECT_DIR / "src" / "Contracts" / "Protos"

RESULTS = []
CFG = types.SimpleNamespace(evento=0, evento_id=EVENT_IDS[0], seat_inicial=1, siguiente=1, args=None)
_TOKENS = {}
_LOCK = threading.Lock()


# ---------------------------------------------------------------------
# Asientos
# ---------------------------------------------------------------------
def seat_id(n, event=None):
    """Id del asiento número n del evento 'event' (formato fijo del sembrado de datos)."""
    ev = CFG.evento if event is None else event
    return f"00000000-0000-0000-{ev:04d}-{n:012d}"


def asiento():
    """Devuelve el próximo asiento libre del bloque (consecutivos desde --seat-inicial)."""
    with _LOCK:
        n = CFG.siguiente
        CFG.siguiente += 1
    return seat_id(n)


def corto(seat):
    return str(seat)[-3:].lstrip("0") or "0"


# ---------------------------------------------------------------------
# JWT / tokens
# ---------------------------------------------------------------------
def b64u_decode(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def b64u_encode(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def jwt_payload(token):
    try:
        return json.loads(b64u_decode(token.split(".")[1]))
    except Exception:
        return {}


def _pedir_token(form):
    req = urllib.request.Request(KEYCLOAK_TOKEN_URL, data=urllib.parse.urlencode(form).encode("utf-8"),
                                 method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())["access_token"]


def _token_cacheado(clave, form):
    with _LOCK:
        t = _TOKENS.get(clave)
        if t and t[1] - time.time() > 30:
            return t[0]
    tok = _pedir_token(form)
    with _LOCK:
        _TOKENS[clave] = (tok, jwt_payload(tok).get("exp", time.time() + 60))
    return tok


def form_usuario(user):
    return {"grant_type": "password", "client_id": "seat-web", "username": user, "password": user}


def get_token(user):
    """Token de usuario (cliente seat-web). Se reutiliza hasta que le quedan 30 s."""
    return _token_cacheado("u:" + user, form_usuario(user))


def token_nuevo(user):
    """Token de usuario recién pedido (sin cache)."""
    return _pedir_token(form_usuario(user))


def token_servicio(client):
    """Token client_credentials de un servicio (availability-service o booking-service)."""
    return _token_cacheado("s:" + client, {
        "grant_type": "client_credentials", "client_id": client,
        "client_secret": SERVICE_CLIENTS[client]})


# ---------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------
def http_completo(method, url, body=None, user=None, token=None, headers=None, raw=None,
                  timeout=None, auth=None):
    """Devuelve (status, texto, headers_dict, segundos). status 0 = error de conexión/timeout.
    user=nombre -> Bearer con el token de ese usuario; token=string -> Bearer con ese token tal cual.
    auth=(usuario, clave) -> Basic (RabbitMQ)."""
    data = None
    if raw is not None:
        data = raw.encode("utf-8") if isinstance(raw, str) else raw
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if user:
        req.add_header("Authorization", "Bearer " + get_token(user))
    elif token:
        req.add_header("Authorization", "Bearer " + token)
    if auth:
        cred = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", "Basic " + cred)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout or TIMEOUT) as resp:
            texto = resp.read().decode("utf-8", "replace")
            return resp.status, texto, dict(resp.headers), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), dict(e.headers), time.time() - t0
    except Exception as e:
        return 0, f"ERROR DE CONEXION: {e}", {}, time.time() - t0


def http(method, url, body=None, user=None, token=None, headers=None, raw=None, timeout=None):
    """Devuelve (status, json_o_texto)."""
    status, texto, _, _ = http_completo(method, url, body, user, token, headers, raw, timeout)
    try:
        return status, json.loads(texto)
    except ValueError:
        return status, texto


# ---------------------------------------------------------------------
# API pública (Availability)
# ---------------------------------------------------------------------
def reservar(user, seat, event=None, correlation=None, extra=None, token=None):
    """POST /reservations. Devuelve (status, requestId_o_None, respuesta)."""
    body = {"eventId": event or CFG.evento_id, "seatId": seat}
    body.update(extra or {})
    headers = {"X-Correlation-Id": correlation} if correlation else None
    status, resp = http("POST", AVAILABILITY_URL + "/reservations", body, user=None if token else user,
                        token=token, headers=headers)
    rid = resp.get("requestId") if isinstance(resp, dict) else None
    return status, rid, resp


def consultar(user, rid):
    """GET /reservations/{id}. Devuelve (status, respuesta)."""
    return http("GET", f"{AVAILABILITY_URL}/reservations/{rid}", user=user)


def resultado(user, rid):
    status, resp = consultar(user, rid)
    return resp if status == 200 and isinstance(resp, dict) else None


def esperar_final(user, rid, timeout=POLL_SECONDS):
    """Consulta cada 0,5 s hasta ver un estado final. Devuelve el último dict visto (o None)."""
    ultimo = None
    fin = time.time() + timeout
    while time.time() < fin:
        r = resultado(user, rid)
        if r:
            ultimo = r
            if r.get("status") in FINAL_STATES:
                return r
        time.sleep(0.5)
    return ultimo


def estado_de(r):
    return r.get("status") if isinstance(r, dict) else "sin respuesta"


def motivo_de(r):
    return r.get("reason") if isinstance(r, dict) else None


def asientos_del_evento():
    status, resp = http("GET", f"{AVAILABILITY_URL}/events/{CFG.evento_id}/seats")
    return resp if status == 200 and isinstance(resp, list) else None


def asiento_ocupado(seat):
    """True/False según GET /events/{id}/seats; None si no se pudo consultar."""
    seats = asientos_del_evento()
    if seats is None:
        return None
    for s in seats:
        if s.get("id") == seat:
            return bool(s.get("occupied"))
    return None


def mis_reservas(user):
    status, resp = http("GET", AVAILABILITY_URL + "/reservations/mine", user=user)
    return resp if status == 200 and isinstance(resp, list) else None


# ---------------------------------------------------------------------
# Booking directo (con token de servicio) -> datos que la API pública no muestra
# ---------------------------------------------------------------------
def booking_get(path, replica=0, client="availability-service", token=None):
    tok = token if token is not None else token_servicio(client)
    return http("GET", BOOKING_URLS[replica] + path, token=tok)


def booking_filas(user_id, seat=None):
    """Reservas de un usuario según Booking (requestId, eventId, seatId, status, reason...).
    Devuelve lista, o None si no se pudo consultar."""
    try:
        status, resp = booking_get("/reservations?userId=" + urllib.parse.quote(user_id))
    except Exception:
        return None
    if status != 200 or not isinstance(resp, list):
        return None
    if seat:
        resp = [r for r in resp if str(r.get("seatId", "")).lower() == seat.lower()]
    return resp


def booking_filas_asiento(seat):
    """Todas las filas de Booking para un asiento (de usuario1 y usuario2). None si falla."""
    todas = []
    for u in (USER_1, USER_2):
        f = booking_filas(u, seat)
        if f is None:
            return None
        todas.extend(f)
    return todas


def booking_estado(rid):
    """GET /reservations/{requestId} en Booking (incluye reservationId). None si no se pudo."""
    try:
        status, resp = booking_get(f"/reservations/{rid}")
    except Exception:
        return None
    return resp if status == 200 and isinstance(resp, dict) else None


def activas(filas):
    return [f for f in filas if f.get("status") in ("Retenida", "Confirmada")]


def reservation_id_de(rid):
    e = booking_estado(rid)
    return e.get("reservationId") if e else None


# ---------------------------------------------------------------------
# Docker / Postgres / logs / grpcurl
# ---------------------------------------------------------------------
def run(cmd, timeout=180):
    """Ejecuta un comando. Devuelve (código, salida). 127 = no existe, 124 = timeout."""
    try:
        p = subprocess.run(cmd, cwd=str(PROJECT_DIR), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return 127, "comando no encontrado: " + str(cmd[0])
    except subprocess.TimeoutExpired:
        return 124, "timeout ejecutando: " + " ".join(cmd)


_DOCKER = {}


def docker_ok():
    """True si 'docker compose' funciona desde la carpeta del proyecto."""
    if "ok" not in _DOCKER:
        if not shutil.which("docker"):
            _DOCKER["ok"] = False
        else:
            rc, _ = run(["docker", "compose", "version"], timeout=30)
            _DOCKER["ok"] = rc == 0
    return _DOCKER["ok"]


def compose(*args, timeout=180):
    return run(["docker", "compose"] + list(args), timeout=timeout)


def sql(base, consulta):
    """Ejecuta una consulta en una base de Postgres (booking/payment/notifications). Devuelve texto o None."""
    if not docker_ok():
        return None
    rc, out = run(["docker", "exec", POSTGRES_CONTAINER, "psql", "-U", "app", "-d", base,
                   "-t", "-A", "-c", consulta], timeout=60)
    return out.strip() if rc == 0 else None


def _lista_sql(ids):
    return ",".join("'" + str(i) + "'" for i in ids)


def contar_cobros(reservation_ids):
    """Cantidad de filas en Payments para esas reservas. None si no se pudo consultar."""
    ids = [i for i in reservation_ids if i]
    if not ids:
        return None
    out = sql("payment", f'SELECT count(*) FROM "Payments" WHERE "ReservationId" IN ({_lista_sql(ids)})')
    return int(out) if out and out.isdigit() else None


def contar_notificaciones(seat, reservation_ids=None):
    """Cantidad de notificaciones de esas reservas (por SQL) o, si no hay Docker, las que mencionan
    el asiento en GET /notifications (solo trae las últimas 50). None si no se pudo."""
    ids = [i for i in (reservation_ids or []) if i]
    if ids:
        out = sql("notifications", f'SELECT count(*) FROM "Notifications" WHERE "ReservationId" IN ({_lista_sql(ids)})')
        if out and out.isdigit():
            return int(out)
    status, resp = http("GET", NOTIFICATIONS_URL + "/notifications", user=USER_1)
    if status != 200 or not isinstance(resp, list):
        return None
    if ids:
        return sum(1 for n in resp if str(n.get("reservationId", "")).lower() in [i.lower() for i in ids])
    return sum(1 for n in resp if seat in str(n.get("message", "")))


def logs_de(servicio, desde=None):
    """Texto de 'docker compose logs' de un servicio (todas las réplicas). None si no hay Docker."""
    if not docker_ok():
        return None
    rc, out = compose("logs", "--no-color", servicio, timeout=120)
    return out if rc == 0 else None


def red_docker():
    rc, out = run(["docker", "inspect", "-f",
                   "{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}", POSTGRES_CONTAINER], timeout=30)
    nombres = out.split() if rc == 0 else []
    return nombres[0] if nombres else None


def grpc_cobrar(request_json, token=None):
    """Llama a Payment.ChargeReservation desde DENTRO de la red de Docker usando grpcurl (en un contenedor
    descartable). Devuelve (codigo_grpc, salida) o None si no se pudo ejecutar."""
    if not docker_ok():
        return None
    red = red_docker()
    if not red:
        return None
    cmd = ["docker", "run", "--rm", "--network", red, "-v", f"{PROTO_DIR}:/protos:ro", GRPCURL_IMAGE,
           "-plaintext", "-import-path", "/protos", "-proto", "payment.proto"]
    if token:
        cmd += ["-H", "authorization: Bearer " + token]
    cmd += ["-d", json.dumps(request_json), "payment:8080", "payment.PaymentProcessor/ChargeReservation"]
    rc, out = run(cmd, timeout=240)
    m = re.search(r"Code:\s*(\w+)", out)
    if m:
        return m.group(1), out
    if rc == 0:
        return "OK", out
    return None


# ---------------------------------------------------------------------
# RabbitMQ (API de gestión)
# ---------------------------------------------------------------------
def rabbit(method, path, body=None):
    status, texto, _, _ = http_completo(method, RABBIT_API + path, body=body, auth=RABBIT_AUTH, timeout=10)
    try:
        return status, json.loads(texto)
    except ValueError:
        return status, texto


def rabbit_cola(nombre):
    """Dict con messages / messages_ready / messages_unacknowledged / consumers, o None."""
    status, resp = rabbit("GET", "/queues/%2F/" + urllib.parse.quote(nombre, safe=""))
    return resp if status == 200 and isinstance(resp, dict) else None


def rabbit_publicar(payload, message_id=None):
    """Publica un texto en el exchange de Booking. True si el broker lo ruteó a alguna cola."""
    props = {"delivery_mode": 2, "content_type": "application/json"}
    if message_id:
        props["message_id"] = str(message_id)
    status, resp = rabbit("POST", "/exchanges/%2F/" + RABBIT_EXCHANGE + "/publish", {
        "properties": props, "routing_key": "", "payload": payload, "payload_encoding": "string"})
    return status == 200 and isinstance(resp, dict) and resp.get("routed") is True


def esperar_cola(nombre, condicion, segundos=30):
    """Espera (las estadísticas de RabbitMQ se refrescan cada ~5 s) hasta que condicion(cola) sea verdadera.
    Devuelve el último dict leído (o None)."""
    fin = time.time() + segundos
    ultimo = None
    while time.time() < fin:
        q = rabbit_cola(nombre)
        if q is not None:
            ultimo = q
            if condicion(q):
                return q
        time.sleep(1)
    return ultimo


def mensaje_reserva(rid, seat, user, correlacion):
    """Mensaje con la misma forma que publica Availability (ReservationRequestedMessage)."""
    return json.dumps({
        "RequestId": rid, "EventId": CFG.evento_id, "SeatId": seat, "UserId": user,
        "RequestedAtUtc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "CorrelationId": correlacion})


# ---------------------------------------------------------------------
# Concurrencia
# ---------------------------------------------------------------------
def disparar_simultaneo(tareas):
    """Ejecuta las funciones (sin argumentos) en hilos, todas arrancando a la vez (Barrier).
    Devuelve la lista de resultados en el mismo orden."""
    barrera = threading.Barrier(len(tareas))

    def envuelta(f):
        def corre():
            barrera.wait()
            return f()
        return corre

    with ThreadPoolExecutor(max_workers=len(tareas)) as pool:
        futuros = [pool.submit(envuelta(f)) for f in tareas]
        return [f.result() for f in futuros]


# ---------------------------------------------------------------------
# Registro de resultados
# ---------------------------------------------------------------------
def record(test_id, caso, esperado, obtenido, ok, detalle=""):
    verdict = "PASS" if ok else "FAIL"
    RESULTS.append({
        "prueba": test_id, "caso": caso, "esperado": str(esperado),
        "obtenido": str(obtenido), "veredicto": verdict, "detalle": str(detalle)[:400],
    })
    icon = "[ OK ]" if ok else "[FAIL]"
    print(f"{icon} {test_id} | {caso:<52} esperado={esperado} | obtenido={obtenido}")
    sys.stdout.flush()


def revisar(test_id, caso, motivo, esperado="-", obtenido="-"):
    """Chequeo que no se pudo hacer, o resultado que hay que mirar a mano."""
    RESULTS.append({
        "prueba": test_id, "caso": caso, "esperado": str(esperado), "obtenido": str(obtenido),
        "veredicto": "REVISAR", "detalle": str(motivo)[:400],
    })
    print(f"[ ?? ] {test_id} | {caso:<52} {motivo}")
    sys.stdout.flush()


def comprimir(estados):
    """['EnProceso','EnProceso','Retenida'] -> ['EnProceso','Retenida']"""
    out = []
    for e in estados:
        if not out or out[-1] != e:
            out.append(e)
    return out


def secuencia_valida(estados):
    """Los estados nunca retroceden y, una vez final, no cambian."""
    ultimo = -1
    final = None
    for e in estados:
        if e not in STATE_RANK:
            return False
        if final is not None and e != final:
            return False
        if STATE_RANK[e] < ultimo:
            return False
        ultimo = STATE_RANK[e]
        if e in FINAL_STATES:
            final = e
    return True


# ---------------------------------------------------------------------
# Runner de bloque
# ---------------------------------------------------------------------
def verificar_asientos(cantidad):
    """Aborta si los asientos que va a usar el bloque no existen o ya están ocupados."""
    seats = asientos_del_evento()
    if seats is None:
        print("No se pudo leer GET /events/{id}/seats (¿está levantado el sistema? ¿Booking responde?).")
        sys.exit(2)
    por_id = {s["id"]: s for s in seats}
    ocupados = []
    for i in range(cantidad):
        sid = seat_id(CFG.seat_inicial + i)
        s = por_id.get(sid)
        if s is None:
            print(f"El asiento {CFG.seat_inicial + i} no existe en el evento {CFG.evento} "
                  f"(tiene {len(seats)} asientos). Usá otro --evento o un --seat-inicial más bajo.")
            sys.exit(2)
        if s.get("occupied"):
            ocupados.append(CFG.seat_inicial + i)
    if ocupados:
        libres = sorted(int(s["id"][-12:]) for s in seats if not s.get("occupied"))
        sugerido = None
        for n in libres:
            if all((n + k) in libres for k in range(cantidad)):
                sugerido = n
                break
        print(f"Estos asientos ya están ocupados: {ocupados}. Las pruebas necesitan {cantidad} asientos "
              f"libres seguidos desde --seat-inicial {CFG.seat_inicial} (evento {CFG.evento}).")
        if sugerido:
            print(f"Sugerencia: --seat-inicial {sugerido}   (o limpiar con: docker compose down -v y volver a levantar)")
        else:
            print("No quedan tantos asientos libres seguidos: probá otro --evento o limpiá con docker compose down -v.")
        sys.exit(2)


def correr_bloque(bloque, titulo, tests, evento, seat_inicial, necesarios, extra_args=None,
                  requiere_docker=False, antes=None, despues=None, notas=""):
    """Arma los argumentos comunes, verifica los asientos, corre las pruebas y guarda el CSV.
    tests: lista ordenada de (id, funcion(args)).  necesarios: funcion(args) -> cantidad de asientos."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ids = [t[0] for t in tests]
    p = argparse.ArgumentParser(description=f"Pruebas bloque {bloque} - {titulo} - Seat Reservation")
    p.add_argument("--evento", type=int, choices=(0, 1, 2), default=evento,
                   help=f"evento a usar (0=Recital 20 asientos, 1=TecWeek 24, 2=Teatro 24). Por defecto {evento}")
    p.add_argument("--seat-inicial", type=int, default=seat_inicial,
                   help=f"número del primer asiento libre a usar. Por defecto {seat_inicial}")
    p.add_argument("--only", help="pruebas separadas por coma. Disponibles: " + ",".join(ids))
    p.add_argument("--csv", default=f"resultados_bloque_{bloque}.csv", help="archivo de evidencia")
    p.add_argument("--no-verificar-asientos", action="store_true",
                   help="no comprobar antes que los asientos estén libres")
    if extra_args:
        extra_args(p)
    args = p.parse_args()

    CFG.evento = args.evento
    CFG.evento_id = EVENT_IDS[args.evento]
    CFG.seat_inicial = args.seat_inicial
    CFG.siguiente = args.seat_inicial
    CFG.args = args

    seleccion = [s.strip() for s in args.only.split(",")] if args.only else ids
    desconocidas = [s for s in seleccion if s not in ids]
    if desconocidas:
        print(f"Prueba(s) desconocida(s): {desconocidas}. Disponibles: {ids}")
        sys.exit(2)

    if requiere_docker and not docker_ok():
        print("Este bloque necesita Docker (docker compose stop/pause/start). No se encontró 'docker compose'.")
        sys.exit(2)

    args.seleccion = seleccion       # las funciones 'necesarios' cuentan solo los asientos de las pruebas elegidas
    cant = necesarios(args)
    print(f"Inicio: {datetime.now():%Y-%m-%d %H:%M:%S} | Bloque {bloque} - {titulo}")
    print(f"Availability: {AVAILABILITY_URL} | evento {CFG.evento} | asientos desde el {CFG.seat_inicial} "
          f"(hasta {cant} asientos)")
    if notas:
        print(notas)
    print()
    if not args.no_verificar_asientos:
        verificar_asientos(cant)
    if not docker_ok():
        print("(Docker no disponible: los chequeos de base de datos/logs se marcarán REVISAR)\n")

    try:
        if antes:
            antes(args)
        for tid, fn in tests:
            if tid not in seleccion:
                continue
            print(f"--- Prueba {tid} ---")
            try:
                fn(args)
            except KeyboardInterrupt:
                raise
            except Exception as e:  # un error del script no debe cortar las demás pruebas
                record(tid, "Excepción en el script", "sin excepción", type(e).__name__, False,
                       traceback.format_exc().replace("\n", " | "))
            print()
    finally:
        if despues:
            print("Restaurando el entorno...")
            despues(args)

    if not RESULTS:
        print("No se ejecutó ninguna prueba.")
        sys.exit(1)

    with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(RESULTS[0].keys()))
        w.writeheader()
        w.writerows(RESULTS)

    por = {v: sum(1 for r in RESULTS if r["veredicto"] == v) for v in ("PASS", "FAIL", "REVISAR")}
    print("=" * 70)
    print(f"Total: {len(RESULTS)} | PASS: {por['PASS']} | FAIL: {por['FAIL']} | REVISAR: {por['REVISAR']}")
    print(f"Evidencia guardada en {args.csv}")
    sys.exit(1 if por["FAIL"] else 0)
