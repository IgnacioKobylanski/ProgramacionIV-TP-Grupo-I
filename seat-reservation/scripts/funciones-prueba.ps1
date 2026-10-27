# Funciones de ayuda para las pruebas. Cargar con:   . ./scripts/funciones-prueba.ps1
$EventoDemo = "11111111-1111-1111-1111-111111111111"

# Id del asiento número N (hay 20: del 1 al 10 son A1..A10 y del 11 al 20 son B1..B10)
function Seat($n) { "00000000-0000-0000-0000-" + $n.ToString("D12") }

# Asientos libres del evento de prueba (no requiere token)
function Asientos { Invoke-RestMethod "http://localhost:5001/events/$EventoDemo/seats" }

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

# Reserva un asiento con el token del usuario y espera (hasta 15 segundos) un resultado final.
# Guarda el id de la solicitud en $UltimaSolicitud para consultarla después con Resultado.
function ReservarAutenticado($seat, $user) {
    $h = @{ Authorization = "Bearer $(Token $user)" }
    $body = @{ eventId = $EventoDemo; seatId = $seat } | ConvertTo-Json
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