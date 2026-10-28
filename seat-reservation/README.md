# Sistema de reserva de asientos

TP grupal de Programación IV (UTN), Grupo 1. Sistema de microservicios en .NET 10 para reservar asientos de eventos, con consistencia eventual entre servicios.

> Todos los comandos de este documento se ejecutan desde la carpeta `seat-reservation`.

## Arquitectura

```mermaid
graph TD
    U([Usuario]) -->|consulta y reserva| A[Availability<br/>Clean Architecture]
    A -->|PUBLISH| S[(Azure Service Bus<br/>topic)]
    S -->|SUBSCRIBE| B[Booking<br/>N-Layer]
    A -->|GET estado y asientos ocupados| B
    B -->|gRPC| P[Payment<br/>N-Layer]
    B -->|HTTP al confirmar| N[Notifications]
    A -.->|pide token| K[Keycloak<br/>Authorization Server]
    B -.->|pide token| K
    P -.->|valida tokens| K
    N -.->|valida tokens| K
    A --> DA[(BD Availability)]
    B --> DB[(BD Booking)]
    P --> DP[(BD Payment)]
    N --> DN[(BD Notifications)]
```

| Servicio | Estilo | Puerto | Rol |
|---|---|---|---|
| Availability | Clean Architecture, dominio anémico | 5001 | Consulta de eventos y asientos libres; recibe la solicitud de reserva y la publica en el broker |
| Booking | N-Layer, dominio anémico | 5002 | Consume del broker, retiene el asiento, cobra a Payment y confirma o rechaza; vence reservas |
| Payment | N-Layer (gRPC), dominio anémico | 5003 | Cobro simulado e idempotente |
| Notifications | API mínima | 5004 | Aviso (simulado) cuando una reserva queda confirmada |
| Keycloak | Servidor de autorización | 8081 | Emite los tokens de usuarios y de servicios |
| PostgreSQL | Una base por servicio | 5432 | Persistencia |
| Azure Service Bus | Topic `grupo1-booking-topic`, suscripción `booking` | - | Broker entre Availability y Booking |

**Consistencia eventual.** Availability responde "solicitud recibida" (202) apenas publica el mensaje, sin esperar el resultado. Entre ese momento y la decisión de Booking, el estado de la solicitud se ve como `EnProceso`.

**Estados de una reserva:** Retenida, Confirmada, Rechazada (asiento ocupado, pago fallido o pago no disponible) y Vencida. Un asiento está ocupado mientras su reserva esté Retenida o Confirmada.

## Requisitos

- Git, .NET SDK 10 y Docker Desktop (abierto).
- PowerShell (en Windows ya viene; en Mac o Linux, PowerShell 7 con el comando `pwsh` en lugar de `powershell`).
- El connection string de Azure Service Bus del grupo. **No está en el repositorio**: se entrega aparte.

## Cómo ejecutarlo

1. Clonar el repositorio (`git clone <URL_DEL_REPO>`) y entrar a la carpeta `seat-reservation`.
2. Abrir Docker Desktop y esperar a que esté corriendo.
3. Levantar la infraestructura (PostgreSQL y Keycloak). Tarda un par de minutos la primera vez; Keycloak carga solo el realm `seat-reservation` (clientes y usuarios de prueba):

   ```powershell
   docker compose up -d
   ```

4. Guardar los secretos (una sola vez). El script pide el connection string y lo guarda con `dotnet user-secrets`, fuera del repositorio. Los secretos de los clientes de Keycloak los lee del realm exportado:

   ```powershell
   powershell -ExecutionPolicy Bypass -File ./scripts/configurar-secretos.ps1
   ```

5. Levantar los cuatro servicios (abre una ventana por cada uno). Esperar a que todas muestren `Application started`:

   ```powershell
   powershell -ExecutionPolicy Bypass -File ./scripts/levantar-servicios.ps1
   ```

6. Cargar las funciones de prueba (hay un punto y un espacio al principio):

   ```powershell
   . ./scripts/funciones-prueba.ps1
   ```

Para apagar todo: cerrar las cuatro ventanas y `docker compose down`. Para borrar además las bases y la configuración de Keycloak y empezar de cero, `docker compose down -v`.

**Credenciales de desarrollo** (no hay datos reales): PostgreSQL `app` / `app`; panel de Keycloak (`http://localhost:8081`) `admin` / `admin`; usuarios de prueba `usuario1` y `usuario2`, con la contraseña igual al nombre de usuario.

## Probar el flujo

Hay 20 asientos, del 1 al 10 (A1 a A10) y del 11 al 20 (B1 a B10).

### Flujo feliz

```powershell
Asientos                                          # asientos libres (no pide token)
ReservarAutenticado (Seat 5) "usuario1"           # Confirmada
Asientos                                          # el asiento 5 ya no aparece
Invoke-RestMethod http://localhost:5004/notifications -Headers @{ Authorization = "Bearer $(Token 'usuario1')" }
```

Las consolas de los servicios muestran líneas `AUDITORIA` con el mismo `CorrelationId` a lo largo de toda la cadena.

### Flujos de fallo

**Asiento ocupado:**

```powershell
ReservarAutenticado (Seat 5) "usuario2"           # Rechazada / AsientoOcupado
```

**Falta un componente: Payment caído.** Cerrar la ventana de Payment y:

```powershell
ReservarAutenticado (Seat 6) "usuario1"           # Rechazada / PagoNoDisponible
Asientos                                          # el asiento 6 sigue libre
```

Volver a abrir Payment (`dotnet run --project src/Payment/Payment.Grpc --urls http://localhost:5003`) y repetir con el mismo asiento: `Confirmada`. Si la primera llamada responde `Retenida`, consultar de nuevo con `Resultado $UltimaSolicitud "usuario1"`: tras reiniciar Payment, la primera llamada tarda unos segundos más.

