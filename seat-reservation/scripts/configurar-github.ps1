# Registra GitHub como proveedor de identidad externo en el realm seat-reservation.
# Pide el Client ID y el Client Secret por consola: no los guarda en ningún archivo.
# Uso, desde la carpeta seat-reservation (con Keycloak levantado):
#   powershell -ExecutionPolicy Bypass -File ./scripts/configurar-github.ps1

$ErrorActionPreference = "Stop"
$kc    = "http://localhost:8081"
$realm = "seat-reservation"

$clientId = Read-Host "GitHub Client ID"
$sec = Read-Host "GitHub Client Secret" -AsSecureString
$clientSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))

# Token de administrador (credenciales de desarrollo del docker-compose)
$tok = Invoke-RestMethod -Method Post -Uri "$kc/realms/master/protocol/openid-connect/token" -Body @{
    grant_type = "password"; client_id = "admin-cli"; username = "admin"; password = "admin"
}
$h = @{ Authorization = "Bearer $($tok.access_token)" }

# GitHub no es OIDC completo: Keycloak trae un proveedor propio ("github") y usa el scope user:email.
$idp = @{
    alias = "github"; providerId = "github"; enabled = $true; trustEmail = $true
    firstBrokerLoginFlowAlias = "first broker login"
    config = @{
        clientId = $clientId; clientSecret = $clientSecret
        defaultScope = "user:email"; syncMode = "IMPORT"
    }
} | ConvertTo-Json -Depth 5

$url = "$kc/admin/realms/$realm/identity-provider/instances"
$existe = $true
try { Invoke-RestMethod -Headers $h -Uri "$url/github" | Out-Null } catch { $existe = $false }

if ($existe) {
    Invoke-RestMethod -Method Put -Headers $h -Uri "$url/github" -ContentType "application/json" -Body $idp | Out-Null
    Write-Host "OK  Proveedor github actualizado."
} else {
    Invoke-RestMethod -Method Post -Headers $h -Uri $url -ContentType "application/json" -Body $idp | Out-Null
    Write-Host "OK  Proveedor github creado."
}
Write-Host "Callback URL que debe estar cargada en GitHub:"
Write-Host "  $kc/realms/$realm/broker/github/endpoint"