#!/usr/bin/env python3
"""
Pruebas de caja negra - Bloque F (seguridad y manejo de datos)
Proyecto: Seat Reservation (back .NET, microservicios)

Solo usa la librería estándar de Python 3.8+ (no hace falta pip install). Necesita tests_back_comun.py
en la misma carpeta.

Uso (desde la carpeta seat-reservation):
    python scripts/tests_back_bloque_F.py
    python scripts/tests_back_bloque_F.py --esperar-expiracion        # suma 27c (~11 min de espera)

IMPORTANTE:
  * 27d, 27e y 27i ocupan asientos de verdad: usa 3 seguidos del evento elegido. Por defecto evento 1 desde
    el asiento 16 (el bloque D usa del 1 al 15). Para repetir desde cero: docker compose down -v.
  * Se pegan directo a Booking y a Notifications con tokens de servicio de DESARROLLO (los mismos secretos
    que figuran en docker-compose.yml). Eso NO modifica datos: solo lecturas y llamadas que deben ser rechazadas.
    Nunca se llama a POST /notifications con el token del servicio autorizado (booking-service).
  * 27h usa la imagen fullstorydev/grpcurl (necesita Docker e internet la primera vez). Sin eso queda REVISAR.
  * 27c: el token vale 5 minutos (accessTokenLifespan=300) y los servicios .NET toleran 5 minutos más de
    diferencia de reloj (ClockSkew por defecto), así que un token realmente "vencido" recién es rechazado
    ~10 minutos después de emitido. Por eso es opcional.
"""

import hashlib
import hmac
import time
import uuid

from tests_back_comun import *

RUN = datetime.now().strftime("%H%M%S")
CLOCK_SKEW = 300  # segundos de tolerancia por defecto de JwtBearer


# ---------------------------------------------------------------------
# Ayudas del bloque
# ---------------------------------------------------------------------
def partes(token):
    h, p, s = token.split(".")
    return h, p, s


def reemplazar_primer_caracter(s):
    return ("A" if s[0] != "A" else "B") + s[1:]


def jwt_json(obj):
    return b64u_encode(json.dumps(obj, separators=(",", ":")).encode("utf-8"))


def tokens_invalidos(valido):
    """Devuelve [(descripción, token)] con variantes inválidas de un token válido."""
    h, p, s = partes(valido)
    payload = jwt_payload(valido)
    modificado = dict(payload)
    modificado["preferred_username"] = USER_2
    modificado["sub"] = "00000000-0000-0000-0000-000000000002"
    p_mod = jwt_json(modificado)
    h_none = jwt_json({"alg": "none", "typ": "JWT"})
    h_hs = jwt_json({"alg": "HS256", "typ": "JWT"})
    firma_hs = b64u_encode(hmac.new(b"clave-cualquiera", f"{h_hs}.{p_mod}".encode(), hashlib.sha256).digest())
    return [
        ("texto basura", "esto.no.es-un-jwt"),
        ("token mal formado (sin puntos)", "abcdef"),
        ("firma alterada", f"{h}.{p}.{reemplazar_primer_caracter(s)}"),
        ("payload alterado (usuario2) con la firma original", f"{h}.{p_mod}.{s}"),
        ("alg=none sin firma", f"{h_none}.{p_mod}."),
        ("alg=none con la firma original", f"{h_none}.{p_mod}.{s}"),
        ("HS256 firmado con una clave inventada", f"{h_hs}.{p_mod}.{firma_hs}"),
    ]


def estado_con_token(token, metodo, path, body=None):
    s, _ = http(metodo, AVAILABILITY_URL + path, body=body, token=token)
    return s


def chequear_401(tid, etiqueta, token):
    """POST /reservations, GET /reservations/{id} y GET /reservations/mine con ese token -> 401 los tres."""
    cuerpo = {"eventId": CFG.evento_id, "seatId": seat_id(CFG.seat_inicial)}
    codigos = [
        estado_con_token(token, "POST", "/reservations", cuerpo),
        estado_con_token(token, "GET", f"/reservations/{uuid.uuid4()}"),
        estado_con_token(token, "GET", "/reservations/mine"),
    ]
    record(tid, etiqueta, "401 en los 3 endpoints", codigos, all(c == 401 for c in codigos))


