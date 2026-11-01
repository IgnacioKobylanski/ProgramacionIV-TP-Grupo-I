# Arquitectura de Booking

Booking recibe la solicitud generada por el cliente en Availability. Es el encargado de retener ese asiento y de ordenar a Payment que realice el cobro. Si el cobro se completa, debe devolver el estado de la reserva a Availability y enviar la orden a Notifications.

## Componentes y dependencias

- **PostgreSQL:** base de datos donde Booking guarda las reservas. Las tablas se crean o actualizan solas cada vez que Booking arranca.
- **RabbitMQ:** Availability publica las solicitudes en el exchange `grupo1-booking` (tipo `fanout`), que las envía a la cola durable `booking`. Las réplicas de Booking comparten esa cola y cada mensaje se entrega a una de ellas.
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
| RabbitMQ | Host y puerto del broker (`RabbitMq:Host` y `RabbitMq:Port`) | `localhost:5672` |
| Credenciales de RabbitMQ | Usuario y contraseña (`RabbitMq:User` y `RabbitMq:Password`) | `app` / `app` (desarrollo local) |
| Payment | Dirección del servicio de cobro | `http://localhost:5003` |
| Notifications | Dirección del servicio de avisos | `http://localhost:5004/` |
| Keycloak | Dirección del servicio de identificación | `http://localhost:8081` |
| Tiempo de retención | Cuánto se guarda el asiento mientras se cobra | 120 segundos |
| Precio del asiento | Monto fijo que se cobra por cada asiento | 500000 centavos |

Para ejecutar Booking localmente, hay que configurar su clave secreta de Keycloak (`ServiceAuth:ClientSecret`). Las credenciales de desarrollo de RabbitMQ ya están en `appsettings.json`.

El consumidor declara automáticamente el exchange, la cola y su enlace, además del exchange `grupo1-booking.dlx` y la cola de mensajes fallidos `booking.dead`. Availability declara la misma topología al publicar, por lo que no hace falta crearla manualmente.

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
| GET | `/reservations?userId={userId}` | Solo Availability (con token) | Consulta las reservas de un usuario | 200, 401, 403 |

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

### GET `/reservations?userId={userId}`

Se consultan las reservas de un usuario en particular. Availability usa este endpoint para responder `GET /reservations/mine`: toma el usuario del token del cliente y se lo envía a Booking en el parámetro `userId`.

| Parámetro | Dónde va | Significado |
| --- | --- | --- |
| userId | Query string (obligatorio) | Identificador del usuario cuyas reservas se quieren consultar |

Responde **200 OK** con la lista de reservas del usuario, obtenida mediante `ReservationService.GetByUserAsync`.

Puntos importantes:

- **Confianza en Availability:** Booking no verifica a qué usuario pertenece el `userId` recibido. Esa responsabilidad es de Availability, que es el único servicio autorizado a llamar a este endpoint y que obtiene el usuario del token del cliente.
- **Sin `userId`:** al ser un parámetro obligatorio, si falta en la consulta la respuesta es un error de solicitud inválida (400), que no depende de la lógica de negocio.
- **Sin 404:** a diferencia de la consulta por `requestId`, si el usuario no tiene reservas no hay error: la respuesta es 200 con una lista vacía.

## Diagrama de Booking.Api

