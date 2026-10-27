# Guarda los secretos de Availability y Booking en los "user-secrets" de .NET (fuera del repositorio):
# el connection string de Azure Service Bus y el secreto de su cliente en Keycloak.
# No necesita el SDK de .NET: escribe directamente el archivo secrets.json que .NET lee.
# Uso, desde la carpeta seat-reservation:
#   powershell -ExecutionPolicy Bypass -File ./scripts/configurar-secretos.ps1

$ErrorActionPreference = "Stop"

# 1) Secretos de los clientes de Keycloak, leídos del realm exportado
$realmFile = "infra/keycloak/seat-reservation-realm.json"
if (-not (Test-Path $realmFile)) { throw "No encuentro $realmFile. Ejecutá el script desde la carpeta seat-reservation." }
$realm = Get-Content $realmFile -Raw | ConvertFrom-Json

function SecretoDe($clientId) {
    $secreto = ($realm.clients | Where-Object { $_.clientId -eq $clientId }).secret
    if (-not $secreto -or $secreto -match '^\*+$') { throw "No pude leer el secreto de $clientId en el realm exportado." }
    return $secreto
}

# 2) Connection string de Azure Service Bus (no se ve al escribir)
$segura = Read-Host "Pegá el connection string de Azure Service Bus" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($segura)
try { $serviceBus = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
$serviceBus = $serviceBus.Trim()
if ($serviceBus -notlike "Endpoint=sb://*") { throw "El connection string tiene que empezar con 'Endpoint=sb://'." }

# 3) Carpeta donde .NET busca los user-secrets
if ($env:USER_SECRETS_DIR) { $base = $env:USER_SECRETS_DIR }
elseif ($env:APPDATA)      { $base = Join-Path $env:APPDATA "Microsoft/UserSecrets" }
else                       { $base = Join-Path $HOME ".microsoft/usersecrets" }

# 4) Escribir el secrets.json de cada proyecto (conserva lo que ya tuviera)
$proyectos = @{
    "src/Availability/Availability.Api/Availability.Api.csproj" = "availability-service"
    "src/Booking/Booking.Api/Booking.Api.csproj"                 = "booking-service"
}
foreach ($p in $proyectos.GetEnumerator()) {
    $xml = [xml](Get-Content $p.Key -Raw)
    $id = @($xml.Project.PropertyGroup.UserSecretsId) | Where-Object { $_ } | Select-Object -First 1
    if (-not $id) { throw "$($p.Key) no tiene UserSecretsId. ¿Está actualizado el repositorio?" }

    $dir = Join-Path $base $id
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $archivo = Join-Path $dir "secrets.json"

    $datos = [ordered]@{}
    if (Test-Path $archivo) {
        $existente = Get-Content $archivo -Raw | ConvertFrom-Json
        if ($existente) { $existente.PSObject.Properties | ForEach-Object { $datos[$_.Name] = $_.Value } }
    }
    $datos["ServiceBus:ConnectionString"] = $serviceBus
    $datos["ServiceAuth:ClientSecret"] = SecretoDe $p.Value

    [IO.File]::WriteAllText($archivo, ($datos | ConvertTo-Json), (New-Object Text.UTF8Encoding $false))
    Write-Host "OK  $($p.Key)"
}
Write-Host "Listo. Los secretos quedaron guardados en $base, fuera del repositorio."