def matriz(base, endpoints, token, esperado):
    """Llama a cada endpoint con ese token. Devuelve (ok, lista_de_códigos)."""
    codigos = []
    for metodo, path, cuerpo in endpoints:
        s, _ = http(metodo, base + path, body=cuerpo, token=token)
        codigos.append(s)
    return all(c in esperado for c in codigos), codigos


# ---------------------------------------------------------------------
# 27a - sin token
# ---------------------------------------------------------------------
def sub_27a():
    chequear_401("27a", "Sin cabecera Authorization", None)
    # Esquema equivocado (Basic) y cabecera Bearer vacía
    cuerpo = {"eventId": CFG.evento_id, "seatId": seat_id(CFG.seat_inicial)}
    s, _ = http("POST", AVAILABILITY_URL + "/reservations", cuerpo,
                headers={"Authorization": "Basic dXN1YXJpbzE6dXN1YXJpbzE="})
    record("27a", "Authorization con esquema Basic", "401", s, s == 401)
    s, _ = http("GET", AVAILABILITY_URL + "/reservations/mine", headers={"Authorization": "Bearer "})
    record("27a", "Authorization: Bearer sin token", "401", s, s == 401)
    # Los endpoints públicos siguen siendo públicos (control)
    s, _ = http("GET", AVAILABILITY_URL + "/events")
    record("27a", "Control: GET /events sin token", "200", s, s == 200)
    s, _ = http("GET", f"{AVAILABILITY_URL}/events/{CFG.evento_id}/seats")
    record("27a", "Control: GET /events/{id}/seats sin token", "200", s, s == 200)


# ---------------------------------------------------------------------
# 27b - tokens inválidos
# ---------------------------------------------------------------------
def sub_27b():
    for desc, tok in tokens_invalidos(get_token(USER_1)):
        chequear_401("27b", f"Token inválido: {desc}", tok)


# ---------------------------------------------------------------------
# 27c - token expirado (opcional)
# ---------------------------------------------------------------------
TOKEN_VIEJO = {}


def preparar_27c(args):
    if args.esperar_expiracion:
        tok = token_nuevo(USER_1)
        TOKEN_VIEJO["token"] = tok
        TOKEN_VIEJO["exp"] = jwt_payload(tok).get("exp", time.time() + 300)
        print(f"Token para la 27c emitido; vence a las "
              f"{datetime.fromtimestamp(TOKEN_VIEJO['exp']):%H:%M:%S} (+{CLOCK_SKEW} s de tolerancia).\n")


def sub_27c(args):
    if not args.esperar_expiracion:
        revisar("27c", "Token expirado", "no ejecutada: tarda ~11 minutos. Correr con --esperar-expiracion "
                "(emite el token al empezar y lo prueba al terminar)", esperado="401")
        return
    tok, exp = TOKEN_VIEJO["token"], TOKEN_VIEJO["exp"]
    limite = exp + CLOCK_SKEW + 30
    print(f"   esperando a que el token deje de ser aceptado (hasta {datetime.fromtimestamp(limite):%H:%M:%S})...")
    s = None
    while time.time() < limite:
        s = estado_con_token(tok, "GET", "/reservations/mine")
        if s == 401:
            break
        time.sleep(15)
    record("27c", "GET /reservations/mine con un token vencido", "401", s, s == 401,
           f"se rechazó {max(0, time.time() - exp):.0f} s después del 'exp' del token")
    chequear_401("27c", "Token vencido en los 3 endpoints", tok)


