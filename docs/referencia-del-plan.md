# Referencia del plan (fuente de verdad)

Todo lo que se documente o diagrame debe coincidir con este archivo.
Si algo del código necesita diferir, se actualiza acá primero.

## Servicios y puertos
| Servicio | Estilo | Puerto |
|---|---|---|
| Availability | Clean Architecture, dominio anémico | 5001 |
| Booking (REST) | N-Layer, dominio anémico | 5002 |
| Payment (gRPC) | N-Layer, dominio anémico | 5003 |
| Notifications | Worker que consume del broker | 5004 |
| Keycloak | Servidor de autorización | 8081 |
| PostgreSQL | Una base por servicio | 5432 |

Broker: Azure Service Bus, con dos colas:
`reservation-requests` (Availability a Booking) y `reservation-confirmed` (Booking a Notifications).

## Flujo de una reserva
```mermaid
sequenceDiagram
    actor U as Usuario
    participant A as Availability
    participant K as Keycloak
    participant S as Service Bus
    participant B as Booking
    participant P as Payment
    participant N as Notifications
    U->>A: Consultar asientos (sin login)
    U->>K: Obtener token
    U->>A: Solicitar reserva (con token)
    A->>A: Verificar asiento y registrar solicitud
    A->>S: Publicar solicitud
    A-->>U: Solicitud recibida (requestId)
    Note over A,B: Zona de consistencia eventual
    S->>B: Entregar mensaje
    B->>B: Retener asiento o rechazar si esta ocupado
    B->>P: Cobrar (gRPC)
    P-->>B: Resultado del pago
    B->>B: Confirmar o rechazar
    B->>S: Publicar reserva confirmada
    S->>N: Entregar mensaje
    N-->>U: Notificar (simulado)
    U->>A: Consultar resultado
    A->>B: GET estado
```

## Estados de una reserva
```mermaid
stateDiagram-v2
    [*] --> Retenida: asiento libre
    [*] --> Rechazada: asiento ocupado
    Retenida --> Confirmada: pago exitoso
    Retenida --> Rechazada: pago fallido o no disponible
    Retenida --> Vencida: se agota el tiempo de retencion
```
Un asiento está ocupado mientras su reserva esté Retenida o Confirmada.

## Entidades por servicio (dominio anémico: solo datos)
```mermaid
classDiagram
    class Event {
        Guid Id
        string Name
        DateTime DateUtc
    }
    class Seat {
        Guid Id
        Guid EventId
        string Label
    }
    class ReservationRequest {
        Guid Id
        Guid EventId
        Guid SeatId
        string UserId
        DateTime CreatedAtUtc
    }
    class Reservation {
        Guid Id
        Guid RequestId
        Guid EventId
        Guid SeatId
        string UserId
        ReservationStatus Status
        RejectionReason Reason
        DateTime CreatedAtUtc
        DateTime ExpiresAtUtc
    }
    class PaymentRecord {
        Guid Id
        Guid ReservationId
        decimal Amount
        PaymentStatus Status
        DateTime CreatedAtUtc
    }
    class Notification {
        Guid Id
        Guid ReservationId
        string UserId
        string Message
        DateTime SentAtUtc
    }
    Event "1" --> "*" Seat
    Event "1" --> "*" ReservationRequest
```
- Availability: Event, Seat, ReservationRequest
- Booking: Reservation (estados: Retenida, Confirmada, Rechazada, Vencida; motivos: AsientoOcupado, PagoFallido, PagoNoDisponible)
- Payment: PaymentRecord (estados: Aprobado, Rechazado)
- Notifications: Notification

No hay relaciones entre entidades de servicios distintos: se vinculan solo por id (cada servicio tiene su propia base).

## Reglas de trabajo
1. Hacer `git pull` antes de empezar a trabajar.
2. Cada integrante trabaja en su área; los cambios a otra área se acuerdan antes.
3. Commits en español, con el formato `tipo: resumen`.
4. Cada integrante guarda sus prompts en `docs/prompts/nombre-apellido.md`.
5. Si una duda cambia el plan, se consulta antes de documentar algo distinto.