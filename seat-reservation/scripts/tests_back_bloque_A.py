#!/usr/bin/env python3
"""
Pruebas de caja negra - Bloque A (contrato y validación de entrada)
Proyecto: Seat Reservation (back .NET, microservicios)

Solo usa la librería estándar de Python 3.8+ (no hace falta pip install).

Uso:
    python tests_back_bloque_A.py
    python tests_back_bloque_A.py --base-url http://localhost:5000 --only 3,5
    
"""

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
import urllib.parse

# =====================================================================
# CONFIG
# =====================================================================
BASE_URL = "http://localhost:5001"          
RESERVATIONS_PATH = "/reservations"         # endpoint de creación (POST)
EXTRA_HEADERS = {}                          # ej: {"Authorization": "Bearer <token>"}
TIMEOUT = 15                                # segundos

# Payload válido.
# Usá un asiento que esté LIBRE: la prueba 1 lo va a ocupar.
VALID_PAYLOAD = {
    "eventId": "11111111-1111-1111-1111-111111111111",
    "seatId": "00000000-0000-0000-0000-000000000005",
}

# Campos obligatorios (para las pruebas 3 a 7). Por defecto, todos los del payload.
REQUIRED_FIELDS = list(VALID_PAYLOAD.keys())

# Campos que referencian entidades existentes (prueba 7).
ID_FIELDS = list(VALID_PAYLOAD.keys())

# Si payload tiene campos de texto (nombre, email, comentario...), agregarlos
# acá con un valor válido: la prueba 6 también los ataca.
STRING_FIELDS = {}
# =====================================================================

OK_CREATE = (200, 201, 202)
BAD_REQUEST = (400, 422)


def send(method, path, body=None, raw=False, content_type="application/json"):
    """Hace un request y devuelve (status, texto_respuesta).
    body: objeto serializable a JSON, o str si raw=True (se manda tal cual)."""
    url = BASE_URL.rstrip("/") + path
    data = None
    if body is not None:
        data = body.encode("utf-8") if raw else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    if content_type:
        req.add_header("Content-Type", content_type)
    for k, v in EXTRA_HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # sin conexión, timeout, etc.
        return 0, f"ERROR DE CONEXION: {e}"