# ---------------------------------------------------------------------
# 27d - solicitud de otro usuario
# ---------------------------------------------------------------------
def sub_27d():
    seat = asiento()
    s, rid, resp = reservar(USER_1, seat, correlation=f"t27d-{RUN}")
    record("27d", "usuario1 crea una reserva", "202", s, s == 202 and bool(rid), resp)
    if not rid:
        return
    s_ajena, txt_ajena, _, _ = http_completo("GET", f"{AVAILABILITY_URL}/reservations/{rid}", user=USER_2)
    s_inex, txt_inex, _, _ = http_completo("GET", f"{AVAILABILITY_URL}/reservations/{uuid.uuid4()}", user=USER_2)
    record("27d", "usuario2 consulta la solicitud de usuario1", "404", s_ajena, s_ajena == 404, txt_ajena[:150])
    record("27d", "Respuesta idéntica a la de una solicitud inexistente",
           f"{s_inex} y mismo cuerpo", f"{s_ajena}; cuerpos {'iguales' if txt_ajena == txt_inex else 'distintos'}",
           s_ajena == s_inex and txt_ajena == txt_inex, f"ajena={txt_ajena[:80]!r} inexistente={txt_inex[:80]!r}")
    mine2 = mis_reservas(USER_2)
    if mine2 is not None:
        record("27d", "La reserva no aparece en /reservations/mine de usuario2", "no aparece",
               "aparece" if any(m.get("requestId") == rid for m in mine2) else "no aparece",
               not any(m.get("requestId") == rid for m in mine2))
    r = esperar_final(USER_1, rid)
    record("27d", "El dueño sí la ve (control)", "Confirmada", estado_de(r), estado_de(r) == "Confirmada", r)


# ---------------------------------------------------------------------
# 27e - reservar a nombre de otro usuario (userId en el cuerpo)
# ---------------------------------------------------------------------
def sub_27e():
    seat = asiento()
    extra = {"userId": USER_2, "UserId": USER_2, "user_id": USER_2, "username": USER_2, "user": USER_2}
    s, rid, resp = reservar(USER_1, seat, correlation=f"t27e-{RUN}", extra=extra)
    record("27e", "POST de usuario1 con userId=usuario2 en el cuerpo", "202 (se ignora) o 400", s,
           s in (202, 400), resp)
    if s != 202 or not rid:
        return
    r = esperar_final(USER_1, rid)
    record("27e", "El dueño de la solicitud es usuario1 (consulta OK)", "200 / Confirmada", estado_de(r),
           estado_de(r) == "Confirmada", r)
    s2, _ = consultar(USER_2, rid)
    record("27e", "usuario2 NO puede ver esa solicitud", "404", s2, s2 == 404)
    f1 = booking_filas(USER_1, seat)
    f2 = booking_filas(USER_2, seat)
    if f1 is None or f2 is None:
        revisar("27e", "Booking: la reserva está a nombre de usuario1", "no se pudo consultar Booking directo")
    else:
        record("27e", "Booking: la reserva está a nombre de usuario1", "1 de usuario1 y 0 de usuario2",
               f"{len(f1)} de usuario1 y {len(f2)} de usuario2", len(f1) == 1 and len(f2) == 0)
    m1 = mis_reservas(USER_1) or []
    m2 = mis_reservas(USER_2) or []
    record("27e", "Historial: en el de usuario1 y no en el de usuario2", "usuario1 sí / usuario2 no",
           f"usuario1 {'sí' if any(m.get('requestId') == rid for m in m1) else 'no'} / "
           f"usuario2 {'sí' if any(m.get('requestId') == rid for m in m2) else 'no'}",
           any(m.get("requestId") == rid for m in m1) and not any(m.get("requestId") == rid for m in m2))


