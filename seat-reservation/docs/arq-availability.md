# Arquitectura de Availability

Availability permite consultar eventos y asientos disponibles, registrar solicitudes de reserva y consultar su resultado. Booking decide si el asiento puede reservarse y mantiene el estado de la reserva.

## Componentes y dependencias

El nodo sigue Clean Architecture: `Availability.Api` expone los endpoints; `Availability.Application` contiene `AvailabilityService`, que orquesta los casos de uso; `Availability.Domain` define las entidades de datos; y `Availability.Infrastructure` implementa la persistencia y las integraciones externas.

- **PostgreSQL:** la base propia `availability` almacena `Event`, `Seat` y `ReservationRequest`. No almacena la ocupación ni el estado de las reservas de Booking.
- **Booking:** se consulta por HTTP para obtener los asientos ocupados y el estado de una solicitud.
- **Azure Service Bus:** Availability publica solicitudes en el topic configurado (`grupo1-booking-topic`); Booking las consume desde la suscripción `booking`.
- **Keycloak:** emite los tokens de usuario y los tokens de servicio utilizados para llamar a Booking.

Availability no consume mensajes de resultado del broker. Consulta el estado en Booking cuando el usuario lo solicita.

## Guía de inicio

Se requiere .NET SDK 10, Docker Desktop con PostgreSQL y Keycloak levantados, y la configuración de `ServiceBus:ConnectionString` y `ServiceAuth:ClientSecret` mediante user-secrets u otro proveedor de configuración. También deben existir el topic y la suscripción del broker. Para consultar asientos y resultados, Booking debe estar disponible en la URL configurada.

Desde la carpeta `seat-reservation`, levantar los contenedores y ejecutar la API:

```powershell
docker compose up -d
dotnet run --project src/Availability/Availability.Api --urls http://localhost:5237
```

Al iniciar, la API aplica las migraciones de su base y, si no hay eventos, crea un evento de demostración con 20 asientos.

> Esta guía refleja la configuración actual. `referencia-del-plan.md` todavía indica el puerto 5001 y una cola `reservation-requests`, en lugar del puerto 5237 y el topic utilizados actualmente.

## Autenticación y autorización

Las consultas de eventos y asientos son públicas. Crear una solicitud y consultar su resultado requiere un token Bearer válido emitido por Keycloak. Availability verifica firma, emisor y vigencia; en la configuración actual no valida la audiencia (`aud`). No guarda contraseñas ni emite tokens.

El usuario se obtiene del claim `preferred_username` o, si no está presente, de `sub`. Si falta un token válido o no puede obtenerse el identificador del usuario, los endpoints protegidos responden **401 Unauthorized**. El usuario no se recibe en el cuerpo de la solicitud.

Para las dos consultas HTTP a Booking, Availability obtiene de Keycloak un token propio mediante `client_credentials`, identificándose como `availability-service`. El token se reutiliza hasta poco antes de vencer y se agrega a las llamadas salientes. Esto también ocurre cuando la consulta de asientos proviene de un usuario sin iniciar sesión.

## Resumen de endpoints

| Método | Ruta | Acceso | Función | Respuestas principales |
| --- | --- | --- | --- | --- |
| GET | `/events` | Público | Listar eventos. | 200 |
| GET | `/events/{eventId:guid}/seats` | Público | Listar asientos disponibles de un evento. | 200, 404, 503 |
| POST | `/reservations` | Autenticado | Registrar y publicar una solicitud de reserva. | 202, 401, 404, 503 |
| GET | `/reservations/{requestId:guid}` | Autenticado | Consultar el estado de una solicitud propia. | 200, 401, 404, 503 |

## Flujo de cada endpoint

### GET `/events`

La API llama a `AvailabilityService`, que consulta los eventos mediante el repositorio de la base local. Devuelve una lista de `EventDto` con `Id`, `Name` y `DateUtc`, ordenada por fecha.

Responde **200 OK**, incluso si la lista está vacía. No incluye asientos ni filtra eventos según su disponibilidad.

### GET `/events/{eventId:guid}/seats`

1. Verifica que el evento exista en la base local. Si no existe, responde **404 Not Found**.
2. Obtiene los asientos del evento desde la base local.
3. Consulta a Booking mediante `GET /events/{eventId}/occupied-seats`. Booking considera ocupados los asientos con reservas `Retenida` o `Confirmada`.
4. Excluye los ocupados y devuelve los disponibles, ordenados por etiqueta, como una lista de `SeatDto` con `Id` y `Label`.

