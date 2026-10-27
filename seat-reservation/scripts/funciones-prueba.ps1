# Funciones de ayuda para las pruebas. Cargar con:   . ./scripts/funciones-prueba.ps1
# Eventos de prueba: 0 = Recital (20 asientos), 1 = Conferencia (24), 2 = Obra de teatro (24)
$IdsEvento = @{
    0 = "11111111-1111-1111-1111-111111111111"
    1 = "22222222-2222-2222-2222-222222222222"
    2 = "33333333-3333-3333-3333-333333333333"
}
$EventoDemo = $IdsEvento[0]

# Lista de eventos (no requiere token)
function Eventos { Invoke-RestMethod http://localhost:5001/events }

# Id del asiento número N del evento E (por defecto, el evento 0)
function Seat($n, $e = 0) { "00000000-0000-0000-" + $e.ToString("D4") + "-" + $n.ToString("D12") }

# Asientos libres del evento E (no requiere token)
function Asientos($e = 0) { Invoke-RestMethod "http://localhost:5001/events/$($IdsEvento[$e])/seats" }

# Token de un usuario de prueba (usuario1 o usuario2; la contraseña es igual al usuario)
function Token($user) {
    (Invoke-RestMethod -Method Post -Uri "http://localhost:8081/realms/seat-reservation/protocol/openid-connect/token" `
        -ContentType "application/x-www-form-urlencoded" `
        -Body @{ grant_type = "password"; client_id = "seat-web"; username = $user; password = $user }).access_token
}

# Consulta el resultado de una solicitud (solo la puede ver quien la hizo)
function Resultado($requestId, $user) {
    Invoke-RestMethod "http://localhost:5001/reservations/$requestId" -Headers @{ Authorization = "Bearer $(Token $user)" }
}

# Reserva un asiento del evento E con el token del usuario y espera (hasta 15 segundos) un resultado final.
# Guarda el id de la solicitud en $UltimaSolicitud para consultarla después con Resultado.
function ReservarAutenticado($seat, $user, $e = 0) {
    $h = @{ Authorization = "Bearer $(Token $user)" }
    $body = @{ eventId = $IdsEvento[$e]; seatId = $seat } | ConvertTo-Json
    $r = Invoke-RestMethod -Method Post -Uri http://localhost:5001/reservations -Headers $h -ContentType "application/json" -Body $body
    $global:UltimaSolicitud = $r.requestId

    $res = $null
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Milliseconds 500
        $res = Invoke-RestMethod "http://localhost:5001/reservations/$($r.requestId)" -Headers $h
        if ($res.status -notin "EnProceso", "Retenida") { break }
    }
    $res
}