# ---------------------------------------------------------------------
# 27f - Booking directo
# ---------------------------------------------------------------------
def sub_27f():
    endpoints = [
        ("GET", f"/reservations/{uuid.uuid4()}", None),
        ("GET", f"/events/{CFG.evento_id}/occupied-seats", None),
        ("GET", f"/reservations?userId={USER_1}", None),
    ]
    for i, base in enumerate(BOOKING_URLS, 1):
        nombre = f"Booking réplica {i} ({base.rsplit(':', 1)[1]})"
        try:
            ok, cods = matriz(base, endpoints, None, (401,))
            record("27f", f"{nombre}: sin token", "401 en los 3 endpoints", cods, ok)
            ok, cods = matriz(base, endpoints, get_token(USER_1), (401, 403))
            record("27f", f"{nombre}: token de usuario (seat-web)", "401/403 en los 3", cods, ok)
            ok, cods = matriz(base, endpoints, token_servicio("booking-service"), (401, 403))
            record("27f", f"{nombre}: token de booking-service", "401/403 en los 3", cods, ok)
            # Control: el servicio autorizado sí entra (si esto falla, los 401/403 de arriba no prueban nada)
            ok, cods = matriz(base, endpoints, token_servicio("availability-service"), (200, 404))
            record("27f", f"{nombre}: control con token de availability-service", "200/404 (autorizado)", cods, ok)
        except Exception as e:
            revisar("27f", nombre, f"no se pudo pedir el token de servicio a Keycloak o conectar: {e}")