Responde **200 OK** con la lista, incluso si no hay asientos disponibles (`[]`). Si la consulta a Booking propaga `HttpRequestException`, responde **503 Service Unavailable**.

Por la consistencia eventual, un asiento recién solicitado puede verse libre hasta que Booking procese la solicitud. La consulta no garantiza la reserva: si otro usuario obtiene el asiento primero, Booking rechaza la solicitud por `AsientoOcupado`.

### POST `/reservations`

Recibe un cuerpo con `EventId` y `SeatId`. El usuario se obtiene del token validado.

1. Toma `correlationId` del header `X-Correlation-Id` o genera uno si el header no está presente.
2. Registra el inicio en el log de auditoría y verifica en la base local que el asiento pertenezca al evento. Si no existe esa combinación, registra el resultado y responde **404 Not Found** con `{ "error": "El asiento no existe para ese evento" }`.
3. Crea y guarda un `ReservationRequest` con un identificador único (`RequestId`), evento, asiento, usuario y fecha UTC.
4. Publica un `ReservationRequestedMessage` en Service Bus con `RequestId`, `EventId`, `SeatId`, `UserId`, `RequestedAtUtc` y `CorrelationId`. El adaptador lo serializa como JSON y asigna `MessageId = RequestId` y el `CorrelationId` del mensaje.
5. Cuando la publicación finaliza correctamente, registra el fin en el log de auditoría y responde **202 Accepted**, con la URL `/reservations/{requestId}` en `Location` y el cuerpo `{ requestId, correlationId }`.

Availability verifica la existencia del asiento, pero no consulta su ocupación ni lo retiene. Espera a que termine la publicación, sin esperar la decisión de Booking. **202 significa que la solicitud se registró y publicó; no que la reserva esté confirmada.**

Si la publicación lanza `ServiceBusException`, responde **503 Service Unavailable**. Como la solicitud se guarda antes de publicar, puede quedar registrada sin que Booking la reciba. No hay Outbox ni recuperación automática de esas solicitudes por parte de la aplicación; una solicitud que no llegue a Booking puede seguir mostrándose como `EnProceso`. Repetir el POST genera otro `RequestId`: no reutiliza la solicitud anterior. La idempotencia de Booking por `RequestId` cubre mensajes repetidos de la misma solicitud.

### GET `/reservations/{requestId:guid}`

1. Busca la solicitud en la base local y verifica que pertenezca al usuario autenticado. Si no existe o es ajena, responde **404 Not Found**, sin consultar Booking.
2. Consulta a Booking mediante `GET /reservations/{requestId}`.
3. Si Booking devuelve 404, lo interpreta como una solicitud todavía no procesada y responde **200 OK** con `{ requestId, status: "EnProceso", reason: null }`.
4. Si Booking conoce la solicitud, responde **200 OK** con `{ requestId, status, reason }`. Los estados pueden ser `Retenida`, `Confirmada`, `Rechazada` o `Vencida`. Los motivos de rechazo pueden ser `AsientoOcupado`, `PagoFallido` o `PagoNoDisponible`; `reason` puede ser nulo.

La respuesta usa `ReservationResultDto` y no expone los campos adicionales de Booking, como `ReservationId` y `ExpiresAtUtc`. El estado no se almacena localmente: cada consulta válida de una solicitud propia vuelve a consultar Booking. Si se propaga `HttpRequestException`, responde **503 Service Unavailable**.

# Diagrama API Availability