def get_token(username="usuario1", password="usuario1"):
    """Pide un token a Keycloak con el usuario de prueba."""
    url = "http://localhost:8081/realms/seat-reservation/protocol/openid-connect/token"
    form = urllib.parse.urlencode({
        "grant_type": "password",
        "client_id": "seat-web",
        "username": username,
        "password": password,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=form, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())["access_token"]

def evaluate(status, expected):
    if status == 0:
        return "ERROR"
    if status >= 500:
        return "FAIL"          # un 5xx siempre es bug: falta validación
    if status in expected:
        return "PASS"
    return "REVISAR"           # no es 5xx pero tampoco lo esperado


RESULTS = []


def record(test_id, name, detail, expected, status, body):
    verdict = evaluate(status, expected)
    RESULTS.append({
        "prueba": test_id,
        "caso": name,
        "detalle": detail,
        "esperado": "/".join(map(str, expected)),
        "obtenido": status,
        "veredicto": verdict,
        "respuesta": body[:300].replace("\n", " "),
    })
    icon = {"PASS": "[ OK ]", "FAIL": "[FAIL]", "REVISAR": "[ ?? ]", "ERROR": "[ERR ]"}[verdict]
    print(f"{icon} {test_id} | {name:<38} esperado={'/'.join(map(str, expected)):<8} obtenido={status}")


def payload_with(**changes):
    p = dict(VALID_PAYLOAD)
    p.update(STRING_FIELDS)
    p.update(changes)
    return p


# ---------------------------------------------------------------------
# PRUEBA 1 - Camino feliz
# ---------------------------------------------------------------------
def test_1_payload_valido():
    status, body = send("POST", RESERVATIONS_PATH, payload_with())
    record("1", "Payload válido", "POST con datos correctos", OK_CREATE, status, body)


# ---------------------------------------------------------------------
# PRUEBA 2 - Body vacío o JSON malformado
# ---------------------------------------------------------------------
def test_2_body_vacio_o_malformado():
    casos = [
        ("Sin body", None, False),
        ("String vacío", "", True),
        ("JSON malformado '{'", "{", True),
        ("Texto que no es JSON", "esto no es json", True),
        ("JSON null", "null", True),
        ("JSON array vacío []", "[]", True),
        ("Objeto vacío {}", "{}", True),
    ]
    for nombre, body, raw in casos:
        status, resp = send("POST", RESERVATIONS_PATH, body, raw=raw)
        record("2", nombre, "esperar 400, nunca 500", BAD_REQUEST, status, resp)

    # Content-Type incorrecto con body válido
    status, resp = send("POST", RESERVATIONS_PATH, json.dumps(payload_with()),
                        raw=True, content_type="text/plain")
    record("2", "Content-Type text/plain", "esperar 415 o 400", (400, 415), status, resp)


# ---------------------------------------------------------------------
# PRUEBA 3 - Campos obligatorios ausentes (uno por uno)
# ---------------------------------------------------------------------
def test_3_campos_ausentes():
    for campo in REQUIRED_FIELDS:
        p = payload_with()
        p.pop(campo, None)
        status, resp = send("POST", RESERVATIONS_PATH, p)
        record("3", f"Falta '{campo}'", f"sin el campo {campo}", BAD_REQUEST, status, resp)

    for campo in REQUIRED_FIELDS:
        status, resp = send("POST", RESERVATIONS_PATH, payload_with(**{campo: None}))
        record("3", f"'{campo}' = null", f"{campo} nulo", BAD_REQUEST, status, resp)


# ---------------------------------------------------------------------
# PRUEBA 4 - Tipos incorrectos
# ---------------------------------------------------------------------
def test_4_tipos_incorrectos():
    valores = [
        ("string", "abc"),
        ("string numérico", "12abc"),
        ("booleano", True),
        ("decimal", 1.5),
        ("array", [1, 2]),
        ("objeto", {"a": 1}),
    ]
    for campo in ID_FIELDS:
        for etiqueta, valor in valores:
            status, resp = send("POST", RESERVATIONS_PATH, payload_with(**{campo: valor}))
            record("4", f"'{campo}' = {etiqueta}", f"valor {valor!r}", BAD_REQUEST, status, resp)


# ---------------------------------------------------------------------
# PRUEBA 5 - Valores límite
# ---------------------------------------------------------------------
def test_5_valores_limite():
    limites = [
        ("0", 0),
        ("-1", -1),
        ("int.MaxValue", 2147483647),
        ("int.MaxValue+1", 2147483648),
        ("long grande", 9223372036854775807),
    ]
    # Se acepta 400 o 404 (id inválido o inexistente); lo que NO debe pasar es 2xx ni 5xx.
    for campo in ID_FIELDS:
        for etiqueta, valor in limites:
            status, resp = send("POST", RESERVATIONS_PATH, payload_with(**{campo: valor}))
            record("5", f"'{campo}' = {etiqueta}", f"valor {valor}", (400, 404, 422), status, resp)


# ---------------------------------------------------------------------
# PRUEBA 6 - Strings larguísimos y caracteres especiales
# ---------------------------------------------------------------------
def test_6_strings_raros():
    raros = [
        ("10.000 caracteres", "A" * 10000),
        ("tildes y ñ", "Ñandú café áéíóú"),
        ("emojis", "🎟️🔥😀"),
        ("comillas", "\"'`"),
        ("SQL injection", "'; DROP TABLE Reservations;--"),
        ("HTML/script", "<script>alert(1)</script>"),
        ("null byte", "abc\u0000def"),
        ("solo espacios", "     "),
    ]
    # Se ataca cada campo (los de texto declarados y también los ids, que deberían rechazarlos).
    campos = list(STRING_FIELDS.keys()) + ID_FIELDS
    for campo in campos:
        for etiqueta, valor in raros:
            status, resp = send("POST", RESERVATIONS_PATH, payload_with(**{campo: valor}))
            # Campos de texto: 2xx puede ser válido (hay que mirar que no se rompa/ni se ejecute).
            esperado = BAD_REQUEST + OK_CREATE if campo in STRING_FIELDS else BAD_REQUEST
            record("6", f"'{campo}' = {etiqueta}", "revisar eco/encoding en la respuesta",
                   esperado, status, resp)


# ---------------------------------------------------------------------
# PRUEBA 7 - Ids que no existen
# ---------------------------------------------------------------------
def test_7_ids_inexistentes():
    inexistente = "99999999-9999-9999-9999-999999999999"  # GUID válido que no existe
    for campo in ID_FIELDS:
        status, resp = send("POST", RESERVATIONS_PATH, payload_with(**{campo: inexistente}))
        record("7", f"'{campo}' inexistente", "esperar 404, sin reserva fantasma",
               (404,), status, resp)


# ---------------------------------------------------------------------
# PRUEBA 8 - Verbo HTTP incorrecto
# ---------------------------------------------------------------------
def test_8_verbo_incorrecto():
    for metodo in ("GET", "PUT", "DELETE", "PATCH"):
        body = payload_with() if metodo in ("PUT", "PATCH") else None
        status, resp = send(metodo, RESERVATIONS_PATH, body)
        # 405 es lo ideal. 404 puede ser válido si el endpoint real exige un id en la ruta.
        record("8", f"{metodo} sobre {RESERVATIONS_PATH}", "esperar 405", (405,), status, resp)


TESTS = {
    1: test_1_payload_valido,
    2: test_2_body_vacio_o_malformado,
    3: test_3_campos_ausentes,
    4: test_4_tipos_incorrectos,
    5: test_5_valores_limite,
    6: test_6_strings_raros,
    7: test_7_ids_inexistentes,
    8: test_8_verbo_incorrecto,
}


def main():
    global BASE_URL
    parser = argparse.ArgumentParser(description="Pruebas bloque A - Seat Reservation")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--only", help="números de prueba separados por coma, ej: 2,3,8")
    parser.add_argument("--csv", default="resultados_bloque_A.csv")
    args = parser.parse_args()
    BASE_URL = args.base_url
    EXTRA_HEADERS["Authorization"] = "Bearer " + get_token()

    seleccion = sorted(TESTS) if not args.only else [int(x) for x in args.only.split(",")]
    print(f"Inicio: {datetime.now():%Y-%m-%d %H:%M:%S} | Base: {BASE_URL}{RESERVATIONS_PATH}\n")

    for n in seleccion:
        print(f"--- Prueba {n} ---")
        TESTS[n]()
        print()

    with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(RESULTS[0].keys()))
        w.writeheader()
        w.writerows(RESULTS)

    total = len(RESULTS)
    por = {v: sum(1 for r in RESULTS if r["veredicto"] == v) for v in ("PASS", "FAIL", "REVISAR", "ERROR")}
    print("=" * 60)
    print(f"Total: {total} | PASS: {por['PASS']} | FAIL: {por['FAIL']} | "
          f"REVISAR: {por['REVISAR']} | ERROR: {por['ERROR']}")
    print(f"Evidencia guardada en {args.csv}")
    sys.exit(1 if por["FAIL"] or por["ERROR"] else 0)


if __name__ == "__main__":
    main()