# ---------------------------------------------------------------------
# 27g - Notifications directo
# ---------------------------------------------------------------------
def sub_27g():
    cuerpo = {"ReservationId": str(uuid.uuid4()), "RequestId": str(uuid.uuid4()), "EventId": CFG.evento_id,
              "SeatId": seat_id(CFG.seat_inicial), "UserId": USER_1,
              "ConfirmedAtUtc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "CorrelationId": f"t27g-{RUN}"}
    base = NOTIFICATIONS_URL
    s, _ = http("POST", base + "/notifications", cuerpo)
    record("27g", "POST /notifications sin token", "401", s, s == 401)
    s, _ = http("POST", base + "/notifications", cuerpo, token=get_token(USER_1))
    record("27g", "POST /notifications con token de usuario (seat-web)", "401/403", s, s in (401, 403))
    s, _ = http("POST", base + "/notifications", cuerpo, token=token_servicio("availability-service"))
    record("27g", "POST /notifications con token de availability-service", "401/403", s, s in (401, 403))
    # (No se prueba con booking-service: crearía una notificación de verdad.)
    s, _ = http("GET", base + "/notifications")
    record("27g", "GET /notifications sin token", "401", s, s == 401)

    # Observación: el GET exige token pero lo ve cualquier usuario autenticado
    s, lista = http("GET", base + "/notifications", user=USER_1)
    if s == 200 and isinstance(lista, list):
        ajenas = [n for n in lista if n.get("userId") not in (None, USER_1)]
        if ajenas:
            revisar("27g", "GET /notifications devuelve notificaciones de OTROS usuarios",
                    f"con el token de usuario1 se ven {len(ajenas)} notificaciones de otros usuarios "
                    f"(ej. {ajenas[0].get('userId')}). El README lo declara como endpoint de pruebas; "
                    "en un sistema real habría que filtrar por el usuario del token",
                    esperado="solo las propias", obtenido=f"{len(ajenas)} ajenas")
        else:
            record("27g", "GET /notifications con token de usuario no muestra notificaciones ajenas", "solo las propias",
                   f"{len(lista)} notificaciones, ninguna ajena", True)


# ---------------------------------------------------------------------
# 27h - Payment (gRPC) directo, desde dentro de la red de Docker
# ---------------------------------------------------------------------
def sub_27h():
    cuerpo = {"reservation_id": str(uuid.uuid4()), "user_id": USER_1, "amount_cents": 1000,
              "correlation_id": f"t27h-{RUN}"}
    casos = [("sin token", None),
             ("token de usuario (seat-web)", get_token(USER_1)),
             ("token de availability-service", token_servicio("availability-service"))]
    for etiqueta, tok in casos:
        resp = grpc_cobrar(cuerpo, tok)
        if resp is None:
            revisar("27h", f"Payment gRPC {etiqueta}",
                    "no se pudo ejecutar grpcurl en Docker (¿Docker disponible? ¿internet para bajar fullstorydev/grpcurl?)",
                    esperado="Unauthenticated/PermissionDenied")
            return
        codigo, salida = resp
        record("27h", f"Payment gRPC {etiqueta}", "Unauthenticated / PermissionDenied", codigo,
               codigo in ("Unauthenticated", "PermissionDenied"), salida.strip().replace("\n", " ")[:150])
    n = contar_cobros([cuerpo["reservation_id"]])
    if n is not None:
        record("27h", "Ninguna de esas llamadas generó un cobro", "0", n, n == 0)


# ---------------------------------------------------------------------
# 27i - datos maliciosos
# ---------------------------------------------------------------------
PAYLOADS = [
    ("SQL clásico", "' OR '1'='1' --"),
    ("SQL destructivo", "1; DROP TABLE \"Reservations\"; --"),
    ("HTML/script", "<script>alert(1)</script>"),
    ("HTML con evento", "<img src=x onerror=alert(1)>"),
    ("plantilla/expresión", "${7*7}{{7*7}}"),
]


def veredicto_malicioso(status):
    """5xx o error de conexión = FAIL; 400/422 = esperado; otro 4xx lo dejamos pasar pero se anota."""
    return status != 0 and status < 500


def sub_27i():
    # (1) Campos con tipo Guid reciben texto malicioso -> 400 (rechazo por validación)
    for desc, p in PAYLOADS:
        s, resp = http("POST", AVAILABILITY_URL + "/reservations", {"eventId": p, "seatId": p}, user=USER_1)
        record("27i", f"POST con {desc} en eventId/seatId", "400/422 (rechazada)", s, s in (400, 422), resp)
    s, resp = http("POST", AVAILABILITY_URL + "/reservations", user=USER_1, raw="<script>alert(1)</script>")
    record("27i", "POST con cuerpo que no es JSON (HTML)", "400/415", s, s in (400, 415), resp)
    s, resp = http("POST", AVAILABILITY_URL + "/reservations", user=USER_1,
                   raw="{\"eventId\": \"" + CFG.evento_id + "\", \"seatId\": \"" + "A" * 100000 + "\"}")
    record("27i", "POST con un string de 100.000 caracteres", "400/413", s, s in (400, 413), str(resp)[:120])

    # (2) Rutas con payloads
    for desc, ruta in (("SQL en el id de la solicitud", "/reservations/%27%20OR%201%3D1%20--"),
                       ("script en el id de la solicitud", "/reservations/%3Cscript%3Ealert(1)%3C/script%3E"),
                       ("SQL en el id del evento", "/events/%27%3B%20DROP%20TABLE%20x%3B--/seats")):
        s, _ = http("GET", AVAILABILITY_URL + ruta, user=USER_1)
        record("27i", f"GET con {desc}", "404 (no 5xx)", s, s == 404)
    s, _ = http("GET", AVAILABILITY_URL + "/reservations/mine?userId=" + urllib.parse.quote("usuario2' OR '1'='1"),
                user=USER_1)
    record("27i", "GET /reservations/mine con userId malicioso en la query", "200 (se ignora; no 5xx)", s, s == 200)

    # (3) Reserva válida con campos extra y cabecera X-Correlation-Id con payloads: deben tratarse como datos
    seat = asiento()
    corr = "x' OR '1'='1' --<script>alert(1)</script>"
    extra = {"comentario": "<script>alert(1)</script>", "nota": "'; DROP TABLE \"Reservations\"; --",
             "nombre": "A" * 5000, "emoji": "\U0001F600‮\u0000"}
    s, texto, headers, _ = http_completo("POST", AVAILABILITY_URL + "/reservations",
                                         body={"eventId": CFG.evento_id, "seatId": seat, **extra}, user=USER_1,
                                         headers={"X-Correlation-Id": corr})
    record("27i", "POST válido con campos extra maliciosos y X-Correlation-Id malicioso", "202 (tratados como datos)",
           s, s == 202, texto[:200])
    if s == 202:
        try:
            resp = json.loads(texto)
        except ValueError:
            resp = {}
        tipo = headers.get("Content-Type", headers.get("content-type", ""))
        record("27i", "La respuesta es JSON (no HTML ejecutable)", "application/json", tipo.split(";")[0],
               tipo.startswith("application/json"))
        record("27i", "El correlationId se devuelve como dato, sin interpretarse", "igual al enviado",
               resp.get("correlationId", "-")[:60], resp.get("correlationId") == corr)
        rid = resp.get("requestId")
        r = esperar_final(USER_1, rid) if rid else None
        record("27i", "La reserva se procesa normalmente (toda la cadena)", "Confirmada", estado_de(r),
               estado_de(r) == "Confirmada", r)

    # (4) El sistema sigue sano: las tablas siguen existiendo y las consultas responden
    s, _ = http("GET", AVAILABILITY_URL + "/events")
    record("27i", "Después de los ataques GET /events responde", "200", s, s == 200)
    filas = booking_filas(USER_1)
    record("27i", "Después de los ataques Booking sigue respondiendo", "lista", "lista" if filas is not None else "error",
           filas is not None)
    n = sql("booking", 'SELECT count(*) FROM "Reservations"')
    if n is not None:
        record("27i", "La tabla Reservations existe (no se ejecutó el DROP)", "count >= 1", n, n.isdigit() and int(n) >= 1)


# ---------------------------------------------------------------------
# 27j - Payment no accesible desde fuera de Docker
# ---------------------------------------------------------------------
def sub_27j():
    if docker_ok():
        rc, out = compose("port", "payment", "8080")
        sin_puerto = rc != 0 or not out.strip() or "no port" in out.lower()
        record("27j", "Payment no publica ningún puerto en el host", "sin puerto publicado",
               "sin puerto" if sin_puerto else out.strip(), sin_puerto, out.strip()[:150])
        return
    # Sin Docker: se revisa el docker-compose.yml
    yml = (PROJECT_DIR / "docker-compose.yml")
    if not yml.exists():
        revisar("27j", "Payment no publica ningún puerto", "no se encontró docker-compose.yml ni Docker")
        return
    lineas = yml.read_text(encoding="utf-8").splitlines()
    dentro, hay_ports = False, False
    for ln in lineas:
        if re.match(r"^  payment:\s*$", ln):
            dentro = True
            continue
        if dentro and re.match(r"^  \S", ln):
            break
        if dentro and re.match(r"^\s+ports:\s*$", ln):
            hay_ports = True
    record("27j", "docker-compose.yml: el servicio payment no tiene 'ports'", "sin ports",
           "tiene ports" if hay_ports else "sin ports", not hay_ports,
           "verificación estática (no hay Docker disponible)")


def extra(p):
    p.add_argument("--esperar-expiracion", action="store_true",
                   help="ejecuta 27c: espera ~11 min a que un token real venza (si no, queda REVISAR)")


if __name__ == "__main__":
    # --only acepta 27 (todo) o sub-pruebas sueltas: se traduce a una lista de funciones.
    SUBS = [("27a", lambda a: sub_27a()), ("27b", lambda a: sub_27b()), ("27c", sub_27c),
            ("27d", lambda a: sub_27d()), ("27e", lambda a: sub_27e()), ("27f", lambda a: sub_27f()),
            ("27g", lambda a: sub_27g()), ("27h", lambda a: sub_27h()), ("27i", lambda a: sub_27i()),
            ("27j", lambda a: sub_27j())]
    # 27c va al final del orden de ejecución porque espera a que venza el token
    orden = [t for t in SUBS if t[0] != "27c"] + [t for t in SUBS if t[0] == "27c"]
    correr_bloque(
        "F", "Seguridad y manejo de datos",
        tests=orden,
        evento=1, seat_inicial=16,
        necesarios=lambda a: sum(1 for t in ("27d", "27e", "27i") if t in a.seleccion),
        extra_args=extra, antes=preparar_27c)