**Falta un componente: Booking caído.** Cerrar la ventana de Booking y:

```powershell
ReservarAutenticado (Seat 7) "usuario1"           # la solicitud se acepta, pero la consulta responde 503
```

Volver a abrir Booking (`dotnet run --project src/Booking/Booking.Api --urls http://localhost:5002`) y, unos segundos después:

```powershell
Resultado $UltimaSolicitud "usuario1"             # Confirmada: el broker había guardado el mensaje
```

**Notifications caído:** cerrar su ventana y reservar otro asiento. La reserva queda `Confirmada` igual; Booking registra el aviso fallido en su consola.

**Autenticación:**

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5001/reservations -ContentType "application/json" -Body (@{ eventId = $EventoDemo; seatId = (Seat 8) } | ConvertTo-Json)   # 401 sin token
Invoke-RestMethod http://localhost:5002/reservations/$([guid]::NewGuid()) -Headers @{ Authorization = "Bearer $(Token 'usuario1')" }   # 403: el token es de un usuario, no de availability-service
```

Para liberar todos los asientos y repetir las pruebas:

```powershell
@'
TRUNCATE "Reservations";
'@ | docker compose exec -T postgres psql -U app -d booking
```

### Réplicas de Booking

Con el sistema corriendo, abrir una segunda instancia de Booking en otro puerto (las dos escuchan la misma suscripción, y el broker entrega cada mensaje a una sola):

```powershell
dotnet run --project src/Booking/Booking.Api --urls http://localhost:5012
```

Y mandar varias reservas seguidas (usan los asientos 1 a 4):

```powershell
$h = @{ Authorization = "Bearer $(Token 'usuario1')" }
1..4 | ForEach-Object {
    $body = @{ eventId = $EventoDemo; seatId = (Seat $_) } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri http://localhost:5001/reservations -Headers $h -ContentType "application/json" -Body $body | Out-Null
}
```

En las consolas de las dos instancias aparecen líneas `AUDITORIA inicio reserva` repartidas entre ambas.

> **Importante:** si dos personas tienen Booking conectado al mismo topic al mismo tiempo (en máquinas distintas), el broker reparte los mensajes entre ellos y la reserva de uno la procesa el otro. Mientras se evalúa, que haya un solo Booking (o las réplicas de una misma máquina).

## Decisiones de diseño

- **Una base de datos por servicio** (en un mismo servidor PostgreSQL para desarrollo). Los servicios solo se vinculan por identificadores.
- **Un asiento solo puede tener una reserva activa:** lo garantiza un índice único parcial en la base de Booking. Es control de concurrencia optimista, sin lock distribuido: el que llega segundo recibe una violación de unicidad y se rechaza por asiento ocupado.
- **Idempotencia:** cada solicitud se procesa una sola vez (índice único por `RequestId`) y el cobro se hace una sola vez por reserva. El mensaje se confirma al broker solo después de procesarlo.
- **Payment es una simulación:** aprueba si el monto es mayor que 0 y no supera un máximo configurable. Booking le pone un plazo de 5 segundos; si no responde, la reserva se rechaza por "pago no disponible".
- **Notifications** no figura en el diagrama oficial (punto h): Booking la llama por HTTP solo al confirmar, sin pasar por el broker. Si Notifications falla, la reserva se confirma igual (degradación elegante).
- **Autenticación (punto e):** Keycloak emite los tokens. Para reservar hace falta el token de un usuario y Availability toma el usuario del token, no del pedido. Entre servicios se usa el flujo *client credentials*: Booking acepta solo a `availability-service`; Payment y Notifications aceptan solo a `booking-service`.
- **Auditoría (punto f):** cada servicio registra el inicio y el fin de su parte de la cadena con un `CorrelationId` común.
- La configuración de Keycloak se exporta a `seat-reservation/infra/keycloak/seat-reservation-realm.json` y se importa sola al primer arranque.

## Limitaciones conocidas

- Los tokens se validan por firma, emisor y vigencia; no se valida la audiencia.
- El login con un proveedor de identidad externo que muestra el diagrama no está configurado en esta entrega.
- Si Notifications está caído justo al confirmar, ese aviso se pierde (no hay reintento; la solución sería un patrón Outbox).
- Si una reserva vence mientras Payment responde, el cobro aprobado no se compensa con un reembolso.
- Keycloak y la validación de tokens funcionan sin HTTPS: es una configuración solo para desarrollo local.
- La solicitud se guarda en Availability antes de publicarse. Si la publicación falla, queda registrada sin mensaje y el usuario puede reintentar.

## Estructura del repositorio

```text
seat-reservation/
├── docker-compose.yml        # PostgreSQL y Keycloak
├── infra/
│   ├── postgres/init.sql     # una base por servicio
│   └── keycloak/seat-reservation-realm.json
├── scripts/                  # secretos, ejecución y funciones de prueba
├── docs/                     # documentación del grupo
└── src/
    ├── Availability/         # Domain, Application, Infrastructure, Api
    ├── Booking/              # Api, Business, DataAccess, Entities
    ├── Payment/              # Grpc, Business, DataAccess, Entities
    ├── Notifications/        # API mínima
    ├── Contracts/            # mensaje del broker y contrato gRPC
    └── Shared/ServiceAuth/   # token entre servicios y validación con Keycloak
```

## Documentación

En `seat-reservation/docs/`: tabla de componentes, diagrama general, diagramas de arquitectura de cada API, decisiones de diseño y los historiales de prompts de cada integrante (`docs/prompts/`).