```mermaid
flowchart TB
    CLIENT["Cliente HTTP"] --> API

    subgraph AV["NODO AVAILABILITY"]
        direction TB

        subgraph API_LAYER["Availability.Api"]
            API["Endpoints HTTP<br/>Autenticación JWT<br/>Manejo de respuestas"]
            ROUTE{"Endpoint solicitado"}
            API --> ROUTE
        end

        subgraph APP["Availability.Application"]
            direction TB

            E1["GET /events<br/>ListEventsAsync"]
            E2["GET /events/eventId/seats<br/>GetSeatsAsync"]
            E3["POST /reservations<br/>RequestReservationAsync"]
            E4["GET /reservations/requestId<br/>GetResultAsync"]

            ROUTE --> E1
            ROUTE --> E2
            ROUTE --> E3
            ROUTE --> E4

            E1 --> LIST["Consultar eventos<br/>Ordenar por DateUtc"]
            LIST --> OK1["200 OK<br/>EventDto[]"]

            E2 --> EVENT{"¿Existe el evento?"}
            EVENT -->|No| NF1["404 Not Found"]
            EVENT -->|Sí| SEATS["Obtener asientos locales"]
            SEATS --> OCC["Consultar asientos ocupados"]
            OCC --> FILTER["Excluir ocupados<br/>Ordenar por Label"]
            FILTER --> OK2["200 OK<br/>SeatDto[]"]
            OCC -.->|Error HTTP| ERR2["503 Service Unavailable"]

            E3 --> AUTH3{"¿Token válido<br/>y usuario identificado?"}
            AUTH3 -->|No| U3["401 Unauthorized"]
            AUTH3 -->|Sí| CORR["Obtener o generar<br/>CorrelationId"]
            CORR --> CHECK{"¿Asiento pertenece<br/>al evento?"}
            CHECK -->|No| NF3["404 Not Found"]
            CHECK -->|Sí| SAVE["Crear y guardar<br/>ReservationRequest"]
            SAVE --> PUBLISH["Publicar<br/>ReservationRequestedMessage"]
            PUBLISH --> PUBOK{"¿Publicación exitosa?"}
            PUBOK -->|Sí| OK3["202 Accepted<br/>RequestId + CorrelationId<br/>Location de seguimiento"]
            PUBOK -->|No| ERR3["503 Service Unavailable<br/>Solicitud local conservada"]

            E4 --> AUTH4{"¿Token válido<br/>y usuario identificado?"}
            AUTH4 -->|No| U4["401 Unauthorized"]
            AUTH4 -->|Sí| OWNER{"¿Existe la solicitud<br/>y pertenece al usuario?"}
            OWNER -->|No| NF4["404 Not Found"]
            OWNER -->|Sí| RESULT["Consultar resultado"]
            RESULT --> STATUS{"Respuesta de Booking"}
            STATUS -->|404 o sin resultado| PROC["200 OK<br/>EnProceso"]
            STATUS -->|Resultado existente| OK4["200 OK<br/>RequestId, Status, Reason"]
            STATUS -->|Error HTTP| ERR4["503 Service Unavailable"]
        end

        subgraph DOMAIN["Availability.Domain"]
            MODELS["Event<br/>Seat<br/>ReservationRequest"]
        end

        subgraph INFRA["Availability.Infrastructure"]
            REPO["IAvailabilityRepository<br/>EF Core / Npgsql"]
            HTTP["IBookingClient<br/>HTTP + token de servicio"]
            BUS["IReservationPublisher<br/>Azure Service Bus"]
        end

        LIST -.-> REPO
        EVENT -.-> REPO
        SEATS -.-> REPO
        CHECK -.-> REPO
        SAVE -.-> REPO
        OWNER -.-> REPO

        OCC -.-> HTTP
        RESULT -.-> HTTP
        PUBLISH -.-> BUS

        REPO -.-> MODELS
    end

    PG[("PostgreSQL<br/>Base availability")]
    KC["Keycloak<br/>Tokens JWT"]
    BOOK["Booking API<br/>Consultas HTTP"]
    AZ["Azure Service Bus<br/>Topic grupo1-booking-topic"]

    REPO --> PG
    HTTP --> BOOK
    BUS --> AZ
    KC -.->|"Validación JWT"| API
    KC -.->|"client_credentials"| HTTP

    classDef endpoint fill:#dbeafe,stroke:#2563eb,color:#1e40af
    classDef action fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef success fill:#dcfce7,stroke:#16a34a,color:#166534
    classDef error fill:#fee2e2,stroke:#dc2626,color:#991b1b
    classDef external fill:#fef3c7,stroke:#d97706,color:#92400e

    class API,ROUTE,E1,E2,E3,E4 endpoint
    class LIST,SEATS,OCC,FILTER,CORR,CHECK,SAVE,PUBLISH,RESULT,STATUS,EVENT,OWNER,AUTH3,AUTH4,PUBOK action
    class OK1,OK2,OK3,OK4,PROC success
    class NF1,NF3,NF4,U3,U4,ERR2,ERR3,ERR4 error
    class PG,KC,BOOK,AZ external
```