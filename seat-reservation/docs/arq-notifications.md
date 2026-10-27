# Arquitectura de Notifications

## Descripción general

Notifications es un microservicio implementado como una API REST mínima en .NET 10. Su responsabilidad es registrar y simular el envío de notificaciones cuando Booking confirma una reserva.

Booking se comunica directamente con Notifications mediante HTTP, sin utilizar Azure Service Bus para este tramo del proceso.

## Diagrama de arquitectura


```mermaid
flowchart TD
    K["Keycloak: servidor de autenticación"]
    A["Booking: reserva confirmada"]
    B["Notifications API"]
    C{"¿Solicitud autenticada y autorizada?"}
    D[("Base de datos PostgreSQL")]
    E{"¿Ya existe una notificación para esta reserva?"}
    F["Guarda notificación en PostgreSQL"]
    G["Registra aviso simulado en el log"]
    H["HTTP 200 OK"]
    I["HTTP 401 o 403"]
    J["Cliente de consulta"]

    A -->|"Obtiene token de servicio"| K
    K -->|"Token de acceso"| A
    A -->|"HTTP POST /notifications con token"| B
    B --> C
    C -->|"No"| I
    C -->|"Sí"| D
    D -->|"Consulta por ReservationId"| E
    E -->|"Sí"| H
    E -->|"No"| F
    F --> G
   G --> H


J -->|"GET /notifications con token válido"| B
B -->|"Devuelve las últimas 50 notificaciones"| J
   ```




## Funcionamiento

1. Booking confirma una reserva después de que Payment informa que el cobro fue exitoso.
2. Booking obtiene un token de servicio de Keycloak utilizando el mecanismo de autenticación entre microservicios (*client credentials*).
3. Booking realiza una solicitud HTTP `POST /notifications`, incluyendo el token en el encabezado `Authorization: Bearer <token>`.
4. Notifications valida la firma, el emisor y el vencimiento del token. Además, comprueba que la solicitud provenga del servicio autorizado `booking-service`.
5. Si falta un token válido, la solicitud se rechaza con HTTP 401. Si el token es válido pero pertenece a un servicio no autorizado, se rechaza con HTTP 403.
6. Si la solicitud está autorizada, Notifications comprueba si ya existe una notificación asociada al `ReservationId`.
7. Si no existe, registra la notificación en su base de datos PostgreSQL y escribe el aviso simulado en el log.
8. Si ya existe, no vuelve a registrar la misma notificación y responde HTTP 200.
9. El endpoint `GET /notifications` permite consultar las últimas 50 notificaciones registradas, ordenadas por fecha descendente.

## Modelo de datos

La entidad `Notification` contiene los siguientes campos:

| Campo | Tipo | Descripción |
|---|---|---|
| Id | Guid | Identificador de la notificación |
| ReservationId | Guid | Identificador de la reserva |
| UserId | string | Usuario destinatario |
| Message | string | Mensaje de confirmación |
| SentAtUtc | DateTime | Fecha y hora UTC del registro |

Se utiliza Entity Framework Core para la persistencia. La base de datos establece un índice único sobre `ReservationId` para evitar duplicados y limita el campo `Message` a 500 caracteres.

## Decisión arquitectónica

Se utiliza comunicación HTTP directa entre Booking y Notifications porque el servicio de notificaciones no forma parte del flujo del broker especificado en el diagrama oficial.

Esta decisión simplifica la implementación y las pruebas, evitando incorporar otra cola de mensajes.

Azure Service Bus continúa utilizándose en el flujo de solicitudes de reserva entre Availability y Booking.

## Manejo de fallos y limitaciones

Según el comportamiento informado para el flujo completo, una falla de Notifications no impide que Booking confirme la reserva.

Sin embargo, la comunicación directa presenta una limitación: si Notifications está fuera de servicio cuando Booking intenta enviar el aviso, la notificación puede perderse.

Como mejora futura, podría utilizarse mensajería asíncrona para desacoplar ambos servicios y permitir reintentos.

## Auditoría y seguridad


Notifications registra en los logs el inicio y la finalización del procesamiento mediante `CorrelationId` y `ReservationId`.

La autenticación entre microservicios se realiza mediante Keycloak, utilizando tokens de acceso.

El endpoint `POST /notifications` solo permite solicitudes autenticadas provenientes del servicio `booking-service`. Si se presenta un token válido correspondiente a otro servicio no autorizado, el acceso se rechaza con HTTP 403.

El endpoint `GET /notifications` requiere autenticación mediante un token válido, pero no está restringido exclusivamente al servicio Booking. Se utiliza para consultar las últimas 50 notificaciones registradas.


## Endpoints

| Método | Ruta | Función | Autorización |
|---|---|---|---|
| POST | `/notifications` | Registra una notificación de reserva confirmada | Token válido de `booking-service` |
| GET | `/notifications` | Consulta las últimas 50 notificaciones | Cualquier token válido |

El servicio fue ejecutado y probado localmente en el puerto `5004`, mediante el siguiente comando:

```powershell
dotnet run --project src/Notifications/Notifications.csproj --urls http://localhost:5004
```



## Pruebas realizadas

Se realizaron pruebas locales del microservicio Notifications con PostgreSQL.

| Prueba | Resultado |
|---|---|
| Inicio de la API en el puerto 5004 | Correcto |
| Conexión con PostgreSQL | Correcto |
| Aplicación de migraciones de Entity Framework Core | Correcto |
| GET /notifications sin registros | Devuelve `[]` |
| POST /notifications con datos de prueba | Registra la notificación |
| GET /notifications después del POST | Devuelve el registro creado |
| POST repetido con el mismo ReservationId | No genera un segundo registro |

La prueba de idempotencia confirmó que repetir una solicitud con el mismo `ReservationId` mantiene una única notificación almacenada para esa reserva.

Estas pruebas verifican el funcionamiento individual de Notifications. La integración completa con Booking y el flujo de reserva quedan pendientes de validación local.