```mermaid
flowchart TD
    subgraph CONSULTAS["1. Responder consultas (solo Availability, con token)"]
        direction TB
        Q1["<b>GET /reservations/requestId</b><br/>Método: GetByRequestIdAsync<br/><br/><b>Datos que recibe:</b><br/>requestId: número de la solicitud"]
        Q1 --> Q1R{¿Existe la reserva?}
        Q1R -->|Sí| Q1OK["<b>200 OK</b><br/><b>Datos que devuelve:</b><br/>requestId, reservationId,<br/>status, reason, expiresAtUtc"]
        Q1R -->|No| Q1NF["<b>404 Not Found</b><br/>Availability la muestra como EnProceso"]

        Q2["<b>GET /events/eventId/occupied-seats</b><br/>Método: GetOccupiedSeatsAsync<br/><br/><b>Datos que recibe:</b><br/>eventId: número del evento"]
        Q2 --> Q2OK["<b>200 OK</b><br/><b>Datos que devuelve:</b><br/>lista de asientos ocupados"]

        Q3["<b>GET /reservations?userId=...</b><br/>Método: GetByUserAsync<br/><br/><b>Datos que recibe:</b><br/>userId: usuario a consultar"]
        Q3 --> Q3V{¿Se envió el userId?}
        Q3V -->|No| Q3BAD["<b>400 Pedido incorrecto</b>"]
        Q3V -->|Sí| Q3OK["<b>200 OK</b><br/><b>Datos que devuelve, por cada reserva:</b><br/>RequestId, EventId, SeatId,<br/>Status, Reason, CreatedAtUtc<br/>(de la más nueva a la más antigua)"]
    end

    subgraph PROCESO["2. Procesar una solicitud de reserva (desde RabbitMQ)"]
        direction TB
        M["<b>Llega una solicitud</b><br/>Cola: booking<br/><br/><b>Datos que recibe:</b><br/>RequestId, EventId, SeatId,<br/>UserId, CorrelationId"]
        M --> M1{¿Se puede leer<br/>el mensaje?}
        M1 -->|No| DEAD["Se aparta en la cola<br/>de mensajes fallidos (booking.dead)"]
        M1 -->|Sí| M2{¿Ya se había<br/>procesado?}
        M2 -->|Sí| IGN["Se ignora para no duplicar"]
        M2 -->|No| M3{¿El asiento está libre?}
        M3 -->|No| REJ1["Reserva <b>Rechazada</b><br/>Motivo: AsientoOcupado"]
        M3 -->|Sí| RET["Reserva <b>Retenida</b><br/>El asiento se guarda 120 segundos"]
        RET --> PAY["Orden de cobro a Payment (gRPC)<br/>Método: ChargeReservation<br/>Espera máxima: 5 segundos"]
        PAY --> M4{¿Cobro aprobado?}
        M4 -->|No, lo rechaza| REJ2["Reserva <b>Rechazada</b><br/>Motivo: PagoFallido"]
        M4 -->|No responde| REJ3["Reserva <b>Rechazada</b><br/>Motivo: PagoNoDisponible"]
        M4 -->|Sí| CONF["Reserva <b>Confirmada</b>"]
        CONF --> NOT["Aviso a Notifications (HTTP)<br/>Si falla, la reserva sigue confirmada"]
        FAIL["Si algo falla al procesar:<br/>el mensaje vuelve a la cola y se reintenta"]
    end

    subgraph VENCIMIENTO["3. Vencer reservas (tarea en segundo plano)"]
        direction TB
        V1["Cada 10 segundos<br/>Booking revisa las reservas Retenidas"]
        V1 --> V2{¿Pasaron los<br/>120 segundos?}
        V2 -->|Sí| V3["Reserva <b>Vencida</b><br/>El asiento queda libre"]
        V2 -->|No| V4["No se hace nada"]
    end

    DB[("PostgreSQL<br/>reservas")]
    K["Keycloak<br/>token de Availability"]

    K -.->|Valida el token| CONSULTAS
    CONSULTAS <--> DB
    PROCESO --> DB
    VENCIMIENTO --> DB
```

Puntos importantes:

- **Sin duplicados:** si la misma solicitud llega dos veces, la segunda se ignora.
- **Confirmación y reintentos:** Booking confirma el mensaje a RabbitMQ después de procesarlo. Si el procesamiento falla, lo devuelve a la cola para reintentar.
- **Tiempo de retención:** el asiento se guarda 120 segundos mientras se cobra. Cada 10 segundos Booking revisa si hay reservas vencidas y las libera.
- **Si falla Notifications:** la reserva igual queda confirmada. El error solo se anota en el registro del sistema y no se reintenta el aviso.
- **Mensajes ilegibles:** si llega un mensaje que no se puede leer, se rechaza sin volver a encolarlo. RabbitMQ lo envía a la cola de mensajes fallidos `booking.dead` mediante el exchange `grupo1-booking.dlx`.
- **Pendiente conocido:** si la reserva vence mientras Payment está cobrando, el dinero no se devuelve de forma automática. Queda como mejora futura.
