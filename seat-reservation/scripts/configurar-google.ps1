# Registra Google como proveedor de identidad externo en el realm seat-reservation.
# Pide el Client ID y el Client Secret por consola: no los guarda en ningún archivo.
# Uso, desde la carpeta seat-reservation (con Keycloak levantado):
#   powershell -ExecutionPolicy Bypass -File ./scripts/configurar-google.ps1

$ErrorActionPreference = "Stop"
$kc    = "http://localhost:8081"
$realm = "seat-reservation"

$clientId = Read-Host "Google Client ID"
$sec = Read-Host "Google Client Secret" -AsSecureString
$clientSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))

# Token de administrador (credenciales de desarrollo del docker-compose)
$tok = Invoke-RestMethod -Method Post -Uri "$kc/realms/master/protocol/openid-connect/token" -Body @{
    grant_type = "password"; client_id = "admin-cli"; username = "admin"; password = "admin"
}
$h = @{ Authorization = "Bearer $($tok.access_token)" }

$idp = @{
    alias = "google"; providerId = "google"; enabled = $true; trustEmail = $true
    firstBrokerLoginFlowAlias = "first broker login"
    config = @{
        clientId = $clientId; clientSecret = $clientSecret
        defaultScope = "openid profile email"; syncMode = "IMPORT"
    }
} | ConvertTo-Json -Depth 5

$url = "$kc/admin/realms/$realm/identity-provider/instances"
$existe = $true
try { Invoke-RestMethod -Headers $h -Uri "$url/google" | Out-Null } catch { $existe = $false }

if ($existe) {
    Invoke-RestMethod -Method Put -Headers $h -Uri "$url/google" -ContentType "application/json" -Body $idp | Out-Null
    Write-Host "OK  Proveedor google actualizado."
} else {
    Invoke-RestMethod -Method Post -Headers $h -Uri $url -ContentType "application/json" -Body $idp | Out-Null
    Write-Host "OK  Proveedor google creado."
}
Write-Host "Redirect URI que debe estar cargada en Google Cloud:"
Write-Host "  $kc/realms/$realm/broker/google/endpoint"