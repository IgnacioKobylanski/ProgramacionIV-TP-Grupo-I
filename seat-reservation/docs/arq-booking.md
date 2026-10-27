# Arquitectura de Booking

Booking recibe la solicitud generada por el cliente en Availability. Es el encargado de retener ese asiento y de ordenar a Payment que realice el cobro. Si el cobro se completa, debe devolver el estado de la reserva a Availability y enviar la orden a Notifications.

## Componentes y dependencias

- **PostgreSQL:** base de datos donde Booking guarda las reservas. Las tablas se crean o actualizan solas cada vez que Booking arranca.
- **Azure Service Bus:** servicio de mensajes. Availability deja allí las solicitudes de reserva y Booking las va leyendo. Si Booking tiene varias copias funcionando, cada solicitud la toma solo una de ellas.
- **Keycloak:** servicio que identifica a cada sistema. Booking pide su token a Keycloak y también lo usa para comprobar quién le consulta.
- **Payment:** servicio que realiza el cobro de la reserva. Booking se comunica con él mediante gRPC.
- **Notifications:** servicio que avisa al usuario cuando su reserva queda confirmada. Booking se comunica con él por HTTP.

## Guía de inicio

Una vez que *Docker Desktop* esté levantado, abrimos una terminal parados sobre la raíz del proyecto y escribimos:

```powershell
dotnet run --project src/Booking/Booking.Api --urls http://localhost:5002/
```

### Configuración necesaria

Estos datos se encuentran en el archivo `appsettings.json` de Booking.Api:

| Dato | Para qué sirve | Valor de ejemplo |
| --- | --- | --- |
| Base de datos | Dónde se guardan las reservas | `localhost:5432` |
| Payment | Dirección del servicio de cobro | `http://localhost:5003` |
| Notifications | Dirección del servicio de avisos | `http://localhost:5004/` |
| Keycloak | Dirección del servicio de identificación | `http://localhost:8081` |
| Tiempo de retención | Cuánto se guarda el asiento mientras se cobra | 120 segundos |
| Precio del asiento | Monto fijo que se cobra por cada asiento | 500000 centavos |

Hay dos datos que **no vienen escritos en el archivo** y hay que cargarlos antes de arrancar: la clave de acceso a Azure Service Bus y la clave secreta de Booking en Keycloak.

## Autorización y Autenticación

Booking cumple dos roles:

- **Cuando llama a otros servicios:** se identifica ante *Keycloak* con el nombre `booking-service` y envía su token a Payment y a Notifications.
- **Cuando recibe consultas:** solamente acepta las que vienen de Availability. Cada consulta debe llevar el token de `availability-service`.

```mermaid
sequenceDiagram
    participant A as Availability
    participant K as Keycloak
    participant B as Booking
    A->>K: Pide su token
    K-->>A: Entrega el token
    A->>B: Consulta con el token
    alt Token válido de Availability
        B-->>A: 200 con la respuesta
    else Sin token o token inválido
        B-->>A: 401
    else Token de otro servicio
        B-->>A: 403
    end
```

## Resumen de endpoints

| Método | Ruta | Acceso | Función | Respuestas principales |
| --- | --- | --- | --- | --- |
| GET | `/reservations/{requestId:guid}` | Solo Availability (con token) | Consulta el estado de una reserva | 200, 404, 401, 403 |
| GET | `/events/{eventId:guid}/occupied-seats` | Solo Availability (con token) | Consulta los asientos ocupados | 200, 401, 403 |

## Flujo de cada endpoint

### GET `/reservations/{requestId:guid}`

Con el requestId se consulta el estado de la reserva. En caso de que Booking todavía no haya procesado la solicitud, responde 404 y Availability se lo muestra al cliente como "En proceso".

Responde **200 OK** con los datos de la reserva, o **404 NOT FOUND** si todavía no existe.

Datos que devuelve:

| Dato | Significado |
| --- | --- |
| requestId | Número de la solicitud que hizo el cliente |
| reservationId | Número de la reserva creada por Booking |
| status | Estado de la reserva (por ejemplo: Retenida, Confirmada o Rechazada) |
| reason | Motivo, solo si fue rechazada |
| expiresAtUtc | Fecha y hora en que vence la retención del asiento |

Motivos posibles de rechazo:

- **AsientoOcupado:** otra persona ya tenía ese asiento.
- **PagoFallido:** Payment rechazó el cobro.
- **PagoNoDisponible:** Payment no pudo responder.

### GET `/events/{eventId:guid}/occupied-seats`

Se consulta un evento en específico con el eventId. Solamente devuelve los asientos ocupados, que se envían a Availability para que no los muestre al cliente o al frontend.

Responde **200 OK** con una lista de asientos.

## Cómo se procesa una solicitud de reserva

Además de los dos endpoints, Booking trabaja en segundo plano: lee las solicitudes que Availability deja en Azure Service Bus y las procesa una por una.

```mermaid
flowchart TD
    S[Llega una solicitud] --> D{¿Ya se había procesado?}
    D -->|Sí| I[Se ignora para no duplicar]
    D -->|No| R[Se intenta retener el asiento]
    R --> O{¿Asiento libre?}
    O -->|No| X1[Reserva Rechazada: AsientoOcupado]
    O -->|Sí| P[Se ordena el cobro a Payment]
    P --> Q{¿Cobro aprobado?}
    Q -->|No| X2[Reserva Rechazada: PagoFallido o PagoNoDisponible]
    Q -->|Sí| C[Reserva Confirmada]
    C --> N[Se avisa a Notifications]
```

Puntos importantes:

- **Sin duplicados:** si la misma solicitud llega dos veces, la segunda se ignora.
- **Tiempo de retención:** el asiento se guarda 120 segundos mientras se cobra. Cada 10 segundos Booking revisa si hay reservas vencidas y las libera.
- **Si falla Notifications:** la reserva igual queda confirmada. El error solo se anota en el registro del sistema y no se reintenta el aviso.
- **Mensajes ilegibles:** si llega un mensaje que no se puede leer, se aparta en una cola de mensajes fallidos para revisarlo después.
- **Pendiente conocido:** si la reserva vence mientras Payment está cobrando, el dinero no se devuelve de forma automática. Queda como mejora futura.
