# Abre una ventana por servicio (modo "dotnet run"). Uso, desde seat-reservation:
#   docker compose up -d postgres keycloak
#   powershell -ExecutionPolicy Bypass -File ./scripts/levantar-servicios.ps1
$servicios = @(
    @{ Nombre = "Payment";       Proyecto = "src/Payment/Payment.Grpc";          Url = "http://localhost:5003" },
    @{ Nombre = "Notifications"; Proyecto = "src/Notifications";                 Url = "http://localhost:5004" },
    @{ Nombre = "Booking";       Proyecto = "src/Booking/Booking.Api";           Url = "http://localhost:5002" },
    @{ Nombre = "Availability";  Proyecto = "src/Availability/Availability.Api"; Url = "http://localhost:5001" }
)
foreach ($s in $servicios) {
    $comando = "`$Host.UI.RawUI.WindowTitle = '$($s.Nombre)'; dotnet run --project $($s.Proyecto) --urls $($s.Url)"
    Start-Process powershell -WorkingDirectory (Get-Location) -ArgumentList "-NoExit", "-Command", "`"$comando`""
}